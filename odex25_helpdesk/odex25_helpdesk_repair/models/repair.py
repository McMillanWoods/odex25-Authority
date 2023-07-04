# -*- coding: utf-8 -*-

from odoo import fields, models


class Repair(models.Model):
    _inherit = 'repair.order'

    ticket_id = fields.Many2one('odex25_helpdesk.ticket', string="Ticket", help="Related Helpdesk Ticket")
