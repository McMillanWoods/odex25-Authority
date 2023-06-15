#-*- coding: utf-8 -*-
'''Doc'''
import logging
from odoo import api, models, fields, _


_logger = logging.getLogger(__name__)


class Sync(models.Model):
    '''Doc'''
    _name = 'cm.inter_entity.sync'
    _description = 'Entity Syncronization'

    activated = fields.Boolean(string='Activate Syncronization')
    sync_key = fields.Char(string='Sync Key', related='server_id.uuid')
    server_id = fields.Many2one('cm.inter_entity', string='Current Server', store=True)
    entities = fields.Many2many(
        'cm.inter_entity', 'inter_entity_sync_rel', 'sync_id', 'inter_entity_id')
    
    important_id = fields.Many2one(
        'cm.transaction.important', string='Default Important Degree')
    subject_type_id = fields.Many2one(
        'cm.subject.type', string='Default Transaction Type')
    employee_id = fields.Many2one(
        'cm.entity', string='Default Created By')

    def generate_key(self):
        '''Doc'''
        inter_entity = self.env['cm.inter_entity'].sudo()
        for rec in self:
            # if not len(rec.entities.filtered(lambda k: k.uuid != rec.sync_key)):
                # first time
            return {
                'name': _('Generate new Key'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': False,
                'res_model': 'cm.inter.entity.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {
                    'default_document_id': rec.id,
                    'default_broadcast': True,
                },
            }
            # k = inter_entity.generate_key()
            # synced = inter_entity.sync_new_key(k)
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>synced",synced)
            # if synced:
            #     rec.write({
            #         'sync_key': k,
            #     })

    def update_from(self):
        '''Doc'''
        inter_entity = self.env['cm.inter_entity'].sudo()
        for rec in self:
            if len(rec.entities.filtered(lambda k: k.uuid != rec.sync_key)):
                # first time
                return {
                    'name': _('Update From ...'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': False,
                    'res_model': 'cm.inter.entity.update.wizard',
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_document_id': rec.id,
                        'default_broadcast': True,
                    },
                }
            k = inter_entity.generate_key()
            synced = inter_entity.sync_new_key(k)
            if synced:
                rec.write({
                    'sync_key': k,
                })
