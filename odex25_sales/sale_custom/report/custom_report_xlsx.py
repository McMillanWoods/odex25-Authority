# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _


class CustomReportExcel(models.AbstractModel):
    _name = 'report.sale_custom.custom_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    @api.model
    def generate_xlsx_report(self, workbook, data, objs):
        self = self.with_context(lang=self.env.user.lang)

        business_unit_ids = data['form']['business_unit_ids']

        custom_data = self.env['report.sale_custom.custom_report'].get_custom_data(business_unit_ids, data)


        for business in business_unit_ids:
            if custom_data[business]:
                title = _("Custom Report")
                sheet = workbook.add_worksheet('Proposal Status' + str(business))
                format_title = workbook.add_format({ 'align': 'center' })
                format_float = workbook.add_format({ 'align': 'center' })
                format_float.set_num_format('#,##0.00')
                sheet.merge_range( 1, 7, 0, 6, title, format_title)
                self.write_filters(data, sheet)
                lang_id = self.env['res.lang'].search([('code', '=', self.env.user.lang)])
                if lang_id.direction == 'rtl':
                    sheet.right_to_left()

                row = 6
                col_h = 1
                col_d = 1
                seq = 0.0

                headers = [_('Seq'), _('Submital Date'), _('RFP No \n P No \n JOB No'), _('Proposal Name'), _('Proposal Status'),
                            _('P Fee \n Revised Fee'), _('Potential'),  _('Rank'), _('Contract Status'),
                            _('Job Fee'), _('Duration'),  _('Contact \n Position'), _('Phone \n EXT')]
                for head in headers:
                    col_h += 1
                    sheet.write(row, col_h, head)
                    sheet.set_column(row, col_h, 10)
            
                row += 1
                for custom in custom_data[business]:
                    seq +=1
                    sheet.write(row, col_d + 1, seq)
                    sheet.write(row, col_d + 2, custom['date'])
                    sheet.write(row, col_d + 3, custom['crm_seq'] + '\n ' + custom['proposal'])
                    sheet.write(row, col_d + 4, custom['name'])
                    sheet.write(row, col_d + 5, custom['proposal_status'])
                    sheet.write(row, col_d + 6, custom['p_fees'])
                    sheet.write(row, col_d + 7, '')
                    sheet.write(row, col_d + 8, '' )
                    sheet.write(row, col_d + 9, custom['contract_status'])
                    sheet.write(row, col_d + 10, '')
                    sheet.write(row, col_d + 11, custom['project_duration'])
                    sheet.write(row, col_d + 12, custom['customer'].name)
                    sheet.write(row, col_d + 13, custom['customer'].phone)



                    row += 1


    def write_filters(self, data, sheet):

        filters =  [
                    [ _("Date From: "),  data['form']['date_from']],
                    [ _("To: "),  data['form']['date_to']],
                    [ _("User"),  self.env.user.name]
                    ]
        col_pos = 1
        row_pos = 3
        for title, value in filters:

            sheet.write_string(row_pos, col_pos, title)
            sheet.merge_range(row_pos, col_pos + 1, row_pos, col_pos + 2, value)
            col_pos += 4


