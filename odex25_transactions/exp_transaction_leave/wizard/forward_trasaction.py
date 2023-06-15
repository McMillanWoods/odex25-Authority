# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, models, fields, _


class ForwardTransactionWizard(models.TransientModel):
    _inherit = 'forward.transaction.wizard'

    def action_forward(self):
        transaction = ''
        name = ''
        to_id = self.employee.id
        unit_id = self.employee.parent_id.id
        if self.internal_transaction_id:
            transaction = self.internal_transaction_id
            name = 'internal_transaction_id'
        elif self.incoming_transaction_id:
            transaction = self.incoming_transaction_id
            name = 'incoming_transaction_id'
        elif self.outgoing_transaction_id:
            transaction = self.outgoing_transaction_id
            name = 'outgoing_transaction_id'
        forward_user_id = self.employee.user_id
        if self.forward_type != 'employee':
            forward_user_id = self.internal_unit.secretary_id.user_id.id
            to_id = self.internal_unit.secretary_id.id
            unit_id = self.internal_unit.id
        transaction.forward_user_id = forward_user_id
        leave_employee = transaction.get_employee_leave(to_id, unit_id, date.today())
        if leave_employee:
            forward_user_id = self.env['cm.entity'].search([('id', '=', leave_employee)]).user_id.id
            to_id = leave_employee
            transaction.forward_user_id = forward_user_id
        transaction.last_forwarded_user = self.env.uid
        if self.is_secret:
            transaction.secret_reason = self.secret_reason
            transaction.secret_forward_user = self.env['cm.entity'].search([('user_id', '=', forward_user_id.id)], limit=1)
        employee = transaction.current_employee()
        from_id = self.env['cm.entity'].search([('user_id', '=', self.env.uid)], limit=1)
        transaction.is_forward = True
        if self.forward_attachment_id:
            transaction.attachment_rule_ids.create({
                'file_save': self.forward_attachment_id,
                'name': transaction.id,
                'description': self.att_description,
                'attachment_filename': self.filename,
            })
        transaction.trace_ids.create({
            'action': 'forward',
            'to_id': to_id,
            'from_id': from_id.id,
            'procedure_id': self.procedure_id.id or False,
            'note': self.note,
            'cc_ids': [(6, 0, self.cc_ids.ids)],
            name: transaction.id
        })
        if self.internal_transaction_id or self.incoming_transaction_id:
            transaction.action_send_forward()
        '''for notification partner in cc or forward user'''
        target = self.forward_type
        target_name = target == 'employee' and self.employee.name or self.internal_unit.name
        subj = _('Message Has been forwarded !')
        msg = _(u'{} &larr; {}').format(
            employee and employee.name or '#', target_name)
        msg = u'{}<br /><b>{}</b> {}.<br />{}'.format(msg,
                                                      _(u'Action Taken'), self.procedure_id.name,
                                                      u'<a href="%s" >رابط المعاملة</a> ' % (
                                                          transaction.get_url()))
        # add mail notification
        partner_ids = []
        if self.forward_type == 'unit':
            partner_ids.append(self.internal_unit.secretary_id.user_id.partner_id.id)
        elif self.forward_type == 'employee':
            partner_ids.append(self.employee.user_id.partner_id.id)
        for partner in self.cc_ids:
            if partner.type == 'unit':
                partner_ids.append(partner.secretary_id.user_id.partner_id.id)
            elif partner.type == 'employee':
                partner_ids.append(partner.user_id.partner_id.id)
        transaction.action_send_notification(subj, msg, partner_ids)
        if self.incoming_transaction_id:
            if transaction.state == 'draft':
                transaction.state = 'send'
