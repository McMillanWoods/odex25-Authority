# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class ReopenTransactionWizard(models.TransientModel):
    _name = 'reopen.transaction.wizard'

    note = fields.Text(string="Notes")
    reason = fields.Text(string="Description")
    date = fields.Date(string='Date', default=fields.Date.today)
    internal_transaction_id = fields.Many2one('internal.transaction', string='Internal')
    incoming_transaction_id = fields.Many2one('incoming.transaction', string='Outgoing')
    outgoing_transaction_id = fields.Many2one('outgoing.transaction', string='Incoming')
    procedure_id = fields.Many2one('cm.procedure', string='Action Taken')

    def action_reopen(self):
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
        transaction.action_reopen()
        from_id = self.env['cm.entity'].search([('user_id', '=', self.env.uid)], limit=1)
        transaction.trace_ids.create({
            'action': 'reopen',
            'procedure_id': self.procedure_id.id or False,
            'from_id': from_id.id,
            'note': self.note,
            name: transaction.id
        })
        close_employee = transaction.current_employee()
        subj = _('Message Has been reopened !')
        msg = _(u'{} &larr; {}').format(
            close_employee and close_employee.name or '#', fields.Datetime.now())
        msg = u'{}<br /><b>{}</b> {}.<br />{}'.format(msg,
                                                      _(u'Action Taken'), self.procedure_id.name,
                                                      u'<a href="%s" >رابط المعاملة</a> ' % (
                                                          transaction.get_url()))
        # add mail notification
        partner_ids = [transaction.employee_id.user_id.partner_id.id]
        transaction.action_send_notification(subj, msg, partner_ids)
        if self.internal_transaction_id:
            transaction.action_reopen_email()
