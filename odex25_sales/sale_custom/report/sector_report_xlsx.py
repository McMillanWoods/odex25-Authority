# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _


class SectorReportExcel(models.AbstractModel):
    _name = 'report.sale_custom.sector_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    @api.model
    def generate_xlsx_report(self, workbook, data, objs):
        self = self.with_context(lang=self.env.user.lang)

        sector_id = data['form']['sector_id'][0]

        partner_ids, sector_data = self.env['report.sale_custom.sector_report'].get_sector_data(sector_id, data)


        title = _("Proposal" + data['form']['sector_id'][1] +" Report")
        sheet = workbook.add_worksheet('Sector Report')
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
                    _('Contact'), _('Phone')]
        for head in headers:
            col_h += 1
            sheet.write(row, col_h, head, format_title)
            sheet.set_column(row, col_h, 20)
            sheet.set_row(row, 50)
    
        row += 1
        for partner in partner_ids:
            # sheet.write(row, col_d + 1, partner.name)
            sheet.merge_range(row, col_d + 1, row, col_d + 12, partner.name)
            sheet.set_row(row, 30)
            row += 1
            for sector in sector_data[partner.id]:
                sheet.set_row(row, 50)
                seq +=1
                sheet.write(row, col_d + 1, seq, format_title)
                sheet.write(row, col_d + 2, sector['date'])
                sheet.write(row, col_d + 3, sector['crm_seq'] + '\n ' + sector['proposal'])

                sheet.write(row, col_d + 4, sector['name'])
                sheet.write(row, col_d + 5, sector['business_unit'])
                sheet.write(row, col_d + 6, sector['proposal_status'])
                sheet.write(row, col_d + 7, sector['p_fees'])
                sheet.write(row, col_d + 8, '' )
                sheet.write(row, col_d + 9, sector['project_duration'])
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


