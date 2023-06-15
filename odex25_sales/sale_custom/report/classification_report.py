# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _

class ClassificationReport(models.AbstractModel):
    _name = 'report.sale_custom.classification_report'

    def get_classification_data(self, partner_ids, data=None, context={}):
        datas = []
        sale_obj = self.env['sale.order']
        res = {x: [] for x in partner_ids}

        for partner in partner_ids:
            domain = [('date_order', '>=', data['form']['date_from']), ('date_order', '<=', data['form']['date_to']), 
                        ('partner_id', '=', partner)]

            sale_ids = sale_obj.search(domain)
            for sale in sale_ids:
                datas = {
                    'date': sale.date_order.strftime('%Y-%m-%d'),
                    'bidbond': sale.bidbond,
                    'crm_seq': sale.opportunity_id.code_rfp,
                    'proposal': sale.name ,
                    'name': sale.opportunity_id.name,
                    'proposal_status':sale.proposal_state_id.name ,
                    'project_duration': sale.project_duration ,
                    'business_unit': sale.department_id.name,
                    'p_fees': sale.amount_total,
                }

                res[partner].append(datas)
        return res



    @api.model
    def _get_report_values(self, docids, data=None):

        classification_ids = data['form']['classification_ids']
        res = {x: [] for x in classification_ids}
        for classification in classification_ids:

            partner = self.env['res.partner'].search([('industry_id', '=', classification)]).ids
            lines = self.get_classification_data(partner, data)

            res[classification].append(lines)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        
        return {
            'doc_model': model,
            'data': data,
            'docs': docs,
            'classification_data': res,
        }

