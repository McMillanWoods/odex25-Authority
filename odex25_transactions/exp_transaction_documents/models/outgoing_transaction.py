# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class OutgoingTransaction(models.Model):
    _name = 'outgoing.transaction'
    _inherit = ['transaction.transaction', 'mail.thread']
    _description = 'outgoing Transaction'

    reason = fields.Text('Reason')
    attachment_rule_ids = fields.One2many('cm.attachment.rule', 'outgoing_transaction_id', string='Attaches')
    attachment_ids = fields.One2many('cm.attachment', 'outgoing_transaction_id', string='Attachments')
    trace_ids = fields.One2many('cm.transaction.trace', 'outgoing_transaction_id', string='Trace Log')
    is_partner = fields.Boolean()
    partner_id = fields.Many2one('res.partner')
    incoming_transaction_id = fields.Many2one('incoming.transaction', string='Related Incoming')
    to_ids = fields.Many2many(comodel_name='cm.entity', relation='outgoing_entity_rel', column1='outgoing_id'
                              , column2='entity_id', string='Send To')
    tran_tag = fields.Many2many(comodel_name='transaction.tag', string='Tags')
    tran_tag_unit = fields.Many2many(comodel_name='transaction.tag', string='Business unit',
                                     relation='outgoing_tag_rel',
                                     column1='incoming_id'
                                     , column2='name')
    project_id = fields.Many2many('project.project')
    sale_order_id = fields.Many2one('sale.order', 'Proposal')
    to_name = fields.Char(string="Recipient")
    cc_ids = fields.Many2many(comodel_name='cm.entity', relation='outgoing_entity_cc_rel',
                              column1='outgoing_id', column2='entity_id', string='CC To')
    processing_ids = fields.Many2many(comodel_name='outgoing.transaction', relation='transaction_outgoing_outgoing_rel',
                                      column1='transaction_id', column2='outgoing_id',
                                      string='Process Transactions outgoing')
    processing2_ids = fields.Many2many(comodel_name='incoming.transaction',
                                       relation='transaction_outgoing_incoming_rel',
                                       column1='transaction_id', column2='incoming_id',
                                       string='Process Transactions incoming')

    # processing_ids = fields.Many2many(comodel_name='transaction.transaction', relation='transaction_outgoing_rel',
    #                                   column1='transaction_id', column2='outgoing_id', string='Process Transactions')

    @api.depends('attachment_rule_ids')
    def compute_attachment_num(self):
        for r in self:
            r.attachment_num = len(r.attachment_rule_ids)

    @api.model
    def get_url(self):
        url = u''
        action = self.env.ref(
            'exp_transaction_documents.outgoing_external_tran_action', False)
        Param = self.env['ir.config_parameter'].sudo()
        if action:
            return u'{}/web#id={}&action={}&model=outgoing.transaction'.format(
                Param.get_param('web.base.url', self.env.user.company_id.website), self.id, action.id)
        return url

    def fetch_sequence(self, data=None):
        """generate transaction sequence"""
        return self.env['ir.sequence'].next_by_code('cm.transaction.out') or _('New')

    ####################################################
    # Business methods
    ####################################################
    #

    def action_draft(self):
        for record in self:
            """her i need to review code for to_ids"""
            # res = super(OutgoingTransaction, self).action_draft()
            if record.subject_type_id.transaction_need_approve or record.preparation_id.need_approve:
                if self.user_has_groups('exp_transaction_documents.group_cm_unit_manager'):
                    record.action_send()
                else:
                    record.state = 'complete'
            else:
                record.state = 'complete'
            # record.trace_create_ids('outgoing_transaction_id', record, 'sent')
            partner_ids = [record.preparation_id.manager_id.user_id.partner_id.id]
            subj = _('Message Has been send !')
            msg = _(u'{} &larr; {}').format(record.employee_id.name, u' / '.join([k.name for k in record.to_ids]))
            msg = u'{}<br /><b>{}</b> {}.<br />{}'.format(msg,
                                                          _(u'Action Taken'), record.procedure_id.name,
                                                          u'<a href="%s" >رابط المعاملة</a> ' % (
                                                              record.get_url()))
            self.action_send_notification(subj, msg, partner_ids)
            # return res

    def action_email(self):
        # todo#add email function here
        company_id = self.env.user.company_id
        if company_id.sms_active == True:
            test = company_id.send_sms("", "Test from odex!")
            test = test.text[:100].split("-")
            error = company_id.get_error_response(test[1])
            print(error)
        for rec in self:
            templates = 'exp_transaction_documents.out_email'
            template = self.env.ref(templates, False)
            emails = rec.partner_id.email if rec.is_partner else rec.to_ids.mapped('email')
            print(emails)
            email_template = template.write(
                {'email_to': emails})
            print(email_template)
            # template.with_context(lang=self.env.user.lang).send_mail(
            #     transaction.id, force_send=True, raise_exception=False)

    def action_reject_outgoing(self):
        name = 'default_outgoing_transaction_id'
        return self.action_reject(name, self)

    def action_return_outgoing(self):
        name = 'default_outgoing_transaction_id'
        return self.action_return_tran(name, self)

    ####################################################
    # ORM Overrides methods
    ####################################################
    @api.model
    def create(self, vals):
        seq = self.fetch_sequence()
        if vals.get('preparation_id'):
            code = self.env['cm.entity'].sudo().browse(vals['preparation_id']).code
            x = seq.split('/')
            sequence = "%s/%s/%s" % (x[0], code, x[1])
            vals['name'] = sequence
        else:
            vals['name'] = seq
        # vals['ean13'] = self.env['odex.barcode'].code128('OT', vals['name'], 'TR')
        return super(OutgoingTransaction, self).create(vals)

    # 
    # def unlink(self):
    #     if self.env.uid != 1:
    #         raise ValidationError(_("You can not delete transaction....."))
    #     return super(OutgoingTransaction, self).unlink()
