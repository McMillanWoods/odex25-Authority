# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from lxml import etree
import json
import simplejson
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'odex25_helpdesk.ticket'

    def _default_team_id(self):

        team_id = False
        if self.user_has_groups('helpdesk_employee_request.group_helpdesk_Secretary'):
            if self._context.get('default_ticket_service_type') == 'request':
                team_id = self.env['odex25_helpdesk.team'].search(
                    [('branch_id', '=', self.env.user.branch_id.id), ('is_internal_team', '=', False)], limit=1).id
            elif self._context.get('default_ticket_service_type') == 'vip':
                team_id = self.env['odex25_helpdesk.team'].search(
                    [('branch_id', '=', self.env.user.branch_id.id), ('is_vip_team', '=', True)], limit=1).id
        elif self.user_has_groups('helpdesk_employee_request.group_helpdesk_employee'):
            team_id = self.env['odex25_helpdesk.team'].search(
                [('branch_id', '=', self.env.user.branch_id.id), ('is_internal_team', '=', False)], limit=1).id
        elif self.user_has_groups('helpdesk_employee_request.group_helpdesk_vip_employee'):
            team_id = self.env['odex25_helpdesk.team'].search(
                [('branch_id', '=', self.env.user.branch_id.id), ('is_vip_team', '=', True)], limit=1).id

        return team_id

    team_id = fields.Many2one('odex25_helpdesk.team', string='Helpdesk Team', default=_default_team_id, index=True)

    requester_id = fields.Many2one('res.users')
    is_submitted = fields.Boolean(default=False)
    is_vip_team = fields.Boolean(related="team_id.is_vip_team", readonly=True)
    is_internal_team = fields.Boolean(related="team_id.is_internal_team", readonly=True)
    ticket_service_type = fields.Selection([
        ('vip', 'VIP'),
        ('request', 'Request'),
        ('secretary', 'Secretary')])

    @api.model
    def create(self, vals):
        """
            prevent editing after saving the record
        """
        record = super(HelpdeskTicket, self).create(vals)
        record.is_submitted = True
        record.active = True
        return record

    @api.onchange('employee_id')
    def set_requester(self):
        """
            get the partner of the user
        """
        user = self.env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1)
        self.requester_id = user.id

    def submit_to_user(self):
        """
            set the flag to true so fields be readonly and go to next stage
        """
        for rec in self:
            rec.is_submitted = True
            rec.active = True
        self.fields_view_get(view_type='form')

    @api.model
    @api.onchange('requester_id')
    def _get_customer_from_requester(self):
        """
            setting customer value from requester id
        """
        if self._context.get('employee_request'):
            self.requester_id = self.env.uid
            self.partner_id = self.requester_id.partner_id.id
            self.partner_email = self.partner_id.email
            res = {'domain': {'partner_id': [('id', '=', [self.requester_id.partner_id.id])]}}
            return res
