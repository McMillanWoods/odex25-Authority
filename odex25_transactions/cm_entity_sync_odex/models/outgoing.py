#-*- coding: utf-8 -*-

import logging
import base64
from odoo import api, models, fields, _, exceptions


_logger = logging.getLogger(__name__)


class Transaction(models.Model):
    _inherit = 'outgoing.transaction'

    syncronized = fields.Boolean(string='Syncronized ?')
    

    def action_draft(self):
        super(Transaction, self).action_draft()
        to_send = []
        inter_entity = self.env['cm.inter_entity'].sudo()
        for r in self:
            r.write({
                'syncronized': True,
            })
            for e in r.to_ids:
                if e.is_inter_entity:
                    to_send.append(e)
            attachment_rule_data = []
            for attachment in r.attachment_rule_ids:
                attachment_rule_data.append({
                'id': attachment.id if attachment else '',
                'file_save': attachment.file_save.decode('utf-8') if attachment.file_save else '',
                'attachment_filename': u"".join(u'%s'%attachment.attachment_filename) if attachment.attachment_filename else '',
                'outgoing_id': False,
                'incoming_transaction_id': r.id if r else False,
                'internal_id': False,
                'date': attachment.date if attachment.date else '',
                'description': attachment.description if attachment.description else '',
                })
            if len(to_send):
                trasaction = {
                    # 'out_date': r.out_date,
                    'to_ids': None,
                    'type': 'new',
                    'subject': r.subject,
                    'incoming_number': r.name,
                    'incoming_date': r.transaction_date,
                    'syncronized': True,
                    'body': r.body,
                    'attachment_rule_ids': attachment_rule_data,
                }
                inter_entity.send_transaction(trasaction, r, to_send)


class Incoming(models.Model):
    _inherit = 'incoming.transaction'

    syncronized = fields.Boolean(string='Syncronized ?')
    inter_entity_id = fields.Many2one('cm.inter_entity', string='Inter Entity')

