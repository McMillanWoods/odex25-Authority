from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ModuleName(models.TransientModel):
    _name = 'purchase.general.report'
    _description = 'Purchase General Report'

    type = fields.Selection([('employee' , 'Employee') , ('department' , 'Department')])
    vendor_ids = fields.Many2many(comodel_name='res.partner', string='Vendor')
    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Employee')
    department_ids = fields.Many2many(comodel_name='hr.department', string='Deparments')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    show_emp_details = fields.Boolean('Show Employees')
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



    
    def action_print(self):
        department_ids = None
        employee_ids = None
        vendor_ids = (self.vendor_ids and self.vendor_ids.ids) or self.env['res.partner'].search([('supplier_rank' , '>' ,0)]).ids
        department_ids = (self.department_ids and self.department_ids.ids) or self.env['hr.department'].search([]).ids
        employee_ids = (self.employee_ids and self.employee_ids.ids) or self.env['hr.employee'].search([]).ids
        data = {'show_emp_details'  : self.show_emp_details ,'department_ids' :  department_ids , 'employee_ids' : employee_ids , 'vendor_ids' : vendor_ids , 
            'type' : self.type , 'date_from' : self.date_from ,
            'date_to' : self.date_to, 'state' : self.state }

        return self.env.ref('purchase_custom_report.action_purchase_general_report').report_action([] , data = data)




class PurchaseGeneralReportParser(models.AbstractModel):
    _name = "report.purchase_custom_report.purchase_general_report"

    
    def _get_report_values(self, docids, data=None):
        report_values = []
        deparments = []
        employees = []
        if data['type'] == 'department':
            deparments = self.env['hr.department'].browse(data['department_ids']) 
            for dep in deparments:
                po_ids = self.env['purchase.order'].search([
                    ('date_order' , '>=' ,data['date_from'] ),('date_order' , '<=' ,data['date_to'] ),
                    ('partner_id' , 'in' , data['vendor_ids'])])
                if po_ids:
                    report_values.append({
                        'department' : dep,
                        'pos' : po_ids
                    })
        else:
            employees = self.env['hr.employee'].browse(data['employee_ids']) 
            for employee in employees:
                po_ids = self.env['purchase.order'].search([('date_order' , '>=' ,data['date_from'] ),('date_order' , '<=' ,data['date_to']),
                    ('partner_id' , 'in' , data['vendor_ids']),('employee_id' , '=' , employee.id)])
                if po_ids:
                    report_values.append({
                        'employee' : employee,
                        'requests' : po_ids
                    })


        if len(report_values) == 0:
            raise ValidationError(_("There is no Data"))
        
        return {
            'report_values' : report_values,
            'type' : data['type'],
            'show_emp_details' : data['show_emp_details']

        }
    
        
    

