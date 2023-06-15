# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CMConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    module_cm_hr_odex = fields.Boolean(string='Synchronization With HR ?', help='''
        If checked, you will be able to sync employees, departments, job titles with Crosspondence Tracking System.
    ''')
    module_cm_mail_odex = fields.Boolean(string='Convert Email Messages to Transactions', help='''
        If checked, you can convert emails to Incoming Transactions.
    ''')
    last_date_to_execute_transaction = fields.Boolean(string='Last Date To Execute Transaction', help='''
            If checked, you add rank value to start date to get last date to execute Transaction.
        ''')
    
    # ir.values is not exited in odoo 11 so i use ir.config_parameter instead of ir.value 15 Apr
    @api.model
    def get_values(self):
        res = super(CMConfig, self).get_values()
        res.update(
            last_date_to_execute_transaction=self.env['ir.config_parameter'].sudo().get_param('exp_transaction_documents.last_date_to_execute_transaction'),
            module_cm_mail_odex=self.env['ir.config_parameter'].sudo().get_param('exp_transaction_documents.module_cm_mail_odex'),
            module_cm_hr_odex=self.env['ir.config_parameter'].sudo().get_param('exp_transaction_documents.module_cm_hr_odex')
        )
        return res

    
    def set_values(self):
        super(CMConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('exp_transaction_documents.last_date_to_execute_transaction', self.last_date_to_execute_transaction)
        self.env['ir.config_parameter'].sudo().set_param('exp_transaction_documents.module_cm_mail_odex', self.module_cm_mail_odex)
        self.env['ir.config_parameter'].sudo().set_param('exp_transaction_documents.module_cm_hr_odex', self.module_cm_hr_odex)

    @api.model
    def create(self, vals):
        """
        create(vals) -> record
        Override create to change last_date_to_execute_transaction_id value in cm.subject.type
        """
        res = super(CMConfig, self).create(vals)
        if res.last_date_to_execute_transaction:
            for rec in self.env['cm.subject.type'].search([]):
                rec.last_date_to_execute_transaction_id = True
        return res
