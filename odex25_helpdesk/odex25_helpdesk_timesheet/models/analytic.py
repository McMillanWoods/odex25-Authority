# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.osv import expression


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    odex25_helpdesk_ticket_id = fields.Many2one('odex25_helpdesk.ticket', 'Helpdesk Ticket')

    def _compute_task_id(self):
        super(AccountAnalyticLine, self)._compute_task_id()
        for line in self.filtered(lambda line: line.odex25_helpdesk_ticket_id):
            line.task_id = line.odex25_helpdesk_ticket_id.task_id

    def _timesheet_preprocess(self, vals):
        odex25_helpdesk_ticket_id = vals.get('odex25_helpdesk_ticket_id')
        if odex25_helpdesk_ticket_id:
            ticket = self.env['odex25_helpdesk.ticket'].browse(odex25_helpdesk_ticket_id)
            if ticket.project_id:
                vals['project_id'] = ticket.project_id.id
            if ticket.task_id:
                vals['task_id'] = ticket.task_id.id
        vals = super(AccountAnalyticLine, self)._timesheet_preprocess(vals)
        return vals

    def _timesheet_get_portal_domain(self):
        domain = super(AccountAnalyticLine, self)._timesheet_get_portal_domain()
        return expression.OR([domain, self._timesheet_in_odex25_helpdesk_get_portal_domain()])

    def _timesheet_in_odex25_helpdesk_get_portal_domain(self):
        return [
            '&',
                '&',
                    '&',
                        ('task_id', '=', False),
                        ('odex25_helpdesk_ticket_id', '!=', False),
                    '|',
                        '|',
                            ('project_id.message_partner_ids', 'child_of', [self.env.user.partner_id.commercial_partner_id.id]),
                            ('project_id.allowed_portal_user_ids', 'child_of', [self.env.user.id]),
                        ('odex25_helpdesk_ticket_id.message_partner_ids', 'child_of', [self.env.user.partner_id.commercial_partner_id.id]),
                ('project_id.privacy_visibility', '=', 'portal')
        ]
