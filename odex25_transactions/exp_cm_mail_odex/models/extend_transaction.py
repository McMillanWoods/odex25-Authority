#-*- coding: utf-8 -*-
from odoo import api, models, fields,_
from email import utils


class Transaction(models.Model):
    _inherit = 'transaction.transaction'

    source = fields.Selection(string='Transaction Source', selection=[
        ('manual', _('Manual')),
        ('email', _('Email')),
        ('auto', _('System')),
    ], default='manual')

    @api.returns('cm.entity')
    def get_entity_by_email(self, emailaddr):
        """
        return cm.entity using email address

        :param emailaddr: entity email

        :return: cm.entity: object
        """
        Entity = self.env['cm.entity']
        Partner = self.env['res.partner']
        User = self.env['res.users']
        email = utils.parseaddr(emailaddr)[1]
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>email",email)
        partners = Partner.search([('email', '=ilike', email)])
        # return first entity in this range
        if not len(partners):
            return Entity  # empty entity
        users = User.search([('partner_id', 'in', partners.ids)])
        entities = Entity.search([('partner_id', 'in', partners.ids)])
        if not len(entities) and len(users):
            entities = Entity.search([('user_id', 'in', users.ids)])
        return len(entities) and entities[0] or Entity


class IncomingTransaction(models.Model):
    _inherit = 'internal.transaction'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """
        Overrides mail_thread message_new that is called by the mailgateway through message_process.
        This override updates the document according to the email.

        :param msg_dict: a map containing the email details and
        attachments. See ``message_process`` and
        ``mail.message.parse`` for details.

        :param custom_values: optional dictionary of additional
        field values to pass to create()
        when creating the new thread record.
        Be careful, these values may override
        any other values coming from the message.

        :return: the id of the newly created thread object
        """
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>hello iam custom")
        context = self.env.context
        data = {}
        if isinstance(custom_values, dict):
            data = custom_values.copy()
        model = context.get('thread_model') or self._name
        model_pool = self.env[model]
        fields = model_pool.with_context(**context).fields_get()
        if 'subject' in fields and not data.get('name'):
            data['subject'] = msg_dict.get('subject', '')
        if 'body' in fields and not data.get('name'):
            data['body'] = msg_dict.get('body', '')
        email_from = msg_dict.get('email_from', '')
        if email_from:
            entity = self.get_entity_by_email(email_from)
            if len(entity):
                # data['to_ids'] = [(4, entity.id)]
                data['employee_id'] = entity.id
                data['state'] = 'draft'
        data['source'] = 'email'
        res_id = model_pool.with_context(**context).create(data)
        res_id.fetch_sequence(data={}, now=True)
        return res_id.id
