# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class RejectReasonWizard(models.TransientModel):
    _name = 'reject.reason.wizard'

    reason = fields.Text(string="Reject Reason")
    internal_transaction_id = fields.Many2one('internal.transaction', string='Internal')
    incoming_transaction_id = fields.Many2one('incoming.transaction', string='Outgoing')
    outgoing_transaction_id = fields.Many2one('outgoing.transaction', string='Incoming')

    def action_confirm(self):
        transaction = ''
        name = ''
        if self.internal_transaction_id:
            transaction = self.internal_transaction_id
            name = 'internal_transaction_id'
        elif self.incoming_transaction_id:
            transaction = self.incoming_transaction_id
            name = 'incoming_transaction_id'
        elif self.outgoing_transaction_id:
            transaction = self.outgoing_transaction_id
            name = 'outgoing_transaction_id'
        employee = transaction.current_employee()
        transaction.reason = self.reason
        transaction.state = 'canceled'
        transaction.trace_ids.create({
            'action': 'refuse',
            'to_id': transaction.employee_id.id,
            'from_id': employee and employee.id or False,
            'note': self.reason,
            name: transaction.id
        })
        if self.internal_transaction_id:
            transaction.action_reject_email()

    def action_return_tran(self):
        transaction = ''
        name = ''
        if self.internal_transaction_id:
            transaction = self.internal_transaction_id
            name = 'internal_transaction_id'
        elif self.incoming_transaction_id:
            transaction = self.incoming_transaction_id
            name = 'incoming_transaction_id'
        elif self.outgoing_transaction_id:
            transaction = self.outgoing_transaction_id
            name = 'outgoing_transaction_id'
        employee = transaction.current_employee()
        transaction.reason = self.reason
        transaction.set_to_draft()
        transaction.trace_ids.create({
            'action': 'return',
            'to_id': transaction.employee_id.id,
            'from_id': employee and employee.id or False,
            'note': self.reason,
            name: transaction.id
        })
        if self.internal_transaction_id:
            transaction.action_return_email()
