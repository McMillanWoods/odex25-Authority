# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _

class SummaryReport(models.AbstractModel):
    _name = 'report.sale_custom.summary_report'

    def get_summary_data(self, data=None, context={}):
        datas = []
        sale_obj = self.env['sale.order']
        business_unit_ids = data['form']['business_unit_ids']
        for business in business_unit_ids:
            domain = [('date_order', '>=', data['form']['date_from']), ('date_order', '<=', data['form']['date_to']), 
                     ('department_id', '=', business)]

            sale_ids = sale_obj.search(domain)
            project_id = sale_ids.filtered(lambda x: x.project_id != False)
            datas.append({
                'business': self.env['hr.department'].browse(business),
                'job_no': len(project_id),
            })

            return datas

    def get_status_data(self, data=None, context={}):

        return True



    @api.model
    def _get_report_values(self, docids, data=None):

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))


        # for business in data['form']['business_unit_ids']:
        status_data = self.get_status_data(data)

        return {
            'doc_model': model,
            'data': data,
            'docs': docs,
            'summary_data': self.get_summary_data(data),
        }

