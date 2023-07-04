from odoo import api, fields, models




class ResSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    days_before_end = fields.Integer(string='Before Subscription End')

    def get_values(self):
        res = super(ResSetting, self).get_values()

        res['days_before_end'] = int(self.env['ir.config_parameter'].sudo().get_param('odex_subscription_service.days_before_end', default=7))

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('odex_subscription_service.days_before_end', self.days_before_end)

        super(ResSetting, self).set_values()