# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, fields, models


class ProjectPhase(models.Model):
    _name = 'project.phase'
    _description = 'Phase'
    _order = 'sequence'
    
    name = fields.Char(string='Phase Name',compute='_compute_name',store=True)
    stage_id = fields.Many2one('project.task.type',string="Phase")
    sequence = fields.Integer(string='Sequence')
    project_id = fields.Many2one('project.project',string='Project',default=lambda self: self.env.context.get('default_project_id'))
    start_date = fields.Date(string='Start Date', copy=False)
    end_date = fields.Date(string='End Date', copy=False)
    estimated_hours = fields.Float("Estimated Hours")
    department_ids = fields.Many2many('hr.department',string="Departments")
    company_id = fields.Many2one('res.company',related="project_id.company_id",string='Company')
    task_count = fields.Integer(compute="get_task",string='Count')
    weight = fields.Float(string="Stage Weight",compute="_compute_weight")
    notes = fields.Text(string='Notes')

    @api.depends('project_id.estimated_hours','estimated_hours')
    def _compute_weight(self):
        for rec in self:
            rec.weight=0
            if rec.origin_plan and rec.time_plan:
                rec.weight = (rec.time_plan / rec.origin_plan) *100

    @api.depends('stage_id')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.stage_id.name

    def action_project_phase_task(self):
        self.ensure_one()
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('phase_id', '=', self.id)],
        }

    def get_task(self):
        for rec in self:
            records = self.env['project.task'].search([('phase_id','=',rec.id)])
            rec.task_count = len(records)

    # def action_read_phase(self):
    #     self.ensure_one()
    #     return {
    #         'name': self.display_name,
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'tree',
    #         'view_mode': 'tree',
    #         'res_model': 'project.time.plan',
    #         'domain': [('phase_id','=',self.id),('project_id','=',self.project_id.id)],
    #         'view_id':self.env.ref('project_custom.project_time_plan_tree_project').id,
    #         # 'target':'new',
    #     }

    
