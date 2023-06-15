# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProposalCommonReportWiz(models.TransientModel):
    _name = 'proposal.common.report.wiz'
    _description = "Proposal Common Report Wizard"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    business_unit_ids = fields.Many2many('hr.department', string='Business Unit')
    classification_ids = fields.Many2many('res.partner.industry', string='Classification')
    sector_id = fields.Many2one('sector', 'Sector')
    proposal_state_id = fields.Many2one('proposal.state', string="Proposal Status")
    proposal_state_ids = fields.Many2many('proposal.state', string="Proposal Status")



    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("Date to must be greater than date from"))


    def prepare_print_data(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['form'] = self.read(['company_id', 'date_from', 'date_to', 'business_unit_ids', 
                                    'proposal_state_id', 'classification_ids', 'sector_id', 'proposal_state_ids'])[0]
        return data

    def print_pdf(self):
        self.ensure_one()
        data = self.prepare_print_data()
        return self.print_report_pdf(data)

    def print_xlsx(self):
        self.ensure_one()
        data = self.prepare_print_data()
        return self.print_report_xlsx(data)

    def print_report_pdf(self, data):
        
        return True

    def print_report_xlsx(self, data):

        return True

