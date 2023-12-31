# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class odex25_helpdeskTicket(models.Model):
    _inherit = 'odex25_helpdesk.ticket'

    repairs_count = fields.Integer('Repairs Count', compute='_compute_repairs_count', compute_sudo=True)
    repair_ids = fields.One2many('repair.order', 'ticket_id', string='Repairs')

    @api.depends('repair_ids')
    def _compute_repairs_count(self):
        repair_data = self.env['repair.order'].sudo().read_group([('ticket_id', 'in', self.ids)], ['ticket_id'], ['ticket_id'])
        mapped_data = dict([(r['ticket_id'][0], r['ticket_id_count']) for r in repair_data])
        for ticket in self:
            ticket.repairs_count = mapped_data.get(ticket.id, 0)

    def action_view_repairs(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Repairs'),
            'res_model': 'repair.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.repair_ids.ids)],
            'context': dict(self._context, create=False, default_company_id=self.company_id.id, default_ticket_id=self.id),
        }
        if self.repairs_count == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.repair_ids.id
            })
        return action
