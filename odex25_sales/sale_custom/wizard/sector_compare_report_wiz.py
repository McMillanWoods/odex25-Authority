# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################

from odoo import models, fields, api

class SectorCcompareReportWiz(models.TransientModel):
    _inherit = "proposal.common.report.wiz"
    _name = 'sector.compare.report.wiz'
    _description = "Sector Compare Report Wizard"

    sector_compare_id = fields.Many2one('sector', 'Sector Compare')

    def print_report_pdf(self, data):
        
        return self.env.ref('sale_custom.action_classification_report_pdf').with_context(landscape=True).report_action(self, data=data)

    def print_report_xlsx(self, data):

        return self.env.ref('sale_custom.').report_action(self, data=data)

