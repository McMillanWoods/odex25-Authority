#-*- coding: utf-8 -*-
import logging
import datetime
import base64
from odoo import http
from odoo.http import request
from odoo import models, api, fields, _,exceptions,SUPERUSER_ID


_logger = logging.getLogger(__name__)


class Sync(http.Controller):
    @http.route('/cm/sync/broadcast', type='json', auth='public', methods=['POST'])
    def add_new(self, **kw):
        keys = [
            'url',
            'name',
            'code',
            'key',
            'auth',
        ]
        for k in keys:
            if not kw.get(k, False):
                return {
                    'error': 'Bad Request 1',
                }
        inter_entity = request.env['cm.inter_entity'].sudo()
        if not inter_entity.authenticate(kw.get('auth', '')):
            return {
                'error': 'Bad Request 2',
                'req': kw,
            }
        data = {
            'url': kw.get('url', ''),
            'name': kw.get('name', ''),
            'code': kw.get('code', ''),
            'uuid': kw.get('key', ''),
        }
        entities = inter_entity.add_new(data)
        return {
            'success': True,
            'entities': entities,
        }

    @http.route('/cm/sync/update_from', type='json', auth='public', methods=['POST'])
    def update_from(self, **kw):
        keys = [
            'key',
            'auth',
        ]
        for k in keys:
            if not kw.get(k, False):
                return {
                    'error': 'Bad Request 1',
                }
        inter_entity = request.env['cm.inter_entity'].sudo()
        if not inter_entity.authenticate(kw.get('auth', '')):
            return {
                'error': 'Bad Request 2',
                'req': kw,
            }
        return {
            'success': True,
            'entities': inter_entity.get_entities()
        }
        data = {
            'url': kw.get('url', ''),
            'name': kw.get('name', ''),
            'code': kw.get('code', ''),
            'uuid': kw.get('key', ''),
        }
        entities = inter_entity.add_new(data)
        return {
            'success': True,
            'entities': entities,
        }

    @http.route('/cm/sync/new_key', type='json', auth='public', methods=['POST'])
    def new_key(self, **kw):
        keys = [
            'old',
            'key',
            'auth',
        ]
        for k in keys:
            if not kw.get(k, False):
                return {
                    'error': 'Bad Request 1',
                }
        inter_entity = request.env['cm.inter_entity'].sudo()
        if not inter_entity.authenticate(kw.get('auth', '')):
            return {
                'error': 'Bad Request 2',
            }
        old = inter_entity.search([('uuid', '=', kw.get('old'))], limit=1)
        if len(old):
            data = {
                'uuid': kw.get('key'),
                'code': kw.get('key').split('-')[0],
            }
            old.write(data)
        return {
            'success': True,
        }

    @http.route('/cm/sync/update_entity', type='json', auth='public', methods=['POST'])
    def update_entity(self, **kw):
        keys = [
            'data',
            'auth',
        ]
        for k in keys:
            if not kw.get(k, False):
                return {
                    'error': 'Bad Request 1',
                }
        inter_entity = request.env['cm.inter_entity'].sudo()
        inter_entity_set = request.env['cm.inter_entity.sync'].sudo()
        if not inter_entity.authenticate(kw.get('auth', '')):
            return {
                'error': 'Bad Request 2',
            }
        data = kw['data']
        key = data['key']
        entity = inter_entity.search([('uuid', '=', key)], limit=1)
        ecode = data['details']['code']
        is_new = data['details'].get('is_new', False)
        if len(entity):
            en = request.env['cm.entity'].sudo().search(
                [('inter_entity_code', '=', ecode), ('inter_entity_id', '=', entity.id)])
            if len(en):
                d = data['details']['data']
                d['broadcasted'] = True
                en.write(d)
            elif is_new:
                d = data['details']['data']
                dd = {
                    'name': d.get('name', ''),
                    # 'code': d.get('code', ''),
                    'type': 'external',
                    'is_inter_entity': True,
                    'inter_entity_code': d.get('inter_entity_code', ''),
                    'inter_entity_id': entity.id,
                }
                request.env['cm.entity'].sudo().create(dd)
        else:
            return {
                'error': 'No Record'
            }
        return {
            'success': True,
        }

    @http.route('/cm/sync/push_new', type='json', auth='public', methods=['POST'])
    def push_new(self, **kw):
        keys = [
            'data',
            'auth',
        ]
        for k in keys:
            if not kw.get(k, False):
                return {
                    'error': 'Bad Request 1',
                }
        inter_entity = request.env['cm.inter_entity'].sudo()
        if not inter_entity.authenticate(kw.get('auth', '')):
            return {
                'error': 'Bad Request 2',
            }
        data = kw['data']
        key = data['key']
        entity = inter_entity.search([('uuid', '=', key)], limit=1)

        if len(entity):

            d = data['data']
            dd = {
                'name': d.get('name', ''),
                # 'code': d.get('code', ''),
                'type': 'external',
                'is_inter_entity': True,
                'inter_entity_code': d.get('inter_entity_code', ''),
                'inter_entity_id': entity.id,
            }
            try:
                request.env['cm.entity'].sudo().with_context(
                    broacasted=True).create(dd)
                return {
                    'success': True,
                }
            except Exception as e:
                return {
                    'error': 'No Record'
                }
        else:
            return {
                'error': 'No Record'
            }
        return {
            'success': True,
        }

    @http.route('/cm/sync/send_transaction', type='json', auth='public', methods=['POST'])
    def send_transaction(self, **kw):
        keys = [
            'data',
            'code',
            'key',
            'auth',
        ]
        for k in keys:
            if not kw.get(k, False):
                return {
                    'error': 'Bad Request 1',
                }
        inter_entity = request.env['cm.inter_entity'].sudo()
        Entity = request.env['cm.entity'].sudo()
        if not inter_entity.authenticate(kw.get('auth', '')):
            return {
                'error': 'Bad Request 2',
            }
        data = kw['data']
        code = kw['code']
        key = kw['key']
        auth = kw['auth']
        from_id = data['from_id']
        ie = inter_entity.search([('uuid', '=', auth)], limit=1)
        extie = inter_entity.search([('uuid', '=', key)], limit=1)
        setting = inter_entity.get_settings()
        if not len(ie) or not len(extie):
            return {
                'error': 'No Record 1'
            }
        if not from_id:
            from_id = Entity.search([('is_master_entity', '=', True),
                                     ('type', '=', 'external'), ('inter_entity_id', '=', extie.id)], limit=1)
            if not len(from_id):
                return {
                    'error': 'No Record 2'
                }
        else:
            from_id = Entity.search([('inter_entity_code', '=', from_id), (
                  'type', '=', 'external'), ('inter_entity_id', '=', extie.id)], limit=1)
            if not len(from_id):
                return {
                    'error': 'No Record 3'
                }
        entity = Entity.search([('inter_entity_code', '=', code),('type', '=', 'unit')], limit=1)
        if len(entity) > 0 and len(from_id) > 0:
            Incoming = request.env['incoming.transaction'].sudo()
            d = data
            d['from_id'] = from_id.id
            d['inter_entity_id'] = extie.id
            d['important_id'] = setting.important_id.id
            d['subject_type_id'] = setting.subject_type_id.id
            if len(entity.secretary_id):
                d['employee_id'] = entity.secretary_id.id
                d['preparation_id'] = entity.id
            else:
                d['employee_id'] = setting.employee_id.id
                d['preparation_id'] = setting.id
            d['to_ids'] = [(4, entity.id), ]
            # if entity.body:
            #    d['body'] = entity.body
            d['due_date'] = fields.date.today()
            attachment_rule_ids = d.get('attachment_rule_ids')
            d.pop('attachment_rule_ids')
            inc = Incoming.create(d)
            for attachment in attachment_rule_ids:
                attachement_rule = request.env['cm.attachment.rule'].sudo().create({
                    'employee_id': entity.secretary_id.id if len(entity.secretary_id) else setting.employee_id.id,
                    'entity_id': entity.id,
                    'file_save': attachment['file_save'],
                    'attachment_filename': attachment['attachment_filename'],
                    'incoming_transaction_id': inc.id if inc.id else False,
                    'date': attachment['date'],
                    'description': attachment['description'],
                })
                attachment_data = {
                    'name': attachment['attachment_filename'],
                    'datas_fname': attachment['attachment_filename'],
                    'datas': attachment['file_save'],
                    'res_model': 'cm.attachment.rule',
                    'res_id': attachement_rule.id,
                }
                request.env['ir.attachment'].sudo().create(attachment_data)
            inc.preparation_id = inc.entity_id
            #     notification system and mailing
            employee = inc.from_id
            subj = _('Message Has been send !')
            msg = _(u'{} &larr; {}.{}').format(employee and employee.name or '#',
                                               u' / '.join([k.name for k in inc.to_ids]),
                                               u'<a href="%s" >رابط المعاملة</a> ' % (inc.get_url()))
            partner_ids = []
            for partner in inc.to_ids:
                if partner.type == 'unit':
                    partner_ids.append(partner.secretary_id.user_id.partner_id.id)
                elif partner.type == 'employee':
                    partner_ids.append(partner.user_id.partner_id.id)
            # thread_obj = request.env['mail.thread']
            # thread_obj.message_post(type="notification", subject=subj, body=msg,
            #                                      partner_ids=partner_ids,
            #                                      subtype="mail.mt_comment")
            # inc.send_message(template='exp_transaction_documents.incoming_notify_send_send_email')
        else:
            return {
                'error': 'No Record 4'
            }
        return {
            'success': True,
        }