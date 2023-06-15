from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class PurchaseOrderCustom(models.Model):
    _inherit = "purchase.order"

    type = fields.Selection(
        selection=[
            ('ordinary', 'Ordinary'),
            ('contract', 'Contract'),
        ],
        default='ordinary'
    )

    contract_id = fields.Many2one(
        comodel_name='contract.contract'
    )
    contract_template_id = fields.Many2one('contract.template' , 'Contract Template')
    contract_name = fields.Char('Contract Name')

    @api.constrains('date_planned')
    def contract_date_planned(self):
        if self.type == "contract" and not self.date_planned:
            raise ValidationError(_("Please Set Receipt Date"))

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
                        'product_qty' : line.quantity or 1,
                        'product_uom' : line.uom_id,
                        'price_unit' : line.price_unit,
                    }))
                rec.order_line = lines
                rec.date_planned = fields.datetime.now()

    def button_confirm(self):
        purchase_budget = self.env.company.purchase_budget
        for rec in self:
            if not rec.id:
                raise ValidationError(_("Please save this quotation"))

            if rec.send_to_budget and purchase_budget:
                raise ValidationError(_("Please sign this quotation"))
            # super(PurchaseOrderCustom,self).button_confirm()
            if rec.type == 'contract':
                # Changed to purchase order
                rec.state = 'purchase'
                print("state is: ", rec.state)
                # Create purchase contract from purchase module
                lines = []
                for l in rec.order_line:
                    lines.append((0, 0, {
                        'name': l.name,
                        'product_id': l.product_id.id,
                        'quantity': l.product_qty,
                        'uom_id': l.product_uom.id,
                        'price_unit': l.price_unit,
                        'department': l.department_name.id,
                        'date_end':l.date_end,
                        'analytic_account_id':l.account_analytic_id.id,
                        'tax_id':[(6,0, l.taxes_id.ids)]
                    }))
                company_id = rec.env.context.get('company_id', rec.env.user.company_id.id)
                domain = [ ('type', '=', 'purchase'), ('company_id', '=', company_id)]
                journal =  rec.env['account.journal'].search(domain, limit=1)
                rec.contract_id = rec.env['contract.contract'].create({
                    'name': rec.contract_name,
                    'state' : 'new',
                    'date' :rec.date_order,
                    'partner_id': rec.partner_id.id,
                    'company_id': rec.company_id.id,
                    'payment_term_id': rec.payment_term_id.id,
                    'fiscal_position_id': rec.fiscal_position_id.id,
                    'contract_type': 'purchase',
                    'contract_template_id' : rec.contract_template_id and rec.contract_template_id.id,
                    'code' : _('Contract for Purchase order #%s') % rec.name,
                    'contract_line_ids': lines,
                    'journal_id':journal.id
                })

            else:
                print("No contract")
                super(PurchaseOrderCustom, rec).button_confirm()
    
    def action_cancel(self):
        if self.contract_id and self.contract_id.state != 'new':
            raise ValidationError(_('You cannot Cancel This Sale order because it has Non draft Contract'))
        return super(PurchaseOrderCustom, self).action_cancel()
