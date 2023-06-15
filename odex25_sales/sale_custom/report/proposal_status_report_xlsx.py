# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _


class ProposalStatusReportExcel(models.AbstractModel):
    _name = 'report.sale_custom.proposal_status_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    @api.model
    def generate_xlsx_report(self, workbook, data, objs):
        self = self.with_context(lang=self.env.user.lang)

        business_unit_ids, proposal_status_data = self.env['report.sale_custom.proposal_status_report'].get_custom_data(data)


        title = _("Proposal Status" + data['form']['proposal_state_id'][1] +" Report")
        sheet = workbook.add_worksheet('Proposal Status')
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

        headers = [_('Seq'), _('Submital Date'), _('RFP No \n P No \n JOB No'), _('Proposal Name'), _('Note ON Proposal'),
                    _('P Fee \n Revised Fee'), _('Rank'),  _('Job Fee'), _('Contract Status'),
                    _('Duration')]
        for head in headers:
            col_h += 1
            sheet.write(row, col_h, head), format_title
            sheet.set_column(row, col_h, 20)
            sheet.set_row(row, 50)
    
        row += 1
        for business in business_unit_ids:
            # sheet.write(row, col_d + 1, partner.name)
            sheet.merge_range(row, col_d + 1, row, col_d + 12, business.name)
            sheet.set_row(row, 30)
            row += 1

            for p_status in proposal_status_data[business.id]:
                sheet.set_row(row, 50)
                seq +=1
                sheet.write(row, col_d + 1, seq, format_title)
                sheet.write(row, col_d + 2, p_status['date'])
                sheet.write(row, col_d + 3, p_status['crm_seq'] if p_status['crm_seq'] else '' + '\n ' + p_status['proposal'])
                sheet.write(row, col_d + 4, p_status['name'])
                sheet.write(row, col_d + 5, ' ')
                sheet.write(row, col_d + 6, p_status['p_fees'])
                sheet.write(row, col_d + 7, p_status['rank'])
                sheet.write(row, col_d + 8, p_status['contract_value'] )
                sheet.write(row, col_d + 9, p_status['project_duration'])
                sheet.write(row, col_d + 10, p_status['contract_status'])

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


