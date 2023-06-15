# -*- coding: utf-8 -*-
import collections
import datetime
from odoo import api, fields, models, _


# from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class OutgoingTransactionReportWizard(models.TransientModel):
    _name = 'outgoing.transaction.report.wizard'
    _inherit = "transaction.common.report"
    _description = 'Print outgoing Transaction Report'

    type_transact = fields.Selection([('internal', 'Internal'), ('outgoing', 'Outgoing'), ('all', 'All')],
                                     'Transaction Type')

    
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
        return self.env.ref('exp_transaction_report.out_transaction_complete_report').report_action(self, data=data)


class ReportOutgoingTransaction(models.AbstractModel):
    _name = 'report.exp_transaction_report.template_out_transaction_report'

    def set_docs_dic(self, transaction, uint, type):
        to_name = ''
        if transaction.to_ids:
            for to in transaction.to_ids:
                to_name += to.name + ','
        dic = {
            'name': transaction.name,
            'subject': transaction.subject,
            'type': transaction.subject_type_id.name,
            'transaction_date': transaction.transaction_date,
            'to': to_name,
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
            employee_ids = self.env['cm.entity'].search([('parent_id', 'in', entity_ids), ('type', '=', 'employee')])
        else:
            employee_ids = self.env['cm.entity'].browse(entity_ids)
        domain.extend((('transaction_date', '>=', start_date),
                       ('transaction_date', '<=', end_date)))
        if type_transact != 'all':
            model_name = ''
            if type_transact == 'internal':
                model_name = 'internal.transaction'
                domain.append(('state', '=', 'send'))
            elif type_transact == 'outgoing':
                model_name = 'outgoing.transaction'
            transaction_ids = self.env[model_name].search(domain, order="transaction_date desc")
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
        else:
            internal_ids = self.env['internal.transaction'].search(domain, order="transaction_date desc")
            if internal_ids:
                for rec in internal_ids:
                    for emp in employee_ids:
                        if rec.employee_id.id == emp.id:
                            if type == 'unit':
                                dic = self.set_docs_dic(rec, emp.parent_id.name, type)
                                docs.append(dic)
                            else:
                                dic = self.set_docs_dic(rec, emp.name, type)
                                docs.append(dic)
            outgoing_ids = self.env['outgoing.transaction'].search(domain, order="transaction_date desc")
            if outgoing_ids:
                for rec in outgoing_ids:
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
        return final_dic, my_key

    @api.model
    def _get_report_values(self, docids, data=None):
        final_dic, my_key = self.get_value(data)
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

