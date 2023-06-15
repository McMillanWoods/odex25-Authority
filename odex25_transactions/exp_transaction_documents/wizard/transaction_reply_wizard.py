# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class TransactionReturnWizard(models.TransientModel):
    _name = 'transaction.reply.wizard'

    cc_ids = fields.Many2many(comodel_name='cm.entity', string='CC To')
    note = fields.Text(string="Notes")
    description = fields.Text(string="Description")
    date = fields.Date(string='Date', default=fields.Date.today)
    procedure_id = fields.Many2one(comodel_name='cm.procedure', string='Procedure')
    internal_transaction_id = fields.Many2one('internal.transaction', string='Internal')
    incoming_transaction_id = fields.Many2one('incoming.transaction', string='Incoming')
    outgoing_transaction_id = fields.Many2one('outgoing.transaction', string='Outgoing')
    attachment_id = fields.Binary(attachment=True, string='Forward Attachment')
    filename = fields.Char()
    att_description = fields.Char(string='Attach Description')

    def action_reply(self):
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
        transaction_trace_obj = self.env['cm.transaction.trace']
        transaction_id = transaction_trace_obj.search(
            [(name, '=', transaction.id), ('action', 'not in', ('archive', 'reopen'))],
            order="create_date desc", limit=1)
        if transaction_id:
            transaction.forward_user_id = transaction_id.from_id.user_id.id
        else:
            transaction.forward_user_id = transaction.employee_id.user_id.id
        transaction.state = 'reply'
        forward_entity = self.env['cm.entity'].search([('user_id', '=', transaction.forward_user_id.id)],limit=1)
        transaction.attachment_rule_ids.create({
            'file_save': self.attachment_id,
            # 'name': transaction.id,
            'description': self.att_description,
            'attachment_filename': self.filename,
        })
        transaction.trace_ids.create({
            'action': 'reply',
            'to_id': forward_entity.id,
            'from_id': from_id.id,
            'procedure_id': self.procedure_id.id or False,
            'note': self.note,
            'cc_ids': [(6, 0, self.cc_ids.ids)],
            name: transaction.id
        })
        employee = transaction.current_employee()
        subj = _('Message Has been replied !')
        msg = _(u'{} &larr; {}').format(employee and employee.name or '#',
                                        transaction.forward_user_id.name)
        msg = u'{}<br /><b>{}</b> {}.<br />{}'.format(msg,
                                                      _(u'Action Taken'), self.procedure_id.name,
                                                      u'<a href="%s" >رابط المعاملة</a> ' % (
                                                          transaction.get_url()))
        # add mail notification
        partner_ids = [transaction.forward_user_id.partner_id.id]
        for partner in self.cc_ids:
            if partner.type == 'unit':
                partner_ids.append(partner.secretary_id.user_id.partner_id.id)
            elif partner.type == 'employee':
                partner_ids.append(partner.user_id.partner_id.id)
        transaction.action_send_notification(subj, msg, partner_ids)
        if self.internal_transaction_id:
            transaction.action_send_reply()