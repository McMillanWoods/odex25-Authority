# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime
import collections


# from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class LateTransactionReportWizard(models.TransientModel):
    _name = 'late.transaction.report.wizard'
    _inherit = "transaction.common.report"
    _description = 'Print late Transaction Report'

    
    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'type': self.type,
                'type_transact': self.type_transact,
                'entity_ids': self.entity_ids.ids,
                'start_date': self.start_date,
            },
        }
        return self.env.ref('exp_transaction_report.late_transaction_complete_report').report_action(self, data=data)


class ReportIncomingTransaction(models.AbstractModel):
    _name = 'report.exp_transaction_report.template_late_transaction_report'

    def set_docs_dic(self, transaction, type, uint, to):
        lang = self.env.user.lang
        if type == 'in':
            if lang == 'ar_SY':
                name = ' المعاملات الداخلية'
            else:
                name = ' Internal Transaction'
            uint = uint + name
        else:
            if lang == 'ar_SY':
                name = ' المعاملات الواردة الخارجية'
            else:
                name = ' Incoming Transaction'
            uint = uint + name
        dic = {
            'name': transaction.name,
            'subject': transaction.subject,
            'type': transaction.subject_type_id.name,
            'transaction_date': transaction.transaction_date,
            'due_date': transaction.due_date,
            'to': to,
            'unit': uint,
        }
        return dic

    def get_value(self, data):
        type = data['form']['type']
        type_transact = data['form']['type_transact']
        entity_ids = data['form']['entity_ids']
        start_date = data['form']['start_date']
        docs = []
        x = False
        if type_transact == 'incoming':
            domain = []
            employee_ids = self.env['cm.entity'].browse(entity_ids)
            domain.extend((('transaction_date', '>=', start_date),
                           ('to_ids', 'in', employee_ids.ids), ('state', 'in', ['send', 'reply'])))
            incoming_ids = self.env['incoming.transaction'].search(domain, order="transaction_date desc")
            if incoming_ids:
                today = fields.date.today()
                for rec in incoming_ids:
                    if datetime.datetime.strptime(rec.due_date, "%Y-%m-%d") < datetime.datetime.strptime(str(today), "%Y-%m-%d"):
                        trasc = rec.trace_ids.filtered(lambda z: z.action == 'forward' or z.action == 'sent' or
                                                                 z.action == 'reply')[0]
                    name = ''
                    for to in rec.to_ids:
                        name += to.name + ','
                    dic = self.set_docs_dic(rec, 'out_in', name, trasc.to_id.name)
                    docs.append(dic)
        elif type_transact == 'internal':
            domain = []
            employee_ids = self.env['cm.entity'].browse(entity_ids)
            domain.extend((('transaction_date', '>=', start_date),
                           ('to_ids', 'in', employee_ids.ids), ('state', 'in', ['send', 'reply'])))
            internal_ids = self.env['internal.transaction'].search(domain, order="transaction_date desc")
            if internal_ids:
                today = fields.date.today()
                for rec in internal_ids:
                    if datetime.datetime.strptime(rec.due_date, "%Y-%m-%d") < datetime.datetime.strptime(str(today), "%Y-%m-%d"):
                        trasc = rec.trace_ids.filtered(lambda z: z.action == 'forward' or z.action == 'sent' or
                                                                 z.action == 'reply')[0]
                    name = ''
                    for to in rec.to_ids:
                        name += to.name + ','
                    dic = self.set_docs_dic(rec, 'in', name, trasc.to_id.name)
                    docs.append(dic)
        else:
            domain = []
            employee_ids = self.env['cm.entity'].browse(entity_ids)
            domain.extend((('transaction_date', '>=', start_date),
                           ('to_ids', 'in', employee_ids.ids), ('state', 'in', ['send', 'reply'])))
            incoming_ids = self.env['incoming.transaction'].search(domain, order="transaction_date desc")
            if incoming_ids:
                today = fields.date.today()
                for rec in incoming_ids:
                    if datetime.datetime.strptime(rec.due_date, "%Y-%m-%d") < datetime.datetime.strptime(str(today),
                                                                                                         "%Y-%m-%d"):
                        trasc = rec.trace_ids.filtered(lambda z: z.action == 'forward' or z.action == 'sent' or
                                                                 z.action == 'reply')[0]
                    name = ''
                    for to in rec.to_ids:
                        name += to.name + ','
                    dic = self.set_docs_dic(rec, 'out_in', name, trasc.to_id.name)
                    docs.append(dic)
            internal_ids = self.env['internal.transaction'].search(domain, order="transaction_date desc")
            if internal_ids:
                today = fields.date.today()
                for rec in internal_ids:
                    if datetime.datetime.strptime(rec.due_date, "%Y-%m-%d") < datetime.datetime.strptime(str(today),
                                                                                                         "%Y-%m-%d"):
                        trasc = rec.trace_ids.filtered(lambda z: z.action == 'forward' or z.action == 'sent' or
                                                                 z.action == 'reply')[0]
                        name = ''
                        for to in rec.to_ids:
                            name += to.name + ','
                        dic = self.set_docs_dic(rec, 'in', name, trasc.to_id.name)
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
        final_dic, my_key = self.get_value(data)
        start_date = data['form']['start_date']
        # edit by fatma rida to make warning message if no data
        if my_key:
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_start': start_date,
                'group_dic': final_dic,
                'key': my_key,
            }
        else:
            raise UserError(_("""No data for your selection\n"""))

