# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class IncomingTransaction(models.Model):
    _name = 'incoming.transaction'
    _inherit = ['transaction.transaction', 'mail.thread']
    _description = 'incoming Transaction'

    # due_date = fields.Date(string='Deadline', compute='compute_due_date')
    from_id = fields.Many2one(comodel_name='cm.entity', string='Incoming From (External)')
    partner_id = fields.Many2one('res.partner')
    outgoing_transaction_id = fields.Many2one('outgoing.transaction', string='Related Outgoing')
    incoming_number = fields.Char(string='Incoming Number')
    incoming_date = fields.Date(string='Incoming Date', default=fields.Date.today)
    incoming_date_hijri = fields.Char(string='Incoming Date (Hijri)', compute='_compute_incoming_date_hijri')
    attachment_rule_ids = fields.One2many('cm.attachment.rule', 'incoming_transaction_id', string='Attaches')
    attachment_ids = fields.One2many('cm.attachment', 'incoming_transaction_id', string='Attachments')
    trace_ids = fields.One2many('cm.transaction.trace', 'incoming_transaction_id', string='Trace Log')
    to_ids = fields.Many2many(comodel_name='cm.entity', relation='incoming_entity_rel', column1='incoming_id'
                              , column2='entity_id', string='Send To')
    cc_ids = fields.Many2many(comodel_name='cm.entity', relation='incoming_entity_cc_rel',
                              column1='incoming_id', column2='entity_id', string='CC To')
    tran_tag = fields.Many2many(comodel_name='transaction.tag', string='Tags')
    tran_tag_unit = fields.Many2many(comodel_name='transaction.tag', string='Business unit',
                                     relation='incoming_tag_rel',
                                     column1='incoming_id'
                                     , column2='name')
    project_id = fields.Many2many('project.project')
    sale_order_id = fields.Many2one('sale.order', 'Proposal')
    processing_ids = fields.Many2many(comodel_name='incoming.transaction', relation='transaction_incoming_incoming_rel',
                                      column1='transaction_id', column2='incoming_id',
                                      string='Process Transactions incoming')
    processing2_ids = fields.Many2many(comodel_name='outgoing.transaction',
                                       relation='transaction_incoming_outgoing_rel',
                                       column1='transaction_id', column2='outgoing_id',
                                       string='Process Transactions Outgoing')
    attachment_count = fields.Integer(compute='count_attachments')
    # attachment_file = fields.Many2many(
    #     comodel_name='ir.attachment',
    #     string='')

    datas = fields.Binary(string="", related='send_attach.datas')

    def count_attachments(self):
        obj_attachment = self.env['ir.attachment']
        for record in self:
            record.attachment_count = 0
            attachment_ids = obj_attachment.search(
                [('res_model', '=', 'incoming.transaction'), ('res_id', '=', record.id)])
            first_file = []
            if attachment_ids:
                first_file.append(attachment_ids[0].id)
                print(first_file)
                record.attachment_file = first_file
            record.attachment_count = len(attachment_ids)

    @api.model
    def get_url(self):
        url = u''
        action = self.env.ref(
            'exp_transaction_documents.forward_incoming_external_tran_action', False)
        Param = self.env['ir.config_parameter'].sudo()
        if action:
            return u'{}/web#id={}&action={}&model=incoming.transaction'.format(
                Param.get_param('web.base.url', self.env.user.company_id.website), self.id, action.id)
        return url

    @api.depends('incoming_date')
    def _compute_incoming_date_hijri(self):
        '''
        method for compute hijir date depend on date using odex hijri
        '''
        H = self.env['odex.hijri']
        for r in self:
            r.incoming_date_hijri = r.incoming_date and H.convert(r.incoming_date) or ''

    @api.depends('attachment_rule_ids')
    def compute_attachment_num(self):
        for r in self:
            r.attachment_num = len(r.attachment_rule_ids)

    def fetch_sequence(self):
        '''generate transaction sequence'''
        return self.env['ir.sequence'].next_by_code('cm.transaction.in') or _('New')

    ####################################################
    # Business methods
    ####################################################

    def action_draft(self):
        for record in self:
            res = super(IncomingTransaction, self).action_send()
            employee = self.current_employee()
            to_id = self.to_ids[0].id
            if self.to_ids[0].type != 'employee':
                to_id = self.to_ids[0].secretary_id.id
            record.trace_ids.create({
                'action': 'sent',
                'to_id': to_id,
                'from_id': employee and employee.id or False,
                'procedure_id': record.procedure_id.id or False,
                'incoming_transaction_id': record.id
            })
            partner_ids = []
            for partner in record.to_ids:
                if partner.type == 'unit':
                    partner_ids.append(partner.secretary_id.user_id.partner_id.id)
                    record.forward_user_id = partner.secretary_id.user_id.id
                elif partner.type == 'employee':
                    partner_ids.append(partner.user_id.partner_id.id)
                    record.forward_user_id = partner.user_id.id
            subj = _('Message Has been send !')
            msg = _(u'{} &larr; {}').format(record.employee_id.name, u' / '.join([k.name for k in record.to_ids]))
            msg = u'{}<br /><b>{}</b> {}.<br />{}'.format(msg,
                                                          _(u'Action Taken'), record.procedure_id.name,
                                                          u'<a href="%s" >رابط المعاملة</a> ' % (
                                                              record.get_url()))
            self.action_send_notification(subj, msg, partner_ids)
            template = 'exp_transaction_documents.incoming_notify_send_send_email'
            self.send_message(template=template)
            return res

    def action_send_forward(self):
        template = 'exp_transaction_documents.incoming_notify_send_send_email'
        self.send_message(template=template)

    def action_reply_internal(self):
        name = 'default_incoming_transaction_id'
        return self.action_reply_tran(name, self)

    def action_forward_incoming(self):
        name = 'default_incoming_transaction_id'
        return self.action_forward_tran(name, self)

    def action_archive_incoming(self):
        name = 'default_incoming_transaction_id'
        return self.action_archive_tran(name, self)

    ####################################################
    # ORM Overrides methods
    ####################################################
    @api.model
    def create(self, vals):
        seq = self.fetch_sequence()
        if vals['preparation_id']:
            code = self.env['cm.entity'].browse(vals['preparation_id']).code
            x = seq.split('/')
            sequence = "%s/%s/%s" % (x[0], code, x[1])
            vals['name'] = sequence
        else:
            vals['name'] = seq
        vals['ean13'] = self.env['odex.barcode'].code128('IN', vals['name'], 'TR')
        return super(IncomingTransaction, self).create(vals)
    #
    # 
    # def unlink(self):
    #     if self.env.uid != 1:
    #         raise ValidationError(_("You can not delete transaction....."))
    #     return super(IncomingTransaction, self).unlink()
