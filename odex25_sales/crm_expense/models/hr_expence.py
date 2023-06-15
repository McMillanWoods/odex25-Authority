# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    crm_lead_id = fields.Many2one('crm.lead', 'CRM Lead')
