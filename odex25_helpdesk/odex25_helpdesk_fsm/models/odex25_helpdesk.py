# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class odex25_helpdeskTeam(models.Model):
    _inherit = 'odex25_helpdesk.team'

    use_fsm = fields.Boolean('Onsite Interventions', help='Convert tickets into Field Service tasks')


class odex25_helpdeskTicket(models.Model):
    _inherit = 'odex25_helpdesk.ticket'

    use_fsm = fields.Boolean(related='team_id.use_fsm')
    fsm_task_ids = fields.One2many('project.task', 'odex25_helpdesk_ticket_id', string='Tasks', help='Tasks generated from this ticket', domain=[('is_fsm', '=', True)])
    fsm_task_count = fields.Integer(compute='_compute_fsm_task_count')

    @api.depends('fsm_task_ids')
    def _compute_fsm_task_count(self):
        ticket_groups = self.env['project.task'].read_group([('is_fsm', '=', True), ('odex25_helpdesk_ticket_id', '!=', False)], ['id:count_distinct'], ['odex25_helpdesk_ticket_id'])
        ticket_count_mapping = dict(map(lambda group: (group['odex25_helpdesk_ticket_id'][0], group['odex25_helpdesk_ticket_id_count']), ticket_groups))
        for ticket in self:
            ticket.fsm_task_count = ticket_count_mapping.get(ticket.id, 0)

    def action_view_fsm_tasks(self):
        fsm_form_view = self.env.ref('project.view_task_form2')
        fsm_list_view = self.env.ref('odex25_industry_fsm.project_task_view_list_fsm')
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
        }

        if len(self.fsm_task_ids) == 1:
            action.update(res_id=self.fsm_task_ids[0].id, views=[(fsm_form_view.id, 'form')])
        else:
            action.update(domain=[('id', 'in', self.fsm_task_ids.ids)], views=[(fsm_list_view.id, 'tree'), (fsm_form_view.id, 'form')], name=_('Tasks from Tickets'))
        return action

    def action_generate_fsm_task(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create a Field Service task'),
            'res_model': 'odex25_helpdesk.create.fsm.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'use_fsm': True,
                'default_odex25_helpdesk_ticket_id': self.id,
                'default_user_id': False,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
                'default_name': self.name,
            }
        }
