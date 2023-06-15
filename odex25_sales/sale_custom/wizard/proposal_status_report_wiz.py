# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################

from odoo import models, fields, api

class ProposalStatusReportWiz(models.TransientModel):
    _inherit = "proposal.common.report.wiz"
    _name = 'proposal.status.report.wiz'
    _description = "Proposal Status Report Wizard"


    def print_report_pdf(self, data):
        
        return self.env.ref('sale_custom.action_proposal_status_report_pdf').with_context(landscape=True).with_context(landscape=True).report_action(self, data=data)

    def print_report_xlsx(self, data):

        return self.env.ref('sale_custom.action_proposal_status_report_xlsx').report_action(self, data=data)

