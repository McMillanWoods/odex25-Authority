# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _

class CustomReport(models.AbstractModel):
    _name = 'report.sale_custom.custom_report'

    def get_custom_data(self, business_unit_ids, data=None, context={}):
        datas = []
        sale_obj = self.env['sale.order']
        res = {x: [] for x in business_unit_ids}

        for business in business_unit_ids:
            domain = [('date_order', '>=', data['form']['date_from']), ('date_order', '<=', data['form']['date_to']), 
                     ('business_unit_ids', '=', business)]


            if data['form']['proposal_state_id']:
                domain+= [('proposal_state_id', '=', data['form']['proposal_state_id'][0])]

            sale_ids = sale_obj.search(domain)
            for sale in sale_ids:
                datas = {
                    'date': sale.date_order.strftime('%Y-%m-%d'),
                    'crm_seq': sale.opportunity_id.code,
                    'proposal': sale.name ,
                    'name': sale.opportunity_id.name,
                    'proposal_status':sale.proposal_state_id.name ,
                    'project_duration': sale.project_duration ,
                    'p_fees': sale.amount_total,
                    'contract_status': sale.contract_status,
                    'customer': sale.partner_id,
                }

                res[business].append(datas)
            return res



    @api.model
    def _get_report_values(self, docids, data=None):

        business_unit_ids = data['form']['business_unit_ids']

        lines = self.get_custom_data(business_unit_ids, data)


        return {
            'doc_ids': business_unit_ids,
            'doc_model': 'hr.department',
            'data': data,
            'docs': self.env['hr.department'].browse(business_unit_ids),
            'custom_data': lines,
        }

