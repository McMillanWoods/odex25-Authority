from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ModuleName(models.TransientModel):
    _name = 'purchase.committee.report'
    _description = 'Purchase Committee Report'

    type = fields.Selection([('None' , 'None') , ('department' , 'Department')],string="Group By")
    department_ids = fields.Many2many(comodel_name='hr.department', string='Deparments')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    state = fields.Selection([
        ('draft','Draft'),
        ('in_progress','Confirmed'),
        ('committee' , 'Committee'),
        ('purchase_manager' , 'Purchase manager'),
        ('second_approve' , 'Second Approval'),
        ('third_approve' , 'Third Approval'),
        ('accept','Accepted'),
        ('open','Bid Selection'),
        ('waiting','Waiting For Budget Confirmation'),
        ('checked','Budget Checked'),
        ('done','Done'),
        ('approve','Approved'),
        ('cancel','cancelled'),
    ],string="Status")
    show_committee_members = fields.Boolean(string='Show Committee Members')
    



    
    def action_print(self):
        department_ids = (self.department_ids and self.department_ids.ids) or self.env['hr.department'].search([]).ids
        data = {'department_ids' :  department_ids  , 'show_committee_members' : self.show_committee_members,
            'group_by' : self.type , 'date_from' : self.date_from ,
            'date_to' : self.date_to, 'state' : self.state }

        return self.env.ref('purchase_custom_report.action_report_purchase_committee').report_action([] , data = data)

class PurchaseGeneralReportParser(models.AbstractModel):
    _name = "report.purchase_custom_report.purchase_comittee_report"

    
    def _get_report_values(self, docids, data=None):
        report_values = []
        deparments = []
        if data['group_by'] == 'department':
            deparments = self.env['hr.department'].browse(data['department_ids']) 
            for dep in deparments:
                requisitions = self.env['purchase.requisition'].search([('department_id' , '=' , dep.id),
                    ('ordering_date' , '>=' ,data['date_from'] ),('ordering_date' , '<=' ,data['date_to'] ),
                    ('purchase_commitee' , '=' , True),
                    ('state' , '=' , data['state'])])
                if requisitions:
                    report_values.append({
                        'lable' : dep.name,
                        'data' : requisitions
                    })
        else:
            requisitions = self.env['purchase.requisition'].search([('department_id' , 'in' , data['department_ids']),
                    ('ordering_date' , '>=' ,data['date_from'] ),('ordering_date' , '<=' ,data['date_to'] ),
                    ('purchase_commitee' , '=' , True),
                    ('state' , '=' , data['state'])])
            if requisitions:
                report_values.append({
                    'lable' : "",
                    'data' : requisitions
                })
            


        if len(report_values) == 0:
            raise ValidationError(_("There is no Data"))
        
        return {
            'report_values' : report_values,
            'date_from' : data['date_from'],
            'date_to' : data['date_to'],
            'show_committee_members' : data['show_committee_members'],
            'group_by' : data['group_by']
        }



class PurchaseGeneralReportDetails(models.AbstractModel):
    _name = "report.purchase_custom_report.purchase_comittee_report_details"

    
    def _get_report_values(self, docids, data=None):
        committee_requisitions = []
        requisitions = self.env['purchase.requisition'].browse(docids)
        for requisition in requisitions:
            if requisition.purchase_commitee:
                committee_requisitions.append(requisition)
        if len(committee_requisitions) == 0:
            raise ValidationError(_('No tender need Committee'))
        else:
            return {
                'docs' : committee_requisitions,
                'self' : self
            }

    def get_orders(self,requisition_id):
        return self.env['purchase.order'].search([('requisition_id' , '=' , requisition_id )])
    def get_win(self,requisition_id):
        return self.env['purchase.order'].search([('requisition_id' , '=' , requisition_id ),
                ('state' , 'in' , ('sign' , 'purchase' , 'done'))
            ])

    
        
    

