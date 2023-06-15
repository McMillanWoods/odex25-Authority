# -*- coding: utf-8 -*-
import collections
import datetime
from odoo import api, fields, models,_
# from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class OutstandingTransactionReportWizard(models.TransientModel):
    _name = 'outstanding.transaction.report.wizard'
    _inherit = "transaction.common.report"
    _description = 'Print Outstanding Transaction Report'

    type_transact = fields.Selection([('outgoing', 'Outgoing'), ('incoming', 'Incoming')], 'Transaction Type')

    
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
        return self.env.ref('exp_transaction_report.outstanding_transaction_complete_report').report_action(self, data=data)


class ReportOutstandingTransaction(models.AbstractModel):
    _name = 'report.exp_transaction_report.outstand_transaction_report_temp'

    def set_docs_dic(self, transaction, uint, type):
        dic = {
            'name': transaction.name,
            'subject': transaction.subject,
            'type': transaction.subject_type_id.name,
            'transaction_date': transaction.transaction_date,
            'to': transaction.to_ids[0].name,
            'processing': transaction.processing_ids,
            'unit': uint,
        }
        return dic

    def get_value(self, data):
        type = data['form']['type']
        type_transact = data['form']['type_transact']
        entity_ids = data['form']['entity_ids']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        docs = []
        domain = []
        employee_ids = ''
        if type == 'unit':
            employee_ids = self.env['cm.entity'].search([('parent_id', 'in', entity_ids)])
        else:
            employee_ids = self.env['cm.entity'].browse(entity_ids)
        domain.extend((('transaction_date', '>=', start_date),
                       ('transaction_date', '<=', end_date),
                       ('type', 'in', ('reply', 'forward'))
                       ))
        search_model = ''
        re_name = ''
        lang = self.env.user.lang
        if type_transact == 'outgoing':
            search_model = self.env['outgoing.transaction']
            domain.append(('state', '=', 'send'))
            re_name = 'Outgoing Transactions'
            if lang == 'ar_SY':
                re_name = ' المعاملات الخارجية الصادره'
        else:
            search_model = self.env['incoming.transaction']
            domain.append(('state', '=', 'closed'))
            re_name = 'Incoming Transactions'
            if lang == 'ar_SY':
                re_name = ' المعاملات الخارجية الوارده'
        transaction_ids = search_model.search(domain, order="transaction_date desc")
        if transaction_ids:
            for rec in transaction_ids:
                for emp in employee_ids:
                    if rec.employee_id.id == emp.id:
                        if type == 'unit':
                            dic = self.set_docs_dic(rec, emp.parent_id.name, type)
                            docs.append(dic)
                        else:
                            dic = self.set_docs_dic(rec, emp.name, type)
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
        return final_dic, my_key, re_name

    @api.model
    def _get_report_values(self, docids, data=None):
        final_dic, my_key, name = self.get_value(data)
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        # edit by fatma rida to make warning message if no data
        if my_key:
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_start': start_date,
                'date_end': end_date,
                'name': name,
                'group_dic': final_dic,
                'key': my_key,
            }
        else:
            raise UserError(_("""No data for your selection\n"""))

