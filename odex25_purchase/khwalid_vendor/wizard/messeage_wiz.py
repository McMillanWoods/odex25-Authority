
from odoo import api, fields, models,_ 
from odoo.exceptions import UserError, ValidationError

class InfoWizard(models.TransientModel):

    _name = 'partner.cancel.wizard'

    _description = 'Reason Wizard'

    cancel_reason = fields.Text(string="Reason")

    
    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
    )

    @api.model
    def default_get(self, fields):
        res = super(InfoWizard, self).default_get(fields)
        partner_id = self.env.context['active_id']
        res['partner_id'] = partner_id
        return res
    
    def cancel_partner(self):
        if self.partner_id:
            self.partner_id.write({'state':'cancel','cancel_reason':self.cancel_reason})
            
            