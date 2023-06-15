# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = "odex25_helpdesk.team"

    elearning_id = fields.Many2one('slide.channel', 'eLearning')
    elearning_url = fields.Char('Presentations URL', readonly=True, related='elearning_id.website_url')

    @api.onchange('use_website_helpdesk_slides')
    def _onchange_use_website_helpdesk_slides(self):
        if not self.use_website_helpdesk_slides:
            self.elearning_id = False
