##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"


    code_rfp = fields.Char(
        string="Number", required=True, default="/", readonly=True, copy=False, tracking=True
    )

    code_rfi = fields.Char(
        string="Number", required=True, default="/", readonly=True, copy=False, tracking=True
    )

    _sql_constraints = [
        ("crm_lead_unique_code_rfp", "UNIQUE (code_rfp)", _("The code must be unique!")),
        ("crm_lead_unique_code_rfi", "UNIQUE (code_rfi)", _("The code must be unique!")),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code_rfi", "/") == "/" and vals.get('type') == 'lead':
                vals['code_rfi'] = self.env['ir.sequence'].next_by_code('crm.lead.rfi') or _('/')

            if vals.get("code_rfp", "/") == "/" and vals.get('type') == 'opportunity':
                vals['code_rfp'] = self.env['ir.sequence'].next_by_code('crm.lead.rfp') or _('/')

        return super().create(vals_list)


    def convert_rfp(self):
       super(CrmLead, self).convert_rfp()
       self.code_rfp = self.env['ir.sequence'].next_by_code('crm.lead.rfp') or _('/')



    def name_get(self):
        result = []
        for crm in self:
            if self._context.get('default_type') == 'lead':
                result.append((crm.id, crm.code_rfi))

            if self._context.get('default_type') == 'opportunity':
                result.append((crm.id, crm.code_rfp))

            else:
                result.append((crm.id, crm.code_rfp))

        return result
