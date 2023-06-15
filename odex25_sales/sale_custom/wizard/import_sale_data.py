# -*- coding: utf-8 -*-

import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
import io
import logging
import tempfile
import binascii
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class ImportSaleData(models.TransientModel):
    _name = 'import.sale.data'
    _description = 'Import Sale Data'

    attachment_ids = fields.Many2many('ir.attachment', string='Files', required=True)
    type_import = fields.Selection([('mhr_estimated', 'Mhrs Estimate'),
                                    ('manpower', 'Manpower'), 
                                    ], default="mhr_estimated", required="1")


    def import_file(self):
        sale_order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
        for data_file in self.attachment_ids:
            file_name = data_file.name.lower()
            if file_name.strip().endswith('.csv') or file_name.strip().endswith('.xlsx'):
                if file_name.strip().endswith('.xlsx'):
                    try:
                        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                        fp.write(binascii.a2b_base64(data_file.datas))
                        fp.seek(0)
                        workbook = xlrd.open_workbook(fp.name)
                        
                    except:
                        raise UserError(_("Invalid file!"))
                    vals_list = []
                    if self.type_import == 'mhr_estimated':
                        sheet = workbook.sheet_by_index(2)
                        sheet_pricing = workbook.sheet_by_index(3)
                        for row_no in range(11, sheet.nrows):
                            if row_no <= 0:
                                fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                            else:
                                line = list(map(
                                    lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                        row.value), sheet.row(row_no)))

                                
                                for depart in sale_order_id.mapped('sale_department_ids').filtered(lambda x: x.display_type == False):
                                    department_id = self.get_department(line[0] if line[0] else line[1])
                                    if department_id:
                                        if depart.department_id.id == department_id.id:
                                            depart.write({'no_sheet': int(float(line[3] if line[3] else 0)),
                                                            'hrs_sheet': line[5] if line[5] else 0,
                                                            'cairo_hrs':  line[7] if line[7] else 0,
                                                            'ksa_hrs': line[8] if line[8] else 0,})

                                
                        for row_pricing in range(7, sheet_pricing.nrows):
                            if row_pricing <= 0:
                                fields = map(lambda row: row.value.encode('utf-8'), sheet_pricing.row(row_pricing))
                            else:
                                line = list(map(
                                    lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                        row.value), sheet_pricing.row(row_pricing)))
                            
                            for order_line in sale_order_id.mapped('order_line').filtered(lambda x: x.display_type == False):
                                product_id = self.get_product(line[0])
                                if product_id:
                                    if order_line.product_id.id == product_id.id:
                                        order_line.write({
                                                        'product_uom_qty': line[2] if line[2] else 1,
                                                        'price_unit': line[4] if line[4] else line[6],})


                    if self.type_import == 'manpower':
                        sheet = workbook.sheet_by_index(0)
                        for row_no in range(4, sheet.nrows):
                            if row_no <= 0:
                                fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                            else:
                                line = list(map(
                                    lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                        row.value), sheet.row(row_no)))
                            for job in sale_order_id.mapped('sale_job_ids').filtered(lambda x: x.display_type == False):
                                job_id = self.get_job(line[2])
                                if job_id:
                                    if job.job_id.id == job_id.id:
                                        job.write({'no_year_experience': line[3],
                                                    'qty': int(float(line[4])),
                                                    'duration':  int(float(line[5])),
                                                    'month_rate': line[6],}
                                                )
                    

            else:
                raise ValidationError(_("Unsupported File Type"))


    def get_department(self, value):
        department = self.env['hr.department'].search([('name', '=', value.strip())])
        return department if department else False


    def get_job(self, value):
        job = self.env['hr.job'].search([('name', '=', value.strip())])
        return job if job else False


    def get_product(self, value):
        product = self.env['product.product'].search([('name', '=', value.strip())])
        return product if product else False
