# -*- coding: utf-8 -*-
import collections
import datetime

from odoo import api,models,_
# from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class CloseTransactionReportWizard(models.TransientModel):
    _name = 'close.transaction.report.wizard'
    _inherit = "transaction.common.report"
    _description = 'Print Close Transaction Report'

    
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
        return self.env.ref('exp_transaction_report.close_transaction_complete_report').report_action(self, data=data)

    
    def print_excel_report(self):
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
        return self.env.ref('exp_transaction_report.close_transaction_xls').report_action(self, data=data, config=False)


class ReportCloseTransaction(models.AbstractModel):

    _name = 'report.exp_transaction_report.template_close_transaction_report'

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
        if lang == 'ar_SY' and name == 'Internal':
            name = 'داخلية'
        elif lang == 'ar_SY' and name == 'Incoming':
            name = 'واردة'
        if flag == 'pdf':
            date = datetime.datetime.strptime(str(transaction.date), '%Y-%m-%d %H:%M:%S').date()
        dic = {
            'classification': name,
            'name': trans.name,
            'subject': trans.subject,
            'type': trans.subject_type_id.name,
            'transaction_date': trans.transaction_date,
            'archive': transaction.archive_type_id.name,
            'date': date,
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
            emp_ids = self.env['cm.entity'].search([('parent_id', 'in', entity_ids)]).ids
            domain.append(('from_id', 'in', emp_ids))
        elif type == 'employee':
            domain.append(('from_id', 'in', entity_ids))
        domain.extend((('action', '=', 'archive'), ('date', '>=', start_date),
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


class CloseReportXls(models.AbstractModel):
    _name = 'report.exp_transaction_report.close_transaction_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        x = self.env['report.exp_transaction_report.template_close_transaction_report']
        final_dic, key = ReportCloseTransaction.get_value(x, data, 'excel')
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        sheet = workbook.add_worksheet(_("Close Transactions Report"))
        sheet.right_to_left()
        format2 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True,
             'align': 'center',
             'bold': True})
        format2.set_align('center')
        format2.set_align('vcenter')

        sheet.merge_range('D3:G3', _("Close Transactions Report"), format2)
        row = 6
        for line in key:
            sheet.write(row + 2, 2, line, format2)
            row += 3
            sheet.write(row, 2, '#', format2)
            sheet.write(row, 3, _("Transaction classification"), format2)
            sheet.set_column('C:C', 10)
            sheet.write(row, 4, _("Transaction number"), format2)
            sheet.set_column('D:D', 20)
            sheet.write(row, 5, _("Date of transaction"), format2)
            sheet.set_column('E:E', 20)
            sheet.write(row, 6, _("Subject"), format2)
            sheet.set_column('F:F', 25)
            sheet.write(row, 7, _("Type"), format2)
            sheet.set_column('G:G', 25)
            sheet.write(row, 8, _("Reason for closure"), format2)
            sheet.set_column('H:H', 25)
            sheet.write(row, 9, _("Closing date"), format2)
            sheet.set_column('I:I', 25)
            sheet.write(row, 10, _("Notes"), format2)
            sheet.set_column('J:J', 25)
            z = 0
            for x in final_dic[line]:
                row += 1
                z += 1
                sheet.write(row, 2,  z, format2)
                sheet.write(row, 3, x['classification'], format2)
                sheet.write(row, 4, x['name'], format2)
                sheet.write(row, 5, x['transaction_date'][0:10], format2)
                sheet.write(row, 6, x['subject'], format2)
                sheet.write(row, 7, x['type'], format2)
                sheet.write(row, 8, x['archive'], format2)
                sheet.write(row, 9, x['date'][0:10], format2)
                sheet.write(row, 10, x['note'], format2)

        sheet.merge_range('A4:C4', _("Start date"), format2)
        sheet.merge_range('A5:C5', _("End date"), format2)
        sheet.write(3, 3, str(start_date)[0:10], format2)
        sheet.write(4, 3, str(end_date)[0:10], format2)