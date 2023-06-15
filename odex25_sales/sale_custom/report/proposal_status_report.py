# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _
import itertools
import operator


class ProposalStatusReport(models.AbstractModel):
    _name = 'report.sale_custom.proposal_status_report'

    def get_custom_data(self, data=None, context={}):
        datas = []
        sale_obj = self.env['sale.order']
        res = {}
        keys = []

        domain = [('date_order', '>=', data['form']['date_from']), ('date_order', '<=', data['form']['date_to']), 
                 ('department_id', 'in', data['form']['business_unit_ids']), ('proposal_state_id', '=', data['form']['proposal_state_id'][0])]

        sale_ids = sale_obj.search(domain)
        for sale in sale_ids:
            datas.append({
                'date': sale.date_order.strftime('%Y-%m-%d'),
                'crm_seq': sale.opportunity_id.code_rfp,
                'proposal': sale.name ,
                'name': sale.opportunity_id.name,
                'project_duration': sale.project_duration ,
                'p_fees': sale.amount_total,
                'contract_status': sale.contract_status,
                'business_unit': sale.department_id,
                'rank': sale.rank,
                'contract_value': sale.contract_value,
            })
        
        for key,val in itertools.groupby(datas, key=operator.itemgetter("business_unit")):

            res[key.id] = list(val) if key.id not in res.keys() else res[key.id] + list(val)
            keys.append(key)
        
        return set(keys), res



    @api.model
    def _get_report_values(self, docids, data=None):

        keys, lines = self.get_custom_data(data)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))


        return {
            'doc_model': model,
            'data': data,
            'docs': docs,
            'proposal_status_data': lines,
            'keys': keys,
        }

