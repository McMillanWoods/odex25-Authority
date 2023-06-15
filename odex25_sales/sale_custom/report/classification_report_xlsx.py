# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _


class ClassificationReportExcel(models.AbstractModel):
    _name = 'report.sale_custom.classification_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    @api.model
    def generate_xlsx_report(self, workbook, data, objs):
        self = self.with_context(lang=self.env.user.lang)

        classification_ids = data['form']['classification_ids']

        partner_ids = self.env['res.partner'].search([('industry_id', 'in', classification_ids)])
        classification_data = self.env['report.sale_custom.classification_report'].get_classification_data(partner_ids.ids, data)

        for partner in partner_ids:
            if classification_data[partner.id]:
                title = _("Proposal Classification Report")
                sheet = workbook.add_worksheet(partner.name)
                format_title = workbook.add_format({ 'align': 'center' })
                format_float = workbook.add_format({ 'align': 'center' })
                format_float.set_num_format('#,##0.00')
                sheet.merge_range( 1, 4, 0, 3, title, format_title)
                self.write_filters(data, sheet)
                lang_id = self.env['res.lang'].search([('code', '=', self.env.user.lang)])
                if lang_id.direction == 'rtl':
                    sheet.right_to_left()

                row = 6
                col_h = 0
                col_d = 0
                seq = 0.0

                headers = [_('Seq'), _('Submital Date'), _('RFP No \n P No \n JOB No'), _('Proposal Name'), _('BL'),
                            _('Proposal Status'), _('P Fee \n Revised Fee'),  _('Job Fee'),_('Duration'),_('Note'),
                            _('Contact'), _('Phone \n EXT')]
                for head in headers:
                    col_h += 1
                    sheet.write(row, col_h, head, format_title)
                    sheet.set_column(row, col_h, 20)
                    sheet.set_row(row, 50)
            
                row += 1
                for classification in classification_data[partner.id]:
                    sheet.set_row(row, 50)
                    seq +=1
                    sheet.write(row, col_d + 1, seq, format_title)
                    sheet.write(row, col_d + 2, classification['date'])
                    sheet.write(row, col_d + 3, classification['crm_seq'] if classification['crm_seq'] else '' + '\n ' + classification['proposal'])

                    sheet.write(row, col_d + 4, classification['name'])
                    sheet.write(row, col_d + 5, classification['business_unit'])
                    sheet.write(row, col_d + 6, classification['proposal_status'])
                    sheet.write(row, col_d + 7, classification['p_fees'])
                    sheet.write(row, col_d + 8, '' )
                    sheet.write(row, col_d + 9, classification['project_duration'])
                    sheet.write(row, col_d + 10, '' )
                    sheet.write(row, col_d + 11, partner.name)
                    sheet.write(row, col_d + 12, partner.phone)
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
            sheet.set_column(row_pos, col_pos, 20)
            sheet.write_string(row_pos, col_pos, title)
            sheet.write(row_pos, col_pos + 1, value)
            col_pos += 2


