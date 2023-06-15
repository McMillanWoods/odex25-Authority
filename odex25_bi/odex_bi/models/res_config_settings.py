# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bi_url = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            bi_url=params.get_param('superset.bi_url', default=False),
            username=params.get_param('superset.username', default=False),
            password=params.get_param('superset.password', default=False)
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("superset.bi_url", self.bi_url)
        self.env['ir.config_parameter'].sudo().set_param("superset.username", self.username)
        self.env['ir.config_parameter'].sudo().set_param("superset.password", self.password)