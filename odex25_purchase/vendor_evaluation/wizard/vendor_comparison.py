from odoo import models, fields, api,_,exceptions
from datetime import datetime
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class VendorComparrisonWizard(models.TransientModel):
    _name = 'vendor.comparison.wizard'
    _description = 'vendor.comparison.wizard'

    type = fields.Selection([('detailed' , 'Detaild') , ('cumulative' , 'Cumulative')])
    vendor_ids = fields.Many2many('res.partner',domain="[('supplier_rank' , '>' , 1) ]")
    criteria_ids = fields.Many2many('evaluation.criteria',string='criteria')




    
    def action_print(self):
        vendor_ids = self.vendor_ids.ids
        criteria_ids = self.criteria_ids.ids
        if not self.vendor_ids.ids:
            vendor_ids =  self.env['res.partner'].search([('supplier_rank' , '>' , 1) ]).ids
        if not vendor_ids:
            raise exceptions.ValidationError(_("Sorry There is No Vendor,make sure you have partner as supplier"))

        if not self.criteria_ids:
            criteria_ids =  self.env['evaluation.criteria'].search([]).ids

        data = {'vendor_ids' : vendor_ids , 'criteria_ids' : criteria_ids , 'report_type' : self.type}
        return self.env.ref('vendor_evaluation.action_vendor_compaarison_report').report_action([] , data=data)


class VendorComparisonParser(models.AbstractModel):
    _name = "report.vendor_evaluation.vendor_comparison_report"
    _description = 'vendor.valuation.report'

    
   
    
    def _get_report_values(self, docids, data=None):
        """
            this method query database according to report type if it is detailed report will get report by criterie
            if its totoal get report by cumulative records
        """
        type = ''
        report_data = []
        departments = [_('account'), _('purchase') , _('stock')]
        vendor_ids = data['vendor_ids']
        criteria_ids = data['criteria_ids']
        
        if data['report_type'] == 'detailed':
            vendors = ",".join(str(i) for i in vendor_ids)
            conditions= '''
                 det.vendor_id  in '''+('''(''' + vendors +''')''' )+'''
                '''
            for criteria_id in criteria_ids:
                self.env.cr.execute("""
                    select 
                        sum(det.value)/count(det.value) as eval, det.vendor_id vendor ,max(v.name) v_name
                    from 
                        evaluation_details det left join res_partner v on (det.vendor_id = v.id) where det.criteria_id = """+str(criteria_id)+"""and 
                        """+conditions+"""
                        group by vendor 
                        order by eval desc ;
                """)
                data = self.env.cr.dictfetchall()
                report_data.append({
                    'criteria_id' : self.env['evaluation.criteria'].browse([criteria_id]),
                    'data' : data,
                })
            type  = 'detailed'  
        else:
            vendors = ",".join(str(i) for i in vendor_ids)
            conditions= '''
                 eval.vendor_id  in '''+('''(''' + vendors +''')''' )+'''
                '''
            type  = 'cumulative' 
            for dep in departments:
                self.env.cr.execute("""
                    select 
                        eval.last_eval as eval ,v.name v_name
                    from 
                        cumulative_vendor_evaluation eval left join res_partner v on (eval.vendor_id = v.id) where 
                        """+conditions+""" and eval.owner = '""" +str(dep)+"""'
                        order by eval desc ;
                """)
                data = self.env.cr.dictfetchall()
                report_data.append({
                    'department' : dep,
                    'data' : data,
                })
        return {
            'data' : report_data,
            'type'  : type
        }


    
