# -*- coding: utf-8 -*-

from odoo import fields, models, tools


class MailingTraceReport(models.Model):
    _inherit = 'mailing.trace.report'

    def _report_get_request_where_items(self):
        res = super(MailingTraceReport, self)._report_get_request_where_items()
        res.append("mailing.use_in_odex25_marketing_automation IS NOT TRUE")
        return res
