from odoo import api, fields, models

class ResSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    days_before_finish = fields.Integer(string='Before Subscription Finish')
    tickets_no = fields.Integer(string='Default Tickets Number')

    def get_values(self):
        res = super(ResSetting, self).get_values()

        res['days_before_finish'] = int(self.env['ir.config_parameter'].sudo().get_param('odex25_helpdesk.days_before_finish', default=30))
        res['tickets_no'] = int(self.env['ir.config_parameter'].sudo().get_param('odex25_helpdesk.tickets_no', default=5))

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('odex25_helpdesk.days_before_finish', self.days_before_finish)
        self.env['ir.config_parameter'].sudo().set_param('odex25_helpdesk.tickets_no', self.tickets_no)
        super(ResSetting, self).set_values()