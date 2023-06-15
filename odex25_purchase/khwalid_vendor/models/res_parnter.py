from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class Partner(models.Model):
    _inherit = 'res.partner'

    parnter_referencen = fields.Char('Partner Reference', required=True, index=True, copy=False, default='New')
    @api.model
    def create(self, vals):
        vals['parnter_referencen'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return super(Partner, self).create(vals)
        
    cancel_reason = fields.Text(
        string='Cancel Reason',
    )

    name = fields.Char(index=True,tracking=True)

    vat = fields.Char(string='Tax ID', index=True, help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.",tracking=True)
    
    email = fields.Char(tracking=True)
   
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)

    state = fields.Selection(
       string='Status', required=True, readonly=True, copy=False,tracking=True,
        selection=[
            ('new', 'New'), 
            ('approved', 'Approved'), 
            ('refused', 'Refused')],
            default='new',
            
    )

    def action_purchase_vendor_approve(self):
        self.state = 'approved'

    def action_purchase_vendor_refuse(self):
        self.state = 'refused'    

    # def action_project_manager(self):
    #     self.state = 'project_manager'

    # def action_financial_manager(self):
    #     self.state = 'financial_manager'

    # def action_ceo(self):
    #     self.state = 'ceo'

    # def action_general_manager(self):
    #     self.state = 'general_manager'

    # def action_cancel(self):
    #     return {
    #             'name': 'Cancel',
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'partner.cancel.wizard',
    #             'view_mode': 'form',
    #             'view_type': 'form',
    #             'target': 'new'

    #         }
       
    # def action_rest_to_draft(self):
    #     self.state = 'draft'
    

    # 