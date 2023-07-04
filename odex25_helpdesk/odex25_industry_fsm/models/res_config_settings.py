# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_odex25_industry_fsm_report = fields.Boolean("Worksheets")
    module_odex25_industry_fsm_sale = fields.Boolean('Time and Material')

    def _get_subtasks_projects_domain(self):
        return [('is_fsm', '=', False)]
