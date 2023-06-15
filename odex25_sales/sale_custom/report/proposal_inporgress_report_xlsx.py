# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2021-2022 LCT
#
##############################################################################


from odoo import api, models, _


class ProposalInprogressReportExcel(models.AbstractModel):
    _name = 'report.sale_custom.proposal_inporgress_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    @api.model
    def generate_xlsx_report(self, workbook, data, objs):
        self = self.with_context(lang=self.env.user.lang)

        proposal_inporgress = self.env['report.sale_custom.proposal_inporgress_report'].get_proposal_inporgress_data( data)

        title = _("Proposal Inprogress Report")
        sheet = workbook.add_worksheet('Proposal Inprogress Report')
        format_title = workbook.add_format({ 'align': 'center' })
        format_float = workbook.add_format({ 'align': 'center' })
        format_float.set_num_format('#,##0.00')
        sheet.merge_range( 1, 4, 0, 3, title, format_title)
        self.write_filters(data, sheet)
        lang_id = self.env['res.lang'].search([('code', '=', self.env.user.lang)])
        if lang_id.direction == 'rtl':
            sheet.right_to_left()

        row = 6
        col_h = 1
        col_d = 1
        seq = 0.0

        headers = [_('Seq'), _('Submital Date'), _('Bid Bond'), _('RFP No \n P No \n JOB No'), _('Proposal Name'), 
                    _('Note'), _('BL')]
        for head in headers:
            col_h += 1
            sheet.write(row, col_h, head, format_title)
            sheet.set_column(row, col_h, 20)
            sheet.set_row(row, 50)
    
        row += 1
        for proposal in proposal_inporgress:
            sheet.set_row(row, 50)
            bidbond = 'Exist' if proposal['bidbond'] else 'Not'
            seq +=1
            sheet.write(row, col_d + 1, seq, format_title)
            sheet.write(row, col_d + 2, proposal['date'])
            sheet.write(row, col_d + 3, bidbond)
            sheet.write(row, col_d + 4, proposal['crm_seq'] + '\n ' + proposal['proposal'] if proposal['proposal'] else '', format_title)

            sheet.write(row, col_d + 5, proposal['name'])

            sheet.write(row, col_d + 6, '' )
            sheet.write(row, col_d + 7, proposal['business_unit'])

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


