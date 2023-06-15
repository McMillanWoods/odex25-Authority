from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class OnlineTenderWizard(models.TransientModel):
    _name = 'online.tender.report'
    _description = 'Online Tender Report'

    type = fields.Selection([('tender' , 'Tender') , ('application' , 'Application'),('price' , 'Prices')],string="Detailing Level")
    department_ids = fields.Many2many(comodel_name='hr.department', string='Deparments')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    # product_ids = fields.Many2many(comodel_name='product.product', string='Products')
    tender_id = fields.Many2one(comodel_name='purchase.requisition', string='Tender')
    state = fields.Selection([('draft' , 'Draft') , ('tender' , 'Tender') , ('contract' , 'Contract'),('reject' , 'Rejected')],string="State")
    


    
    def action_print(self):
        department_ids = (self.department_ids and self.department_ids.ids) or self.env['hr.department'].search([]).ids
        data = {
                'tender_id' : self.tender_id.id,
                'type'  : self.type , 'department_ids' :  department_ids ,  
                'date_from' : self.date_from ,
                'date_to' : self.date_to ,
                'state' : self.state,
                'printed_type' : dict(self._fields['type']._description_selection(self.env)).get(self.type) }

        return self.env.ref('online_tendering.action_online_tendering_report').report_action([] , data = data)




class PurchaseGeneralReportParser(models.AbstractModel):
    _name = "report.online_tendering.online_tender_report"

    
    def get_report_values(self, docids, data=None):
        report_values = []
        product_prices = []
        applications = []
        tender_id = None
        deparments = self.env['hr.department'].browse(data['department_ids'])
        tender_ids = self.env['purchase.requisition'].search([('published_in_portal' , '=' , True),('ordering_date' , '>=' ,data['date_from'] ),('ordering_date' , '<=' ,data['date_to'])])
        if data['type'] == 'tender':
            for dep in deparments:
                tender_ids = self.env['purchase.requisition'].search([('department_id' , '=' , dep.id),
                ('ordering_date' , '>=' ,data['date_from']),
                ('published_in_portal' , '=' , True),
                ('ordering_date' , '<=' ,data['date_to'])])
                if tender_ids:
                    report_values.append({
                        'lable' : dep.name,
                        'data' : tender_ids
                    })
        elif data['type'] == 'application':
            for tender in tender_ids:
                applications = self.env['tender.application'].search([('tender_id' , '=' , tender.id),('state' , '=' , data['state'])])
                if applications:
                    report_values.append({
                        'lable' : tender.name,
                        'data' : applications,
                    })
        elif data['type'] == 'price': 
            tender_id = self.env['purchase.requisition'].search([('id' , '=' , data['tender_id'])])
            for line in tender_id.line_ids:
                application_lines = self.env['tender.application.line'].search([
                    ('tender_id' ,'=' , tender_id.id),
                    ('product_id' , '=' , line.product_id.id),
                    ('state'  , '=' , data['state'])
                ])
                if application_lines:
                    report_values.append({
                        'lable' : line,
                        'data' : application_lines
                    })
        if len(report_values) == 0:
            raise ValidationError(_("There is no Data"))
        
        return {
            'report_values' : report_values,
            'date_from' : data['date_from'],
            'date_to' : data['date_to'],
            'type' : data['type'],
            'printed_type' : data['printed_type'],
            'doc' : self,
            'tender_id' : tender_id
        }

    def date_format(self,date):
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()

    
        
    

