# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class ArchiveTransactionWizard(models.TransientModel):
    _name = 'archive.transaction.wizard'

    note = fields.Text(string="Notes")
    date = fields.Date(string='Date', default=fields.Date.today)
    archive_type_id = fields.Many2one(comodel_name='cm.archive.type', string='Archive Reason')
    internal_transaction_id = fields.Many2one('internal.transaction', string='Internal')
    incoming_transaction_id = fields.Many2one('incoming.transaction', string='Outgoing')
    outgoing_transaction_id = fields.Many2one('outgoing.transaction', string='Incoming')

    def action_archive(self):
        from_id = self.env['cm.entity'].search([('user_id', '=', self.env.uid)], limit=1)
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
        transaction.state = 'closed'
        transaction.archive_user_id = from_id.id
        transaction.trace_ids.create({
            'from_id': from_id.id,
            'action': 'archive',
            'note': self.note,
            'archive_type_id': self.archive_type_id.id,
            name: transaction.id
        })
        close_employee = transaction.current_employee()
        subj = _('Message Has been closed !')
        msg = _(u'{} &larr; {}.<br />{}').format(
            close_employee and close_employee.name or '#', fields.Datetime.now(),
            u'<a href="%s" >رابط المعاملة</a> ' % (
                transaction.get_url()))
        # add mail notification
        partner_ids = [transaction.employee_id.user_id.partner_id.id]
        transaction.action_send_notification(subj, msg, partner_ids)
        if self.internal_transaction_id:
            transaction.action_send_close()