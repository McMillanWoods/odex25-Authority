# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Task(models.Model):
    _inherit = 'project.task'

    odex25_helpdesk_ticket_id = fields.Many2one('odex25_helpdesk.ticket', string='Ticket', help='Ticket this task was generated from', readonly=True)

    def action_view_ticket(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'odex25_helpdesk.ticket',
            'view_mode': 'form',
            'res_id': self.odex25_helpdesk_ticket_id.id,
        }