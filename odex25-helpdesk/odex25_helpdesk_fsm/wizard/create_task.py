# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CreateTask(models.TransientModel):
    _name = 'odex25_helpdesk.create.fsm.task'
    _description = 'Create a Field Service task'

    odex25_helpdesk_ticket_id = fields.Many2one('odex25_helpdesk.ticket', string='Related ticket', required=True)
    company_id = fields.Many2one(related='odex25_helpdesk_ticket_id.company_id')
    name = fields.Char('Title', required=True)
    project_id = fields.Many2one('project.project', string='Project', help='Project in which to create the task', required=True, domain="[('company_id', '=', company_id), ('is_fsm', '=', True)]")
    partner_id = fields.Many2one('res.partner', string='Customer', help="Ticket's customer, will be linked to the task", required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.model
    def default_get(self, fields_list):
        defaults = super(CreateTask, self).default_get(fields_list)
        if 'project_id' in fields_list and not defaults.get('project_id'):
            task_default = self.env['project.task'].with_context(fsm_mode=True).default_get(['project_id'])
            defaults.update({'project_id': task_default.get('project_id', False)})
        return defaults

    def action_generate_task(self):
        self.ensure_one()
        return self.env['project.task'].create({
            'name': self.name,
            'odex25_helpdesk_ticket_id': self.odex25_helpdesk_ticket_id.id,
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
        })

    def action_generate_and_view_task(self):
        self.ensure_one()
        new_task = self.action_generate_task()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks from Tickets'),
            'res_model': 'project.task',
            'res_id': new_task.id,
            'view_mode': 'form',
            'view_id': self.env.ref('project.view_task_form2').id,
            'context': {
                'fsm_mode': True,
            }
        }
