from odoo import api, fields, models ,_
from odoo.exceptions import ValidationError

class online_tendering(models.Model):
    _inherit = "res.partner"

    company_type = fields.Selection(
        selection_add=[('establish', _('Establish'))])
    company_represent = fields.Char('Company Representative')
    activity_type = fields.Many2one('activity.type' , 'Activity Type')
   

class PortalResUser(models.Model):
    _inherit = 'res.users'

    address = fields.Char('Address')
    activity_type = fields.Many2one('activity.type' , 'Activity Type')
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    # tax_no = fields.Char('Tax No.')
    # commercial_no = fields.Char('Commercial No.')
    # supplier_type = fields.Selection([('company','Company'),('individual','Individual')],string="Supplier Type")
  # supplier_doc = fields.Binary(string='Supplier Doc.')
 
