# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_odex25_helpdesk_tickets_closed = fields.Boolean('Tickets Closed')
    kpi_odex25_helpdesk_tickets_closed_value = fields.Integer(compute='_compute_kpi_odex25_helpdesk_tickets_closed_value')

    def _compute_kpi_odex25_helpdesk_tickets_closed_value(self):
        if not self.env.user.has_group('odex25_helpdesk.group_odex25_helpdesk_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            closed_ticket = self.env['odex25_helpdesk.ticket'].search_count([
                ('close_date', '>=', start),
                ('close_date', '<', end),
                ('company_id', '=', company.id)
            ])
            record.kpi_odex25_helpdesk_tickets_closed_value = closed_ticket

    def _compute_kpis_actions(self, company, user):
        res = super(Digest, self)._compute_kpis_actions(company, user)
        res['kpi_odex25_helpdesk_tickets_closed'] = 'odex25_helpdesk.odex25_helpdesk_team_dashboard_action_main&menu_id=%s' % self.env.ref('odex25_helpdesk.menu_odex25_helpdesk_root').id
        return res
