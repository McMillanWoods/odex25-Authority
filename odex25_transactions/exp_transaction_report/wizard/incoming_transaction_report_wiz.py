# -*- coding: utf-8 -*-
import datetime
import collections
from odoo import api, fields, models, _


# from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class IncomingTransactionReportWizard(models.TransientModel):
    _name = 'incoming.transaction.report.wizard'
    _inherit = "transaction.common.report"
    _description = 'Print incoming Transaction Report'

    
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
        return self.env.ref('exp_transaction_report.incom_transaction_complete_report').report_action(self, data=data)


class ReportIncomingTransaction(models.AbstractModel):
    _name = 'report.exp_transaction_report.template_incom_transaction_report'

    def set_docs_dic(self, transaction, uint, type, to):
        lang = self.env.user.lang
        if type == 'in':
            tran = transaction.internal_transaction_id
            date = transaction.date
            if lang == 'ar_SY':
                name = ' المعاملات الداخلية'
            else:
                name = ' Internal Transaction'
            uint = uint + name
        else:
            tran = transaction
            date = transaction.transaction_date
            if lang == 'ar_SY':
                name = ' المعاملات الواردة الخارجية'
            else:
                name = ' Incoming Transaction'
            uint = uint + name
        dic = {
            'name': tran.name,
            'subject': tran.subject,
            'type': tran.subject_type_id.name,
            'transaction_date': date,
            'form': transaction.from_id.name,
            'to': to,
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
        x = False
        if type_transact == 'incoming':
            domain = []
            employee_ids = self.env['cm.entity'].browse(entity_ids)
            domain.extend((('transaction_date', '>=', start_date),
                           ('transaction_date', '<=', end_date), ('to_ids', 'in', employee_ids.ids)))
            incoming_ids = self.env['incoming.transaction'].search(domain, order="transaction_date desc")
            if incoming_ids:
                for rec in incoming_ids:
                    name = ''
                    for emp in employee_ids:
                        for to in rec.to_ids:
                            name += to.name + ','
                        dic = self.set_docs_dic(rec, emp.name, 'out_in', name)
                        docs.append(dic)
        elif type_transact == 'internal':
            domain = []
            if type == 'unit':
                emp_ids = self.env['cm.entity'].search([('parent_id', 'in', entity_ids), ('type', '=', 'employee')]).ids
                domain.append(('to_id', 'in', emp_ids))
            elif type == 'employee':
                domain.append(('to_id', 'in', entity_ids))
            domain.extend((('action', '!=', 'archive'), ('date', '>=', start_date),
                           ('date', '<=', end_date)))
            trace_log_ids = self.env['cm.transaction.trace'].search(domain, order="date desc")
            if trace_log_ids:
                for rec in trace_log_ids:
                    if rec.internal_transaction_id:
                        dic = self.set_docs_dic(rec, rec.to_id.parent_id.name, 'in', rec.to_id.name)
                        docs.append(dic)
        else:
            in_domain = []
            employee_ids = self.env['cm.entity'].browse(entity_ids)
            in_domain.extend((('transaction_date', '>=', start_date),
                              ('transaction_date', '<=', end_date), ('to_ids', 'in', employee_ids.ids)))
            incoming_ids = self.env['incoming.transaction'].search(in_domain, order="transaction_date desc")
            if incoming_ids:
                for rec in incoming_ids:
                    name = ''
                    for emp in employee_ids:
                        for to in rec.to_ids:
                            name += to.name + ','
                        dic = self.set_docs_dic(rec, emp.name, 'out_in', name)
                        docs.append(dic)
            domain = []
            if type == 'unit':
                emp_ids = self.env['cm.entity'].search([('parent_id', 'in', entity_ids), ('type', '=', 'employee')]).ids
                domain.append(('to_id', 'in', emp_ids))
            elif type == 'employee':
                domain.append(('to_id', 'in', entity_ids))
            domain.extend((('action', '!=', 'archive'), ('date', '>=', start_date),
                           ('date', '<=', end_date)))
            trace_log_ids = self.env['cm.transaction.trace'].search(domain, order="date desc")
            if trace_log_ids:
                for rec in trace_log_ids:
                    if rec.internal_transaction_id:
                        dic = self.set_docs_dic(rec, rec.to_id.parent_id.name, 'in', rec.to_id.name)
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

