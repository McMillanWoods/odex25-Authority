# -*- coding: utf-8 -*-
import collections
import datetime

from odoo import api, fields, models,_
# from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ForwardTransactionReportWizard(models.TransientModel):
    _name = 'forward.transaction.report.wizard'
    _inherit = "transaction.common.report"
    _description = 'Print Forward Transaction Report'

    
    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'type': self.type,
                'type_transact': self.type_transact,
                'entity_ids': self.entity_ids.ids,
                'start_date': self.start_date,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('exp_transaction_report.forward_transaction_complete_report').report_action(self, data=data)


class ReportForwardTransaction(models.AbstractModel):
    _name = 'report.exp_transaction_report.template_forw_transaction_report'

    def set_docs_dic(self, transaction, name, flag, unit, type):
        unit_name = unit.name
        if type == 'unit':
            unit_name = unit.parent_id.name
        # rec = transaction.trace_ids.filtered(lambda z: z.action == 'archive')[0]
        lang = self.env.user.lang
        trans = ''
        if name == 'Internal':
            trans = transaction.internal_transaction_id
        if name == 'Incoming':
            trans = transaction.incoming_transaction_id
        date = transaction.date
        if flag == 'pdf':
            date = datetime.datetime.strptime(str(transaction.date), '%Y-%m-%d %H:%M:%S').date()
        if lang == 'ar_SY' and name == 'Internal':
            name = 'داخلية'
        elif lang == 'ar_SY' and name == 'Incoming':
            name = 'واردة'
        dic = {
            'classification': name,
            'name': trans.name,
            'subject': trans.subject,
            'type': trans.subject_type_id.name,
            'transaction_date': trans.transaction_date,
            'action': transaction.procedure_id.name,
            'date': date,
            'form': unit.name,
            'note': transaction.note,
            'unit': unit_name,
        }
        return dic

    def get_value(self, data, flag):
        type = data['form']['type']
        type_transact = data['form']['type_transact']
        entity_ids = data['form']['entity_ids']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        docs = []
        x = False
        domain = []
        if type == 'unit':
            emp_ids = self.env['cm.entity'].search([('parent_id', 'in', entity_ids), ('type', '=', 'employee')]).ids
            domain.append(('from_id', 'in', emp_ids))
        elif type == 'employee':
            domain.append(('from_id', 'in', entity_ids))
        domain.extend((('action', 'in', ['forward', 'reply']), ('date', '>=', start_date),
                       ('date', '<=', end_date)))
        if type_transact == 'internal':
            x = self.env['cm.transaction.trace'].search(domain, order="date desc")
            if x:
                for rec in x:
                    if rec.internal_transaction_id:
                        dic = self.set_docs_dic(rec, 'Internal', flag, rec.from_id, type)
                        docs.append(dic)
        elif type_transact == 'incoming':
            x = self.env['cm.transaction.trace'].search(domain, order="date desc")
            if x:
                for rec in x:
                    if rec.incoming_transaction_id:
                        dic = self.set_docs_dic(rec, 'Incoming', flag, rec.from_id, type)
                        docs.append(dic)
        else:
            internal_ids = self.env['cm.transaction.trace'].search(domain, order="date desc")
            if internal_ids:
                for rec in internal_ids:
                    if rec.internal_transaction_id:
                        dic = self.set_docs_dic(rec, 'Internal', flag, rec.from_id, type)
                        docs.append(dic)
            incoming_ids = self.env['cm.transaction.trace'].search(domain, order="date desc")
            if incoming_ids:
                for rec in incoming_ids:
                    if rec.incoming_transaction_id:
                        dic = self.set_docs_dic(rec, 'Incoming', flag, rec.from_id, type)
                        docs.append(dic)
        final_dic = {}
        key_list = []
        grouped = collections.defaultdict(list)
        for item in docs:
            grouped[item['unit']].append(item)
        for key, value in grouped.items():
            final_dic[key] = list(value)
            key_list.append(key)
        my_key = list(dict.fromkeys(key_list))
        return final_dic, my_key

    @api.model
    def _get_report_values(self, docids, data=None):
        final_dic, my_key = self.get_value(data, 'pdf')
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        # edit by fatma rida to make warning message if no data
        if my_key:
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_start': start_date,
                'date_end': end_date,
                'group_dic': final_dic,
                'key': my_key,
            }
        else:
            raise UserError(_("""No data for your selection\n"""))


