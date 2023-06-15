# -*- coding: utf-8 -*-

from odoo import fields, models


class ActivityReport(models.Model):
    _inherit = 'crm.activity.report'

    won_status = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('pending', 'Pending'),
    ], string='Is Won', readonly=True)

    def _select(self):
        res = super(ActivityReport, self)._select()
        res += ', l.won_status'
        return res
