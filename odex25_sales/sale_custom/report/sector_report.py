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

class SectorReport(models.AbstractModel):
    _name = 'report.sale_custom.sector_report'

    def get_sector_data(self, sector_id, data=None, context={}):
        datas = []
        sale_obj = self.env['sale.order']
        res = {}
        keys = []

        domain = [('date_order', '>=', data['form']['date_from']), ('date_order', '<=', data['form']['date_to']), 
                    ('sector_id', '=', sector_id)]

        sale_ids = sale_obj.search(domain)
        for sale in sale_ids:
            datas.append({
                'date': sale.date_order.strftime('%Y-%m-%d'),
                'bidbond': sale.bidbond,
                'crm_seq': sale.opportunity_id.code_rfp,
                'proposal': sale.name ,
                'name': sale.opportunity_id.name,
                'proposal_status':sale.proposal_state_id.name ,
                'project_duration': sale.project_duration ,
                'business_unit': sale.department_id.name,
                'p_fees': sale.amount_total,
                'customer': sale.partner_id,
            })

        for key,val in itertools.groupby(datas, key=operator.itemgetter("customer")):

            res[key.id] = list(val) if key.id not in res.keys() else res[key.id] + list(val)
            keys.append(key)
        
        return set(keys), res



    @api.model
    def _get_report_values(self, docids, data=None):

        sector_id = data['form']['sector_id'][0]
        keys, lines = self.get_sector_data(sector_id, data)

        return {
            'doc_ids': sector_id,
            'doc_model': 'sector',
            'data': data,
            'docs': self.env['sector'].browse(sector_id),
            'sector_data': lines,
            'keys': keys

        }

