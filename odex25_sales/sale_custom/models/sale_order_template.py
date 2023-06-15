# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    sale_department_template_line_ids = fields.One2many('sale.department.template.line', 'sale_order_template_id', 'Mhr Estimated', copy=True)
    sale_job_template_line_ids = fields.One2many('sale.job.template.line', 'sale_order_template_id', 'Manpower', copy=True)
