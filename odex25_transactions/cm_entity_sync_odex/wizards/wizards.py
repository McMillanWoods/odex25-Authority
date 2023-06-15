# -*- coding: utf-8 -*-
from odoo import api, models, fields, _, exceptions

import logging

_logger = logging.getLogger(__name__)


class AddNew(models.TransientModel):
    _name = 'cm.inter.entity.wizard'

    document_id = fields.Many2one('cm.inter_entity.sync', string='Document')
    broadcast = fields.Boolean(string='Broadcast')
    key = fields.Char(string='Sync Key')
    server_url = fields.Char('Server URL')
    server_key = fields.Char(string='Server Key')

    def generate(self):
        inter_entity = self.env['cm.inter_entity'].sudo()
        for rec in self:
            K = inter_entity.generate_key()
            rec.key = K
            company_code = K.split('-')[0]
            company_name = self.env.user.company_id.name
            company_url = self.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url')
            # company_url = company_url.replace('http://', 'https://')
            synced = inter_entity.sync_new_key(K)
            if synced:
                rec.document_id.write({
                    'sync_key': K,
                })
            if rec.broadcast:
                url = rec.server_url
                key = rec.server_key
                added = inter_entity.broadcast(url=url, key=key, new_key=K)
                if not added:
                    raise exceptions.Warning(_('Broadcast Error !'
                                               u'Error While Broadcast new Server, please check server key and url.'))
            data = {
                'name': company_name,
                'code': company_code,
                'url': company_url,
                'uuid': K,
            }
            if len(rec.document_id.server_id):
                rec.document_id.server_id.write({
                    'uuid': K,
                    'code': company_code,
                    'name': company_name,
                    'url': company_url,
                })
            else:
                entity = inter_entity.create(data)
                rec.document_id.write({
                    'server_id': entity.id,
                    'entities': [(4, entity.id)]
                })


class Update(models.TransientModel):
    _name = 'cm.inter.entity.update.wizard'

    document_id = fields.Many2one('cm.inter_entity.sync', string='Document')
    primary_id = fields.Many2one('cm.inter_entity', string='Main Server', related='document_id.server_id', store=True)
    server_id = fields.Many2one('cm.inter_entity', string='Update Server')

    def update(self):
        for r in self:

            setting = r.document_id
            r.primary_id.sudo().update_from(r.server_id)
