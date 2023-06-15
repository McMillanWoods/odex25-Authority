from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class SaleOrder(models.Model):
    _inherit = "sale.order"

    type = fields.Selection(
        selection=[
            ('ordinary', 'Ordinary'),
            ('contract', 'Contract'),
        ],
        
    )
    contract_id = fields.Many2one(
        comodel_name='contract.contract'
    )
    ref_order = fields.Char(string='Ref.')
    ref_date = fields.Date(string='Ref Date')
    contract_template_id = fields.Many2one('contract.template' , 'Contract Template')
    contract_name = fields.Char('Contract Name')


    @api.onchange('contract_template_id')
    def template_onchange(self):
        lines = []
        for rec in self:
            if rec.contract_template_id:
                rec.contract_name = rec.contract_template_id.name
                for line in rec.order_line:
                    lines.append((2,line.id))
                for line in rec.contract_template_id.contract_line_ids:
                    lines.append((0,0,{
                        'product_id' : line.product_id.id,
                        'name' : line.product_id.name + '\n' + str(line.product_id.description_sale or ''),
                        'product_qty' : line.quantity,
                        'product_uom' : line.uom_id,
                        'price_unit' : line.price_unit,
                    }))
                rec.order_line = lines

                


    
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        if self.type == 'contract':
            lines = []
            for l in self.order_line:
                lines.append((0, 0, {
                    'name': l.name,
                    'product_id': l.product_id.id,
                    'quantity': l.product_uom_qty,
                    'uom_id': l.product_uom.id,
                    'price_unit': l.price_unit,
                    'discount': l.discount,
                }))

            company_id = self.env.context.get(
            'company_id', self.env.user.company_id.id
            )
            domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', company_id),
            ]
            journal =  self.env['account.journal'].search(domain, limit=1)
            self.contract_id = self.env['contract.contract'].create({
                'name': self.contract_name,
                'state' : 'to_confirm',
                'date' :self.confirmation_date,
                'partner_id': self.partner_id.id,
                'pricelist_id': self.pricelist_id.id,
                'company_id': self.company_id.id,
                'payment_term_id': self.payment_term_id.id,
                'fiscal_position_id': self.fiscal_position_id.id,
                'contract_type': 'sale',
                'contract_template_id' : self.contract_template_id and self.contract_template_id.id,
                'code' : _('Contract for sale order #%s') % self.name,
                'contract_line_ids': lines,
                'journal_id':journal.id,
            })

    
    def action_cancel(self):
        if self.contract_id and self.contract_id.state != 'new':
            raise ValidationError(_('You cannot Cancel This Sale order because it has Non draft Contract'))
        return super(SaleOrder, self).action_cancel()
