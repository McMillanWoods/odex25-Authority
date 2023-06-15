# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
import datetime
# from odoo.exceptions import ValidationError


class TransactionCommonReport(models.TransientModel):
    _name = "transaction.common.report"
    _description = "Transaction Common Report"

    type = fields.Selection(selection=[('unit', 'Unit'), ('employee', 'Employee')], string='Type', required=True)
    type_transact = fields.Selection([('internal', 'Internal'), ('incoming', 'Incoming'), ('all', 'All')],
                                     'Transaction Type')
    entity_ids = fields.Many2many(comodel_name='cm.entity', string='Entities', required=True)
    start_date = fields.Date(string='Start Date', default=datetime.date.today())
    end_date = fields.Date(string='End Date', default=datetime.date.today())

    @api.onchange('type')
    def onchange_type(self):
        domain = {}
        self.entity_ids = False
        if self.type == 'employee':
            domain = {'entity_ids': [('id', 'in', self.env['cm.entity'].search([('type', '=', 'employee')]).ids)]}
        elif self.type == 'unit':
            domain = {'entity_ids': [('id', 'in', self.env['cm.entity'].search([('type', '=', 'unit')]).ids)]}
        return {'domain': domain}
