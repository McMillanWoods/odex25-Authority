from odoo import api, fields, models,  _
from odoo.exceptions import ValidationError
from datetime import datetime

class ModuleName(models.TransientModel):
    _name = 'purchase.total.report'
    _description = 'Purchase General Report'

    vendor_ids = fields.Many2many(comodel_name='res.partner', string='Vendor')
    department_ids = fields.Many2many(comodel_name='hr.department', string='Deparments')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    product_ids = fields.Many2many(comodel_name='product.product', string='Products')
    group_by = fields.Selection(string='Grop By', selection=[('department', 'Department'), ('vendor', 'Vendor'),])
    type = fields.Selection([('detailed' , 'Detailed') , ('total' , 'Total')])
    
    def action_print(self):
        department_ids = None
        employee_ids = None
        vendor_ids = (self.vendor_ids and self.vendor_ids.ids) or self.env['res.partner'].search([('supplier_rank' , '>' ,0)]).ids
        department_ids = (self.department_ids and self.department_ids.ids) or self.env['hr.department'].search([]).ids
        product_ids = (self.product_ids and self.product_ids.ids) or self.env['product.product'].search([]).ids
        data = {'type' : self.type,'department_ids' :  department_ids , 'product_ids' : product_ids , 'vendor_ids' : vendor_ids , 
             'date_from' : self.date_from ,
            'date_to' : self.date_to, 'group_by' : self.group_by }

        return self.env.ref('purchase_custom_report.action_total_purchase').report_action([] , data = data)

    





class PurchaseTotalReportParser(models.AbstractModel):
    _name = "report.purchase_custom_report.purchase_total_report"

    
    def _get_report_values(self, docids, data=None):
        report_values = []
        deparments = []
        employees = []
        product_ids = data['product_ids']
        if data['group_by'] == 'department':
            deparments = self.env['hr.department'].browse(data['department_ids']) 
            for dep in deparments:
                po_ids = self.env['purchase.order'].search([
                    ('date_order' , '>=' ,data['date_from'] ),('date_order' , '<=' ,data['date_to'] ),
                    ('partner_id' , 'in' , data['vendor_ids'])]).ids
                if po_ids:
                    if data['type'] == 'total':
                        products = self._get_total_products(po_ids,product_ids)
                        if len(products) > 0:
                            report_values.append({
                                'lable' : dep.name,
                                'products' : products
                            })
                    else:
                        products = self._get_po_lines(po_ids,product_ids)
                        if len(products) > 0:
                            report_values.append({
                                'lable' : dep.name,
                                'lines' : products
                            })
        elif data['group_by'] == 'vendor' : 
            vendors = self.env['res.partner'].search([('id' , 'in' , data['vendor_ids'])])
            if vendors:
                for vendor in vendors:
                    po_ids = self.env['purchase.order'].search([('partner_id' , '=' , vendor.id),
                    ('date_order' , '>=' ,data['date_from'] ),('date_order' , '<=' ,data['date_to'])]).ids
                    if po_ids:
                        if data['type'] == 'total':
                            products = self._get_total_products(po_ids,product_ids)
                            if len(products) > 0:
                                report_values.append({
                                    'lable' : vendor.name,
                                    'products' : products
                                })
                        else:
                            products = self._get_po_lines(po_ids,product_ids)
                            if len(products) > 0:
                                report_values.append({
                                    'lable' : vendor.name,
                                    'lines' : products
                                })
        else:
            po_ids = self.env['purchase.order'].search([('partner_id' , 'in' , data['vendor_ids']),
                ('date_order' , '>=' ,data['date_from'] ),('date_order' , '<=' ,data['date_to'] ),
                ]).ids
            if po_ids:
                if data['type'] == 'total':
                    products = self._get_total_products(po_ids,product_ids)
                    if len(products) > 0:
                        report_values.append({
                            'lable' : "",
                            'products' : products
                        })
                else:
                    products = self._get_po_lines(po_ids,product_ids)
                    if len(products) > 0:
                        report_values.append({
                            'lable' : "",
                            'lines' : products
                        })
        if len(report_values) == 0:
            raise ValidationError(_("There is no Data"))
        
        return {
            'report_values' : report_values,
            'group_by' : data['group_by'],
            'date_from' : data['date_from'],
            'date_to' : data['date_to'],
            'type' : data['type'],
            'doc' : self
        }

    def date_format(self,date):
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()

    def _get_total_products(self,po_ids,product_ids):
        po_ids = str(po_ids).replace('[' , '(')
        po_ids = str(po_ids).replace(']' , ')')
        product_ids = str(product_ids).replace('[' , '(')
        product_ids = str(product_ids).replace(']' , ')')

        self.env.cr.execute("""
                            SELECT 
                                sum(line.product_qty) qty, 
                                product_templ.name product_name,
                                sum(line.price_subtotal) product_price 
                            FROM 
                                purchase_order_line line 
                            left join 
                                product_product product on (line.product_id = product.id) 
                            left join  
                                product_template product_templ on (product.product_tmpl_id = product_templ.id) 
                            where line.order_id in """ + po_ids +""" and 
                                line.product_id in """+ product_ids+"""
                            group by product_templ.name;
                        """)
        products = self.env.cr.dictfetchall()
        return products

    def _get_po_lines(self,po_ids,product_ids):
        lines = self.env['purchase.order.line'].search([('order_id' , 'in' , po_ids),('product_id' , 'in' , product_ids)])
        return lines

    
        
    

 