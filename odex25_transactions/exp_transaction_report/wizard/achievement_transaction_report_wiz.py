# -*- coding: utf-8 -*-
import collections
import datetime
from odoo import api, fields, models,_
# from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class AchievementTransactionReportWizard(models.TransientModel):
    _name = 'achievement.transaction.report.wizard'
    _inherit = "transaction.common.report"
    _description = 'Print Achievement Transaction Report'

    
    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'type': self.type,
                'entity_ids': self.entity_ids.ids,
                'start_date': self.start_date,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('exp_transaction_report.achievement_transaction_complete_report').report_action(self, data=data)

    
    def print_excel_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'type': self.type,
                'entity_ids': self.entity_ids.ids,
                'start_date': self.start_date,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('exp_transaction_report.achievement_transaction_xls').report_action(self, data=data, config=False)


class ReportAchievementTransaction(models.AbstractModel):
    _name = 'report.exp_transaction_report.achievement_tran_report_temp'

    def get_value(self, data, flag):
        type = data['form']['type']
        entity_ids = data['form']['entity_ids']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        docs = []
        x = False
        employee_ids = ''
        data = {'unit': [], 'total_from': {}, 'total_to': {}, 'total_transfer_from': {}, 'total_transfer_to': {},
                'total_closed': {}}
        if type == 'unit':
            employee_ids = self.env['cm.entity'].search([('parent_id', 'in', entity_ids)])
        else:
            employee_ids = self.env['cm.entity'].browse(entity_ids)
        for employee in employee_ids:
            total_from = 0
            total_to = 0
            transfered_from = 0
            transfered_to = 0
            closed = 0
            from_ids = self.env['internal.transaction'].search(
                                           [('employee_id', '=', employee.id), ('transaction_date', '>=', start_date),
                                            ('transaction_date', '<=', end_date)])
            to_ids = self.env['internal.transaction'].search(
                                         [('to_ids', '=', employee.id), ('transaction_date', '>=', start_date),
                                          ('transaction_date', '<=', end_date)])
            transfer_from_ids = self.env['cm.transaction.trace'].search([('from_id', '=', employee.id),
                                                                         ('action', '=', 'forward'),
                                                                         ('date', '>=', start_date),
                                                                         ('date', '<=', end_date)])
            transfer_to_ids = self.env['cm.transaction.trace'].search([('to_id', '=', employee.id),
                                                                       ('action', '=', 'forward'),
                                                                       ('date', '>=', start_date),
                                                                       ('date', '<=', end_date)])
            closed_ids = self.env['cm.transaction.trace'].search([('from_id', '=', employee.id),
                                                                  ('action', '=', 'archive'),
                                                                  ('date', '>=', start_date),
                                                                  ('date', '<=', end_date)], order="date desc")
            total_from += len(from_ids)
            total_to += len(to_ids)
            transfered_from += len(transfer_from_ids)
            transfered_to += len(transfer_to_ids)
            y = []
            for close in closed_ids:
                if close.internal_transaction_id.state == 'closed':
                    t_obj = self.env['cm.transaction.trace'].search([('internal_transaction_id', '=', close.internal_transaction_id.id),
                                                                 ('action', '=', 'archive')], order="date desc", limit=1)

                    if t_obj.from_id.id == employee.id:
                        if close.internal_transaction_id.id not in y:
                            y.append(close.internal_transaction_id.id)
            closed += len(y)
            if type == 'unit':
                name = employee.parent_id.name
                if employee.parent_id not in data['unit']:
                    data['unit'].append(employee.parent_id)
            else:
                name = employee.name
                if employee not in data['unit']:
                    data['unit'].append(employee)
            if name not in data['total_from']:
                data['total_from'][name] = total_from
            else:
                data['total_from'][name] += total_from
            if name not in data['total_to']:
                data['total_to'][name] = total_to
            else:
                data['total_to'][name] += total_to
                # transfer
            if name not in data['total_transfer_from']:
                data['total_transfer_from'][name] = transfered_from
            else:
                data['total_transfer_from'][name] += transfered_from
            if name not in data['total_transfer_to']:
                data['total_transfer_to'][name] = transfered_to
            else:
                data['total_transfer_to'][name] += transfered_to
            if name not in data['total_closed']:
                data['total_closed'][name] = closed
            else:
                data['total_closed'][name] += closed
        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        final_dic = self.get_value(data, 'pdf')
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        # edit by fatma rida to make warning message if no data
        if final_dic:
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_start': start_date,
                'date_end': end_date,
                'data': final_dic,
            }
        else:
            raise UserError(_("""No data for your selection\n"""))


class AchievementReportXls(models.AbstractModel):
    _name = 'report.exp_transaction_report.achievement_transaction_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        x = self.env['report.exp_transaction_report.template_close_transaction_report']
        final_dic = ReportAchievementTransaction.get_value(x, data, 'excel')
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        sheet = workbook.add_worksheet(U'duration report')
        sheet.right_to_left()
        format2 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        format2.set_align('center')
        format2.set_align('vcenter')

        sheet.merge_range('D3:G3', _("Compilation Report"), format2)

        sheet.write(6, 2, '#', format2)
        sheet.write(6, 3, _("Department/Employee"), format2)
        sheet.set_column('C:C', 10)
        sheet.write(6, 4, _("Number of incoming transactions"), format2)
        sheet.set_column('D:D', 20)
        sheet.write(6, 5, _("Number of transactions issued"), format2)
        sheet.set_column('E:E', 20)
        sheet.write(6, 6, _("Number of transactions transferred by departament"), format2)
        sheet.set_column('F:F', 25)
        sheet.write(6, 7, _("Number of transactions referred to departament"), format2)
        sheet.set_column('G:G', 25)
        sheet.write(6, 8, _("Number of closed transactions"), format2)
        sheet.set_column('H:H', 25)
        row = 6
        for index, line in enumerate(final_dic['unit']):
            row += 1
            sheet.write(row, 2, index + 1, format2)
            sheet.write(row, 3, line.name, format2)
            sheet.write(row, 4, final_dic['total_to'][line.name], format2)
            sheet.write(row, 5, final_dic['total_from'][line.name], format2)
            sheet.write(row, 6, final_dic['total_transfer_from'][line.name], format2)
            sheet.write(row, 7, final_dic['total_transfer_to'][line.name], format2)
            sheet.write(row, 8, final_dic['total_closed'][line.name], format2)

        sheet.merge_range('A4:C4', _("Start date"), format2)
        sheet.merge_range('A5:C5', _("End date"), format2)
        sheet.write(3, 3, str(start_date)[0:10], format2)
        sheet.write(4, 3, str(end_date)[0:10], format2)