# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
from dateutil import relativedelta
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.osv import expression
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    phase_id = fields.Many2one('project.phase', string='Project Phase')
    time_plan_id = fields.Many2one('project.time.plan',string="Department - Project")
    department_id = fields.Many2one('hr.department',string="Department",related="time_plan_id.department_id",store=True)
    weight = fields.Float(string="Weight",compute="_compute_weight")
    task_progress_ids = fields.One2many('project.task.progress','task_id',string="Task Progress")
    week_ids = fields.Many2many('week.week', 'project_task_week_week_rel',
        'task_id', 'week_id',related="time_plan_id.week_ids",string="Week",store=True)

    @api.depends('planned_hours','time_plan_id','time_plan_id.time_plan')
    def _compute_weight(self):
        for rec in self:
            rec.weight=0
            if rec.planned_hours and rec.time_plan_id.time_plan:
                rec.weight = (rec.planned_hours / rec.time_plan_id.time_plan) *100

    @api.onchange('time_plan_id')
    def _onchange_time_plan_id(self):
        if self.time_plan_id:
            self.project_id = self.time_plan_id.project_id.id

    def _get_same_week(self,week):
        weeks= self.env['project.task.progress']
        for rec in self:
            week = self.task_progress_ids.filtered(lambda l: l.week_id.id == week.id)
            weeks +=week
        return weeks

    def get_progress_ids(self):
        TaskLine = self.env["project.task.progress"]
        print("----------------------------get_progress_ids")
        for rec in self:
            vals_list = []
            lines_week = rec.task_progress_ids.mapped('week_id')
            for week in rec.week_ids:
                if week.id not in lines_week.ids:
                    vals_list.append({'task_id':rec.id,'week_id':week.id,})
            rec.task_progress_ids = [(6, 0, TaskLine.create(vals_list).ids)]

    def write(self, vals):
        res = super().write(vals)
        print("--------------------vals.get('week_ids', False)",vals.get('week_ids', False))
        if vals.get('week_ids', False):
            self.get_progress_ids()
        return res

            
class ProjectTaskProgress(models.Model):
    _name = "project.task.progress"
    _description = "Task Progress"

    task_id = fields.Many2one('project.task',string="Task")
    week_id = fields.Many2one('week.week',string="Week")
    task_progress = fields.Float(string="Progress%",compute='_compute_progress',readonly=False,store=True, copy=False)

    @api.depends('task_id.child_ids','task_id.child_ids.task_progress_ids','task_id.child_ids.task_progress_ids.task_progress')
    def _compute_progress(self):
        for record in self:
            if record.task_id.child_ids:
                record.task_progress = sum(t.task_progress * t.task_id.weight for t in record.task_id.child_ids._get_same_week(record.week_id) )