# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, fields, _


class InternalTransaction(models.Model):
    _name = 'internal.transaction'
    _inherit = ['transaction.transaction', 'mail.thread']
    _description = 'internal Transaction'

    # due_date = fields.Date(string='Deadline', compute='_compute_due_date')
    reason = fields.Text('Reason')
    attachment_rule_ids = fields.One2many('cm.attachment.rule', 'internal_transaction_id', string='Attaches')
    attachment_ids = fields.One2many('cm.attachment', 'internal_transaction_id', string='Attachments')
    trace_ids = fields.One2many('cm.transaction.trace', 'internal_transaction_id', string='Trace Log')
    type_sender = fields.Selection(
        string='',
        selection=[('unit', 'Unit'),
                   ('employee', 'Employee'),
                   ],
        required=False, default='unit')

    to_ids = fields.Many2many(comodel_name='cm.entity', relation='internal_entity_rel', column1='internal_id'
                              , column2='entity_id', string='Send To')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True,
                                 related='to_ids.secretary_id.partner_id')
    cc_ids = fields.Many2many(comodel_name='cm.entity', relation='internal_entity_cc_rel',
                              column1='internal_id', column2='entity_id', string='CC To')
    project_domain = fields.Many2many('project.project', string='Project Domain')
    processing_ids = fields.Many2many(comodel_name='internal.transaction', relation='transaction_internal_rel',
                                      column1='transaction_id', column2='internal_id', string='Process Transactions')

    @api.model
    def get_url(self):
        url = u''
        action = self.env.ref(
            'exp_transaction_documents.incoming_internal_tran_action', False)
        Param = self.env['ir.config_parameter'].sudo()
        if action:
            return u'{}/web#id={}&action={}&model=internal.transaction'.format(
                Param.get_param('web.base.url', self.env.user.company_id.website), self.id, action.id)
        return url

    @api.depends('attachment_rule_ids')
    def compute_attachment_num(self):
        for r in self:
            r.attachment_num = len(r.attachment_rule_ids)

    def fetch_sequence(self, data=None):
        '''generate transaction sequence'''
        return self.env['ir.sequence'].get('cm.transaction.internal') or _('New')

    ####################################################
    # Business methods
    ####################################################

    def action_draft(self):
        for record in self:
            """her i need to review code for to_ids"""
            res = super(InternalTransaction, self).action_draft()
            sent = 'sent'
            template = 'exp_transaction_documents.internal_notify_send_send_email'
            if record.subject_type_id.transaction_need_approve or record.preparation_id.need_approve:
                template = 'exp_transaction_documents.internal_approval1_request_email'
                sent = 'waite'
            record.trace_create_ids('internal_transaction_id', record, sent)
            partner_ids = []
            for partner in record.to_ids:
                if partner.type == 'unit':
                    partner_ids.append(partner.secretary_id.user_id.partner_id.id)
                    record.forward_user_id = partner.secretary_id.user_id.id
                elif partner.type == 'employee':
                    partner_ids.append(partner.user_id.partner_id.id)
                    record.forward_user_id = partner.user_id.id
            if record.to_user_have_leave:
                record.forward_user_id = record.receive_id.user_id.id
            record.send_message(template=template)
            subj = _('Message Has been send !')
            msg = _(u'{} &larr; {}').format(record.employee_id.name, u' / '.join([k.name for k in record.to_ids]))
            msg = u'{}<br /><b>{}</b> {}.<br />{}'.format(msg,
                                                          _(u'Action Taken'), record.procedure_id.name,
                                                          u'<a href="%s" >رابط المعاملة</a> ' % (
                                                              record.get_url()))
            company_id = self.env.user.company_id
            if company_id.sms_active == True:
                message = "There is a transaction that needs to " + self.procedure_id.name if self.procedure_id else ""
                message += " with the number " + self.name
                print(record.employee_id.employee_id.phone)
                print(message)
                request = company_id.send_sms(str(record.employee_id.employee_id.phone), message if message else "")
            for rec in record:
                rec.action_send_notification(subj, msg, partner_ids)
            return res

    def action_approve(self):
        res = super(InternalTransaction, self).action_approve()
        template = 'exp_transaction_documents.internal_notify_send_send_email'
        self.send_message(template=template)
        employee = self.current_employee()
        to_id = self.to_ids[0].id
        if self.to_ids[0].type != 'employee':
            to_id = self.to_ids[0].secretary_id.id
        self.trace_ids.create({
            'action': 'sent',
            'to_id': to_id,
            'from_id': employee and employee.id or False,
            'procedure_id': self.procedure_id.id or False,
            'internal_transaction_id': self.id
        })
        # self.trace_create_ids('internal_transaction_id', self, 'sent')
        subj = _('Message Has been approved !')
        msg = _(u'{} &larr; {}').format(self.preparation_id.manager_id.name, u' / '.join([k.name for k in self.to_ids]))
        msg = u'{}<br /><b>{}</b> {}.<br />{}'.format(msg,
                                                      _(u'Action Taken'), self.procedure_id.name,
                                                      u'<a href="%s" >رابط المعاملة</a> ' % (
                                                          self.get_url()))
        partner_ids = [self.employee_id.user_id.partner_id.id, self.to_ids[0].user_id.partner_id.id]
        self.action_send_notification(subj, msg, partner_ids)
        return res

    def action_reject_internal(self):
        name = 'default_internal_transaction_id'
        return self.action_reject(name, self)

    def action_return_internal(self):
        name = 'default_internal_transaction_id'
        return self.action_return_tran(name, self)

    def action_forward_internal(self):
        name = 'default_internal_transaction_id'
        return self.action_forward_tran(name, self)

    def action_reply_internal(self):
        name = 'default_internal_transaction_id'
        return self.action_reply_tran(name, self)

    def action_archive_internal(self):
        name = 'default_internal_transaction_id'
        return self.action_archive_tran(name, self)

    def action_reopen_internal(self):
        name = 'default_internal_transaction_id'
        return self.action_reopen_tran(name, self)

    def get_latest_forward(self):
        for rec in self:
            return rec.trace_ids.filtered(lambda z: z.action == 'forward')[0]

    def get_latest_by_action(self, action):
        for rec in self:
            return rec.trace_ids.filtered(lambda z: z.action == action)[0]

    def action_send_forward(self):
        template = 'exp_transaction_documents.internal_notify_forward_email'
        self.send_message(template=template)

    def action_send_reply(self):
        template = 'exp_transaction_documents.internal_notify_reply_email'
        self.send_message(template=template)

    def action_send_close(self):
        template = 'exp_transaction_documents.internal_notify_close_email'
        self.send_message(template=template)

    def action_reopen_email(self):
        template = 'exp_transaction_documents.internal_reopen_transaction_email'
        self.send_message(template=template)

    def action_reject_email(self):
        template = 'exp_transaction_documents.internal_reject_transaction_email'
        self.send_message(template=template)

    def action_return_email(self):
        template = 'exp_transaction_documents.internal_return_transaction_email'
        self.send_message(template=template)

    def late_transaction_cron(self):
        templates = 'exp_transaction_documents.internal_late_transaction_email'
        transaction_ids = self.env['internal.transaction'].search([('state', 'in', ['send', 'reply'])])
        if transaction_ids:
            today = fields.date.today()
            for transaction in transaction_ids:
                if datetime.strptime(transaction.due_date, "%Y-%m-%d") < datetime.strptime(str(today), "%Y-%m-%d"):
                    rec = transaction.trace_ids.filtered(lambda z: z.action == 'forward' or z.action == 'sent' or
                                                                   z.action == 'reply')[0]
                    template = self.env.ref(templates, False)
                    template.write({'email_to': rec.to_id.user_id.partner_id.email,
                                    'email_cc': rec.to_id.parent_id.manager_id.user_id.partner_id.email})
                    template.with_context(lang=self.env.user.lang).send_mail(
                        transaction.id, force_send=True, raise_exception=False)

    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.model
    def create(self, vals):
        seq = self.fetch_sequence()
        if vals.get('preparation_id', False):
            code = self.env['cm.entity'].browse(vals['preparation_id']).code
            x = seq.split('/')
            sequence = "%s/%s/%s" % (x[0], code, x[1])
            vals['name'] = sequence
        else:
            vals['name'] = seq
        # vals['ean13'] = self.env['odex.barcode'].code128('IL', vals['name'], 'TR')
        return super(InternalTransaction, self).create(vals)

    #
    # def unlink(self):
    #     if self.env.uid != 1:
    #         raise ValidationError(_("You can not delete transaction....."))
    #     return super(InternalTransaction, self).unlink()
