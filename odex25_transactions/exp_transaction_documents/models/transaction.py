# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

TRANSACTION_STATE = [
    ('draft', _('Draft')),
    ('to_approve', _('To Approve')),
    ('complete', _('complete')),
    ('send', _('Send')),
    ('reply', _('Reply')),
    ('closed', _('Closed')),
    ('canceled', _('Canceled')),
]


class Transaction(models.Model):
    _name = 'transaction.transaction'
    _inherit = ['mail.thread']
    _description = 'for common attribute between transaction'

    name = fields.Char(string='Transaction Number')
    type = fields.Selection(string='Transaction Type', selection=[
        ('new', _('New Transaction')),
        ('forward', _('Forwarded Transaction')),
        ('reply', _('Reply'))], default='new')
    subject = fields.Char(string='Subject')
    important_id = fields.Many2one(comodel_name='cm.transaction.important', string='Important Degree')
    transaction_date = fields.Date(string='Transaction Date', default=fields.Date.today)
    transaction_date_hijri = fields.Char(string='Transaction Date (Hijri)', compute='compute_hijri')
    subject_type_id = fields.Many2one(comodel_name='cm.subject.type', string='Subject Type')
    is_need_approve = fields.Boolean(related='subject_type_id.transaction_need_approve', string='Need Approve')
    preparation_id = fields.Many2one(comodel_name='cm.entity', string='Preparation Unit',
                                     default=lambda self: self.default_preparation_id())
    employee_id = fields.Many2one(comodel_name='cm.entity', string='Created By',
                                  default=lambda self: self.default_employee_id())
    entity_id = fields.Many2one(comodel_name='cm.entity', string='Unit Responsible',
                                related='employee_id.parent_id', store=True)
    procedure_id = fields.Many2one(comodel_name='cm.procedure', string='Procedure')
    attachment_num = fields.Integer(string='No. of Attachments', compute='compute_attachment_num')
    body = fields.Html(string='Transaction Details')
    state = fields.Selection(selection=TRANSACTION_STATE, string='state', default='draft')
    need_approve = fields.Boolean(related='preparation_id.need_approve', string='NEED approve', )
    due_date = fields.Date(string='Deadline', compute='compute_due_date')
    send_date = fields.Date(string='Send Date')
    send_attach = fields.Many2many(
        comodel_name='ir.attachment',
        string='')
    current_is_manager = fields.Boolean(string='Is Manager', compute="set_is_manager")
    current_is_forward_user = fields.Boolean(string='Is Manager', compute="set_is_forward_user")
    current_user = fields.Boolean("current user", compute='_default_current_user')
    reason = fields.Text(string="Reject Reason")
    forward_user_id = fields.Many2one(comodel_name='res.users', string='Forward User')
    archive_user_id = fields.Many2one(comodel_name='cm.entity', string='Archive Entity')
    last_forwarded_user = fields.Many2one(comodel_name='res.users', string='Forwarded User')
    is_forward = fields.Boolean(string="Is Forward")
    ean13 = fields.Char(string='Ean13', size=30)
    receive_id = fields.Many2one(comodel_name='cm.entity', string='Receiver', compute='compute_receive_id')
    secret_reason = fields.Text(string="Secret reason")
    secret_forward_user = fields.Many2one(comodel_name='cm.entity', string='User')
    current_is_secret_user = fields.Boolean(string='Is Manager', compute="set_is_secret_user")
    receive_user_id = fields.Many2one(related='receive_id.user_id',
                                      comodel_name='res.users', string='Receiver', store=True)
    receive_manger_id = fields.Many2one(comodel_name='cm.entity', string='Receiver',
                                        compute='compute_receive_manger_id')
    current_is_receive_manger = fields.Boolean(string='Is Manager', compute="set_to_is_manager")
    to_user_have_leave = fields.Boolean(string="Have Leave?", default=False, compute='compute_have_leave')
    is_reade = fields.Boolean(string="Is Reade?!", default=True)
    is_favorite = fields.Selection([
        ('0', 'not'),
        ('1', 'Favorite'),
    ], size=1, string="Favorite")
    signature = fields.Binary("Signature image")
    tran_tag = fields.Many2many(comodel_name='transaction.tag', string='Tags')
    add_rank = fields.Integer(string='Transaction Rank')

    # @api.onchange('tran_tag')
    # def get_subject_type(self):
    #     # self.subject_type_id = False
    #     if self.tran_tag:
    #         domain = {'subject_type_id': [
    #             ('id', 'in', self.env['cm.subject.type'].search([('tran_tag', '=', self.tran_tage.id)
    #                                                              ]).ids)]
    #         }
    #     else:
    #         domain = {'subject_type_id': [('id', 'in', self.env['cm.subject.type'].search([]).ids)]
    #                   }
    #     return {'domain': domain}

    def action_read(self):
        for rec in self:
            rec.is_reade = True

    def action_unread(self):
        for rec in self:
            rec.is_reade = False

    def add_to_favorite(self):
        for rec in self:
            rec.is_favorite = '1'

    def remove_from_favorite(self):
        for rec in self:
            rec.is_favorite = '0'

    @api.constrains('type')
    def check_process_id(self):
        if self.type:
            if self.type != 'new':
                if not self.processing_ids:
                    raise ValidationError(_("please make sure transaction have Process Transactions..."))

    def default_employee_id(self):
        user = self.env.user
        em = self.env['cm.entity'].search([('user_id', '=', user.id)], limit=1)
        return len(em) and em or self.env['cm.entity']

    def compute_receive_id(self):
        for rec in self:
            if rec.to_ids:
                employee_id = rec.to_ids[0].id
                if rec.to_ids[0].type == 'unit':
                    employee_id = rec.to_ids[0].secretary_id.id
                rec.receive_id = employee_id

    def compute_receive_manger_id(self):
        for rec in self:
            rec.receive_manger_id = False
            if rec.preparation_id:
                rec.receive_manger_id = rec.preparation_id.manager_id

    def default_preparation_id(self):
        employee = self.default_employee_id()
        return len(employee) and employee.parent_id or self.env['cm.entity']

    @api.depends('transaction_date', 'important_id', 'add_rank')
    def compute_due_date(self):
        self.due_date = False
        for record in self:
            record.due_date = False
            if not len(record.important_id) or not record.transaction_date:
                continue
            rank = record.important_id.rank or 1
            final_rank = rank + record.add_rank
            date = datetime.strptime(str(record.transaction_date), DEFAULT_SERVER_DATE_FORMAT)
            due = date
            for i in range(final_rank):
                due = due + timedelta(days=1)
                if (due.strftime('%A') in ['vendredi', 'Friday']):
                    due = due + timedelta(days=2)
            record.due_date = due.strftime(DEFAULT_SERVER_DATE_FORMAT)

    def set_is_forward_user(self):
        user_id = self.env['res.users'].browse(self.env.uid)
        if self.forward_user_id.id == user_id.id:
            self.current_is_forward_user = True
        else:
            self.current_is_forward_user = False

    def set_is_manager(self):
        self.current_is_manager = True
        user_id = self.env['res.users'].browse(self.env.uid)
        if self.receive_manger_id.user_id == user_id:
            self.current_is_manager = True
        else:
            self.current_is_manager = False

    def set_to_is_manager(self):
        user_id = self.env['res.users'].browse(self.env.uid)
        if self.receive_id.parent_id.manager_id.user_id == user_id:
            self.current_is_receive_manger = True
        else:
            self.current_is_receive_manger = False

    def set_is_secret_user(self):
        user_id = self.env['res.users'].browse(self.env.uid)
        if self.secret_forward_user.user_id == user_id:
            self.current_is_secret_user = True
        else:
            self.current_is_secret_user = False

    def compute_have_leave(self):
        self.current_is_manager = False

    @api.depends('transaction_date')
    def compute_hijri(self):
        '''
        method for compute hijir date depend on date using odex hijri
        '''
        H = self.env['odex.hijri']
        for r in self:
            r.transaction_date_hijri = r.transaction_date and H.convert(r.transaction_date) or ''

    @api.model
    def current_employee(self):
        employee = False
        employees = self.env['cm.entity'].search(
            [('user_id', '=', self.env.user.id), ('type', '=', 'employee')], limit=1)
        if len(employees):
            employee = employees
        return employee

    def _default_current_user(self):
        for record in self:
            record.current_user = False
            if len(record.to_ids) == 1:
                if record.employee_id.user_id == self.env.user:
                    record.update({'current_user': True})
                else:
                    record.update({'current_user': False})

    @api.model
    def generate(self):
        EAN = self.env['odex.barcode']
        for r in self:
            return EAN.generate(r.ean13)

    ####################################################
    # Business methods
    ####################################################
    @api.model
    def action_draft(self):
        for record in self:
            if record.subject_type_id.transaction_need_approve or record.preparation_id.need_approve:
                if self.user_has_groups('exp_transaction_documents.group_cm_unit_manager'):
                    record.action_send()
                else:
                    record.state = 'to_approve'
            else:
                record.action_send()

    def action_send(self):
        for record in self:
            record.state = 'send'
            record.send_date = datetime.today()
            record.is_reade = False

    def action_approve(self):
        for record in self:
            record.state = 'send'
            record.is_reade = False

    def action_cancel(self):
        for record in self:
            record.state = 'canceled'

    def action_reopen(self):
        for record in self:
            record.state = 'send'

    def set_to_draft(self):
        for record in self:
            record.state = 'draft'

    def trace_create_ids(self, name, transaction, action):
        ''' method to create log trace in transaction'''
        employee = self.current_employee()
        to_id = transaction.to_ids[0].id
        if transaction.to_ids[0].type != 'employee':
            to_id = transaction.to_ids[0].secretary_id.id
        if transaction.subject_type_id.transaction_need_approve or transaction.preparation_id.need_approve and transaction.state == 'to_approve':
            to_id = transaction.preparation_id.manager_id.id
        transaction.trace_ids.create({
            'action': action,
            'to_id': to_id,
            'from_id': employee and employee.id or False,
            'procedure_id': transaction.procedure_id.id or False,
            name: transaction.id
        })

    def action_reject(self, name, transaction):
        form_view = self.env.ref('exp_transaction_documents.view_reject_transaction_wizard')
        return {
            'name': _('Reject Transaction'),

            'view_mode': 'form',
            'res_id': False,
            'views': [(form_view.id, 'form'), ],
            'res_model': 'reject.reason.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                name: transaction.id
            },
        }

    def action_return_tran(self, name, transaction):
        form_view = self.env.ref('exp_transaction_documents.view_return_transaction_wizard')
        return {
            'name': _('Return Transaction'),

            'view_mode': 'form',
            'res_id': False,
            'views': [(form_view.id, 'form'), ],
            'res_model': 'reject.reason.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                name: transaction.id
            },
        }

    def action_forward_tran(self, name, transaction):
        form_view = self.env.ref('exp_transaction_documents.forward_transaction_wizard_view')
        return {
            'name': _('Forward Transaction'),

            'view_mode': 'form',
            'res_id': False,
            'views': [(form_view.id, 'form'), ],
            'res_model': 'forward.transaction.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                name: transaction.id
            },
        }

    def action_reply_tran(self, name, transaction):
        form_view = self.env.ref('exp_transaction_documents.reply_transaction_wizard_view')
        return {
            'name': _('Reply Transaction'),

            'view_mode': 'form',
            'res_id': False,
            'views': [(form_view.id, 'form'), ],
            'res_model': 'transaction.reply.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                name: transaction.id
            },
        }

    def action_archive_tran(self, name, transaction):
        form_view = self.env.ref('exp_transaction_documents.archive_transaction_wizard_view')
        return {
            'name': _('Archive Transaction'),

            'view_mode': 'form',
            'res_id': False,
            'views': [(form_view.id, 'form'), ],
            'res_model': 'archive.transaction.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                name: transaction.id
            },
        }

    def action_reopen_tran(self, name, transaction):
        form_view = self.env.ref('exp_transaction_documents.reopen_transaction_wizard_view')
        return {
            'name': _('Reopen Transaction'),

            'view_mode': 'form',
            'res_id': False,
            'views': [(form_view.id, 'form'), ],
            'res_model': 'reopen.transaction.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                name: transaction.id
            },
        }

    ####################################################
    # Messaging methods
    ####################################################
    def get_name(self):
        name = False
        if self.is_forward:
            name = self.forward_user_id.name
        elif self.to_ids[0].type != 'employee':
            name = self.to_ids[0].secretary_id.user_id.name
        else:
            name = self.receive_id.user_id.name
        return name

    def get_email(self):
        email = False
        if self.is_forward:
            name = self.forward_user_id.partner_id.email
        elif self.to_ids[0].type != 'employee':
            email = self.to_ids[0].secretary_id.user_id.partner_id.email
        else:
            email = self.receive_id.user_id.partner_id.email
        return email

    def send_message(self, template=None):
        if not template:
            return
        template = self.env.ref(template, False)
        if not template:
            return
        for r in self:
            template.with_context(lang=self.env.user.lang).send_mail(
                r.id, force_send=True, raise_exception=False)

    def action_send_notification(self, subj, msg, partner_ids):
        self.ensure_one()
        for rec in self:
            author = self.env['res.users'].sudo().browse(self._uid)
            author = author.id
            if False not in partner_ids:
                rec.message_post(type="notification", subject=subj, body=msg, author_id=author,
                                 partner_ids=partner_ids,
                                 subtype_xmlid="mail.mt_comment")
