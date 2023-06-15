#-*- coding: utf-8 -*-
import logging
import uuid
import requests
# from odoo import _, api, exceptions, fields, models
from odoo import models, api, fields,_
from odoo.exceptions import Warning,AccessError



_logger = logging.getLogger(__name__)


class EntityMatrix(models.Model):
    _name = 'cm.inter_entity'

    code = fields.Char(string='Code')
    name = fields.Char(string='Description')
    url = fields.Char(string='Server URL')
    uuid = fields.Char(string='Secret Key')
    
    @api.model
    def generate_key(self):
        key = uuid.uuid4()
        return str(key)

    @api.model
    def broadcast(self, key=None, url=None, new_key=None):
        if url.endswith('/'):
            url = u'{}{}'.format(url[:-1], '/cm/sync/broadcast')
        else:
            url = u'{}{}'.format(url, '/cm/sync/broadcast')
        code = new_key.split('-')[0]
        company_name = self.env.user.company_id.name
        new_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        new_url = new_url.replace('http://', 'http://')
        data = {
            'code': code,
            'name': company_name,
            'url': new_url,
            'key': new_key,
            'auth': key,
        }
        try:
            json = {
                'jsonrpc': '2.0',
                'method': 'call',
                'id': None,
                'params': data,
            }
            result = requests.post(url, json=json)
            r = result.json()
            if 'success' not in r.get('result', {}):
                _logger.error(r)
                return False
            entities = r.get('result', {}).get('entities', [])
            handle = []
            cm_entity = self.env['cm.entity'].sudo()
            for e in entities:
                ie = self.sudo().create(e)
                if len(e.get('entities', [])):
                    for ce in e.get('entities', []):
                        O = ce.copy()
                        O['inter_entity_id'] = ie.id
                        cm_entity.create(O)
                T = {
                    'name': ie.name,
                    'inter_entity_code': e['uuid'].split('-')[0],
                    'type': 'external',
                    'is_inter_entity': True,
                    'is_master_entity': True,
                    'inter_entity_id': ie.id,
                }
                cm_entity.with_context(broadcasted=True).create(T)
                handle.append((4, ie.id))
            if handle:
                sync = self.env['cm.inter_entity.sync'].sudo()
                setting = sync.search([], limit=1)
                setting.write({
                    'entities': handle,
                })

        except Exception as e:
            _logger.error(e)
            return False
        return True

    @api.model
    def add_new(self, arch):
        sync = self.env['cm.inter_entity.sync'].sudo()
        setting = sync.search([], limit=1)
        entities = self.sudo().get_entities()
        entity = self.sudo().create(arch)
        T = {
            'name': arch['name'],
            'inter_entity_code': arch['uuid'].split('-')[0],
            'type': 'external',
            'is_inter_entity': True,
            'is_master_entity': True,
            'inter_entity_id': entity.id,
        }
        self.env['cm.entity'].sudo().with_context(broadcasted=True).create(T)
        setting.write({
            'entities': [(4, entity.id)],
        })
        return entities
    
    @api.model
    def wrap_jsonrpc(self, data):
        return {
            'jsonrpc': '2.0',
            'method': 'call',
            'id': None,
            'params': data,
        }

    @api.model
    def post(self, url, data):
        result = requests.post(url, json=data)

        return result

    @api.model
    def is_success(self, result):
        r = result.json() or {}
        return 'success' in r.get('result', {})

    @api.model
    def get_settings(self):
        sync = self.env['cm.inter_entity.sync'].sudo()
        setting = sync.search([], limit=1)
        return setting

    @api.model
    def sync_new_key(self, key):
        sync = self.env['cm.inter_entity.sync'].sudo()
        setting = sync.search([], limit=1)
        SUBURL = u'/cm/sync/new_key'
        
        for e in setting.entities.filtered(lambda k: k.uuid != setting.sync_key):
            data = self.wrap_jsonrpc({
                'key': key,
                'old': setting.sync_key,
                'auth': e.uuid,
            })
            url = u'{}{}'.format(e.url, SUBURL)
            result = self.post(url, data)
            if not self.is_success(result):
                raise Warning(_('Sync Error'u'Cannot Syncronize new key to Server {}, URL "{}"').format(e.name, e.url))
        return True

    @api.model
    def update_from(self, server):
        setting = self.sudo().get_settings()
        SUBURL = u'/cm/sync/update_from'

        data = self.wrap_jsonrpc({
            'auth': server.uuid,
            'key': setting.sync_key,
        })
        url = u'{}{}'.format(server.url, SUBURL)
        result = self.post(url, data)
        if not self.is_success(result):
            raise Warning(_('Sync Error Cannot Syncronize new key to Server {}, URL "{}"').format(server.name, server.url))
        try:
            r = result.json()
            entities = r.get('result', {}).get('entities', [])
            handle = []
            cm_entity = self.env['cm.entity'].sudo()
            for e in entities:
                exists = setting.entities.filtered(lambda k: k.uuid == e['uuid'])
                if len(exists):
                    exists.write(e)
                    continue
                ie = self.sudo().create(e)
                if len(e.get('entities', [])):
                    for ce in e.get('entities', []):
                        O = ce.copy()
                        O['inter_entity_id'] = ie.id
                        cm_entity.create(O)
                try:
                    T = {
                        'name': ie.name,
                        'inter_entity_code': e['uuid'].split('-')[0],
                        'type': 'external',
                        'is_inter_entity': True,
                        'is_master_entity': True,
                        'inter_entity_id': ie.id,
                    }
                    cm_entity.with_context(broadcasted=True).create(T)
                except Exception as e:
                    _logger.error(e)
                handle.append((4, ie.id))
            if handle:
                sync = self.env['cm.inter_entity.sync'].sudo()
                setting = sync.search([], limit=1)
                setting.write({
                    'entities': handle,
                })
        except Exception as ee:
            _logger.error(ee)
            return False
        return True

    @api.model
    def send_transaction(self, trasaction, instance, to_send):
        setting = self.sudo().get_settings()
        SUBURL = u'/cm/sync/send_transaction'
        for e in to_send:
            # trasaction['to_ids'] = e.inter_entity_code
            from_id = False
            K = instance.employee_id
            K = K.parent_id
            if K.is_inter_entity:
                from_id = K
            # while True:
            #     if not len(K.parent_id):
            #         break
            #     K = K.parent_id
            #     if K.is_inter_entity:
            #         _logger.warning(
            #             '----ccxxxxxxxxxxxxxxxxxxxxcccccccccccccccccccccccccccccccccccccccccccccccccccccc---------sendtransaction %s',
            #             K.is_inter_entity)
            #         from_id = K
            #         break
            if from_id:
                trasaction['from_id'] = from_id.inter_entity_code
            else:
                trasaction['from_id'] = False
            data = self.wrap_jsonrpc({
                'data': trasaction,
                'key': setting.sync_key,
                'code': e.inter_entity_code,
                'auth': e.sudo().inter_entity_id.uuid,
            })
            url = u'{}{}'.format(e.sudo().inter_entity_id.url, SUBURL)
            result = self.post(url, data)
            # 'http://localhost:8069/cm/sync/send_transaction'
            if not self.is_success(result):
                _logger.error(result.json())
                raise Warning(_('Sync Error Cannot send Transaction to server {}').format(e.name))

    @api.model
    def sync(self, entities):
        raise NotImplementedError('Not NotImplemented !')

    @api.model
    def activate(self, arch):
        raise NotImplementedError('Not NotImplemented !')

    @api.model
    def push_new(self, vals):
        """here we have bug"""
        setting = self.sudo().get_settings()
        SUBURL = u'/cm/sync/push_new'
        for e in setting.entities.filtered(lambda k:
                                           k.uuid != setting.sync_key):
            data = self.wrap_jsonrpc({
                'data': vals,
                'auth': e.uuid,
            })
            url = u'{}{}'.format(e.url, SUBURL)
            result = self.post(url, data)
            if not self.is_success(result):
                raise Warning(_('Sync Error Cannot Syncronize new key to Server {}, URL "{}"').format(e.name, e.url))
        return True

    @api.model
    def clone(self, entity):
        raise NotImplementedError('Not NotImplemented !')
    
    @api.model
    def update(self, vals):
        setting = self.sudo().get_settings()
        if vals['key'] != setting.sync_key:
            if not vals.get('broadcasted', False) and not vals.get('dont_appear_in_send', False):
                e = AccessError(_('Access Error'))
                e.args = (
                    _('Access Error'), _('You cannot change syncronized entity data !'))
                raise e
            else:
                return True
        SUBURL = u'/cm/sync/update_entity'
        for e in setting.entities.filtered(lambda k:
            k.uuid != setting.sync_key):
            data = self.wrap_jsonrpc({
                'data': vals,
                'auth': e.uuid,
            })
            url = u'{}{}'.format(e.url, SUBURL)
            result = self.post(url, data)
            if not self.is_success(result):
                raise Warning(_('Sync Error Cannot Syncronize new key to Server {}, URL "{}"').format(e.name, e.url))
        return True

    @api.model
    def remove(self, vals):
        raise NotImplementedError('Not NotImplemented !')

    @api.model
    def get_cm_entities(self, e):
        entity = self.env['cm.entity'].sudo()
        entities = entity.search(
            [('is_inter_entity', '=', True), ('inter_entity_id', '=', e.id)])
        result = []
        for ce in entities:
            result.append({
                'inter_entity_code': ce.inter_entity_code,
                'name': ce.name,
                'code': ce.code,
                'type': 'external',
                'is_inter_entity': True,
            })
        return result

    @api.model
    def get_entities(self):
        sync = self.env['cm.inter_entity.sync'].sudo()
        setting = sync.search([], limit=1)
        data = []
        for e in setting.entities:
            if e.id == setting.server_id.id:
                cm_entities = self.sudo().get_cm_entities(e)
                data.append({
                    'name': e.name,
                    'code': e.code,
                    'uuid': e.uuid,
                    'url': e.url,
                    'entities': cm_entities,
                })
        return data

    @api.model
    def authenticate(self, key):
        # add by Fatima 7/5/2020 for clean older code
        """to check key of entity before sync using in controller method receive key and return true if right key"""
        sync = self.env['cm.inter_entity.sync'].sudo()
        setting = sync.search([], limit=1)
        try:
            if setting.sync_key == key.strip():
                return True
        except Exception as e:
            return False
        return False


class Entity(models.Model):
    _inherit = 'cm.entity'

    inter_entity_id = fields.Many2one('cm.inter_entity', string='Inter-Entities Ref')
    inter_entity_code = fields.Char(
        string='Inter-Entities Code')
    is_inter_entity = fields.Boolean(string='Is Inter-Entity ?', help='''
        If checked, this entity will be syncronized by other entities in the group.
    ''')
    is_master_entity = fields.Boolean(string='Is Master-Entity ?', help='''
        If checked, this entity will be syncronized by other entities in the group.
    ''')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if not (name == '' and operator == 'ilike'):
            search = self.env['cm.inter_entity'].sudo().search([('name', 'ilike', name)])
            if len(search):
                args += ['|', ('inter_entity_id', 'in', search.ids)]
        return super(Entity, self).name_search(name=name, args=args, operator=operator, limit=limit)

    def name_get(self):
        result = []
        for r in self:
            if r.is_inter_entity:
                if r.type == 'external':
                    result.append((r.id, u'{} \u21E6 {}'.format(
                        r.inter_entity_id.name or u'**', r.name)))
                    continue
            result.append((r.id, r.name))
        return result

    @api.model
    def create(self, vals):
        setting = self.env['cm.inter_entity'].sudo().get_settings()
        if vals.get('type', False) == 'unit' and vals.get('is_inter_entity', False):
            if not vals.get('inter_entity_code', False):
                vals['inter_entity_id'] = setting.server_id.id
                vals['inter_entity_code'] = u'{}-{}'.format(setting.sync_key.split('-')[0] if setting.sync_key else False,
                                                            self.env['ir.sequence'].sudo().next_by_code('cm.inter.entity'))
        obj = super(Entity, self).create(vals)
        IE = self.env['cm.inter_entity'].sudo()
        if vals.get('type', False) == 'unit' and vals.get('is_inter_entity', False):
            if not self.env.context.get('broadcasted', False):
                IE.push_new({
                    'data': vals,
                    'key': setting.sync_key,
                })
        return obj

    # def unlink(self, cr, uid, ids, context=None):
    #     return super(Entity, self).unlink(cr, uid, ids, context=context)

    def write(self, vals):
        data = {}
        values = vals.copy()
        is_inter_entity = False
        setting = self.env['cm.inter_entity'].sudo().get_settings()
        if vals.get('is_inter_entity', False):
            values['inter_entity_id'] = setting.server_id.id
            values['inter_entity_code'] = u'{}-{}'.format(setting.sync_key.split(
                '-')[0], self.env['ir.sequence'].sudo().next_by_code('cm.inter.entity'))
            vals['inter_entity_id'] = values['inter_entity_id']
            vals['inter_entity_code'] = values['inter_entity_code']
            is_inter_entity = True
        for r in self:
            if r.is_inter_entity:
                data = {
                    'details': {'code': r.inter_entity_code, 'data': vals},
                    'key': r.inter_entity_id.uuid,
                    'broadcasted': vals.get('broadcasted', False)
                }
                if not is_inter_entity:
                    data['details']['remove'] = True
            elif is_inter_entity:
                vals1 = r.read([])
                vals1 = vals1[0]
                lister = [
                    'name', 'inter_entity_code',
                    'is_inter_entity',
                ]
                vals2, vals3 = {}, {}
                for l in lister:
                    if l in vals1:
                        vals2[l] = vals1[l]
                    if l in vals:
                        vals3[l] = vals[l]
                vals2.update(vals3)
                if vals2:
                    code = vals2.get('inter_entity_code', r.inter_entity_code)
                    data = {
                        'details': {'code': code, 'data': vals2, 'is_new': True},
                        'key': setting.sync_key,
                        'broadcasted': vals.get('broadcasted', False)
                    }
        u = super(Entity, self).write(values)
        if data:
            IE = self.env['cm.inter_entity'].sudo()
            IE.update(data)
        return u
