# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _

class ProposalInprogressReport(models.AbstractModel):
    _name = 'report.sale_custom.proposal_inporgress_report'

    def get_proposal_inporgress_data(self, data=None, context={}):
        datas = []
        crm_lead_obj = self.env['crm.lead']
        domain = [('date_open', '>=', data['form']['date_from']), ('date_open', '<=', data['form']['date_to']), 
                    ('active', '=', True), ('type', '=', 'opportunity')]

        crm_ids = crm_lead_obj.search(domain)
        for proposal in crm_ids.mapped('order_ids'):
            datas.append({
                'date': proposal.opportunity_id.date_open.strftime('%Y-%m-%d'),
                'bidbond': proposal.opportunity_id.bidbond,
                'crm_seq': proposal.opportunity_id.code_rfp,
                'proposal': proposal.name ,
                'name': proposal.opportunity_id.name,
                'business_unit': proposal.department_id.name
            })

        return datas



    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        return {
            'doc_model': model,
            'data': data,
            'docs': docs,
            'proposal_inporgress': self.get_proposal_inporgress_data(data),
        }
