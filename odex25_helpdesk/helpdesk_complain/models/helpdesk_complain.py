
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import datetime
_logger = logging.getLogger(__name__)


class HelpdeskComplain(models.Model):
    _name = "helpdesk.complain"

    name = fields.Text("Description")
    helpdesk_id = fields.Many2one('odex25_helpdesk.ticket',"Ticket")
    date = fields.Datetime(default=datetime.datetime.now())
    customer_id = fields.Many2one('res.partner',related="helpdesk_id.partner_id")
    user_id = fields.Many2one('res.users',related="helpdesk_id.user_id")
    is_submitted = fields.Boolean(default=False)

    def submit_to_user(self):
        """
            set the flag to true so fields be readonly and go to next stage
        """
        for rec in self:
            rec.is_submitted = True
    # date = fields.DateTime()


class HelpdeskTicket(models.Model):
    _inherit = 'odex25_helpdesk.ticket'

    complains = fields.Integer(compute='_compute_complains')
    complain_ids = fields.One2many('helpdesk.complain','helpdesk_id')

    def _compute_complains(self):
        """
            number of complains associated with the ticket
        """
        complains = self.env['helpdesk.complain'].search_count([('helpdesk_id','=',self.id)])
        self.complains = complains
    
    def open_complains(self):
        """
            this is returning an action to all complains domained by this ticket 
        """
        action = {
            'name': _('Complains'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.complain',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context':{
                'default_helpdesk_id':self.id,
            },
            'domain': [('helpdesk_id', '=', self.id)],
        }
        return action


class autoattach_mail(models.Model):
    _inherit='mail.template'

    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False):
        """ Generates a new mail.mail. Template is rendered on record given by
        res_id and model coming from template.

        :param int res_id: id of the record to render the template
        :param bool force_send: send email immediately; otherwise use the mail
            queue (recommended);
        :param dict email_values: update generated mail with those values to further
            customize the mail;
        :param str notif_layout: optional notification layout to encapsulate the
            generated email;
        :returns: id of the mail.mail that was created """

        # Grant access to send_mail only if access to related document
        self.ensure_one()
        self._send_check_access([res_id])

        Attachment = self.env['ir.attachment']  # TDE FIXME: should remove default_type from context

        # create a mail_mail based on values, without attachments
        values = self.generate_email(res_id,
                                     ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc',
                                      'reply_to', 'scheduled_date'])
        values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
        values['attachment_ids'] = [(4, aid) for aid in values.get('attachment_ids', list())]
        values.update(email_values or {})
        attachment_ids = values.pop('attachment_ids', [])
        attachments = values.pop('attachments', [])
        # add a protection against void email_from
        if 'email_from' in values and not values.get('email_from'):
            values.pop('email_from')
        # encapsulate body
        if notif_layout and values['body_html']:
            try:
                template = self.env.ref(notif_layout, raise_if_not_found=True)
            except ValueError:
                _logger.warning('QWeb template %s not found when sending template %s. Sending without layouting.' % (
                notif_layout, self.name))
            else:
                record = self.env[self.model].browse(res_id)
                model = self.env['ir.model']._get(record._name)

                if self.lang:
                    lang = self._render_lang([res_id])[res_id]
                    template = template.with_context(lang=lang)
                    model = model.with_context(lang=lang)

                template_ctx = {
                    'message': self.env['mail.message'].sudo().new(
                        dict(body=values['body_html'], record_name=record.display_name)),
                    'model_description': model.display_name,
                    'company': 'company_id' in record and record['company_id'] or self.env.company,
                    'record': record,
                }
                body = template._render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                values['body_html'] = self.env['mail.render.mixin']._replace_local_links(body)
        mail = self.env['mail.mail'].sudo().create(values)

        # manage attachments
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas': attachment[1],
                'type': 'binary',
                'res_model': 'mail.message',
                'res_id': mail.mail_message_id.id,
            }
            attachment_ids.append((4, Attachment.create(attachment_data).id))
        if attachment_ids:
            mail.write({'attachment_ids': attachment_ids})

        if force_send:
            mail.send(raise_exception=raise_exception)
        return mail.id  # TDE CLEANME: return mail + api.returns ?

    # def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
    #     """Generates a new mail message for the given template and record,
    #        and schedules it for delivery through the ``mail`` module's scheduler.
    #
    #        :param int res_id: id of the record to render the template with
    #                           (model is taken from the template)
    #        :param bool force_send: if True, the generated mail.message is
    #             immediately sent after being created, as if the scheduler
    #             was executed for this message only.
    #        :param dict email_values: if set, the generated mail.message is
    #             updated with given values dict
    #        :returns: id of the mail.message that was created
    #     """
    #     self.ensure_one()
    #     Mail = self.env['mail.mail']
    #     Attachment = self.env['ir.attachment']  # TDE FIXME: should remove default_type from context
    #
    #     # create a mail_mail based on values, without attachments
    #     values = self.generate_email(res_id)
    #     if self._context.get('recipient_ids'):
    #         values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
    #     else:
    #         values['recipient_ids'] = False
    #     values.update(email_values or {})
    #     attachment_ids = values.pop('attachment_ids', [])
    #     attachments = values.pop('attachments', [])
    #     # add a protection against void email_from
    #     if 'email_from' in values and not values.get('email_from'):
    #         values.pop('email_from')
    #     mail = Mail.create(values)
    #
    #     # manage attachments
    #     for attachment in attachments:
    #         attachment_data = {
    #             'name': attachment[0],
    #             'datas_fname': attachment[0],
    #             'datas': attachment[1],
    #             'type': 'binary',
    #             'res_model': 'mail.message',
    #             'res_id': mail.mail_message_id.id,
    #         }
    #         attachment_ids.append(Attachment.create(attachment_data).id)
    #     if attachment_ids:
    #         values['attachment_ids'] = [(6, 0, attachment_ids)]
    #         mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
    #
    #     if force_send:
    #         mail.send(raise_exception=raise_exception)
    #     return mail.id  # TDE CLEANME: return mail + api.returns ?
