# -*- coding: utf-8 -*-

from datetime import date,datetime, time, timedelta
from babel.dates import format_date
from dateutil.relativedelta import relativedelta
from dateutil import rrule
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.osv import expression
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from collections import namedtuple



class ProjectTimePlan(models.Model):
    _name = "project.time.plan"
    _description = "Time Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # name = fields.Char("Number",default='/',tracking=True)
    department_id = fields.Many2one('hr.department',string="Department",tracking=True)
    project_id = fields.Many2one('project.project',string='Project',tracking=True)
    phase_id = fields.Many2one('project.phase',string='Project Stage',tracking=True)
    start_date = fields.Date(string="From",related='phase_id.start_date')
    end_date = fields.Date(string="To",related='phase_id.end_date')
    origin_plan = fields.Float(string="Stage Total Hours",related="phase_id.estimated_hours")
    time_plan = fields.Float(string="Estimated Hours")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('close','Closed')], string='Status',
        copy=False, default='draft', required=True,tracking=True)
    week_ids = fields.Many2many('week.week',string="Week")
    line_ids = fields.One2many('project.time.plan.line','plan_id')
    task_ids = fields.One2many('project.task','time_plan_id',string="Tasks")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.department_id.name or '' +'-'+ rec.project_id.name or ''
            result.append((rec.id, name))
        return result

    @api.onchange('phase_id')
    def _onchange_phase_id(self):
        weeks = []
        if self.phase_id:
            weeks = self._get_weeks(self.phase_id.start_date,self.phase_id.end_date)
        self.week_ids =  [(6, 0, weeks)]
        
    def write(self, vals):
        res = super().write(vals)
        if vals.get('week_ids', False):
            self.get_line_ids()
            self.task_ids.get_progress_ids()
        return res

    def _get_weeks(self,start_date,end_date):
        WEEK_OBJ = self.env['week.week']
        self.env.cr.execute("""
                        SELECT id
                        FROM week_week
                        WHERE date_from between %s AND %s OR date_to between %s AND %s""",
                        (fields.Date.to_string(start_date),fields.Date.to_string(end_date),fields.Date.to_string(start_date),fields.Date.to_string(end_date)))
        weeks = list(w[0] for w in self.env.cr.fetchall())
        return weeks

    def get_line_ids(self):
        PlanLine = self.env["project.time.plan.line"]
        for plan in self:
            vals_list = []
            for week in plan.week_ids:
                vals_list.append({'plan_id':plan.id,'week_id':week.id,'department_id':plan.department_id.id})
            plan.line_ids = [(6, 0, PlanLine.create(vals_list).ids)]

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_close(self):
        self.write({'state': 'close'})


class ProjectTimePlan(models.Model):
    _name = "project.time.plan.line"
    _description = "Time Plan Details"

    plan_id = fields.Many2one('project.time.plan',ondelete="cascade")
    week_id = fields.Many2one('week.week',string="Week")
    project_id = fields.Many2one(comodel_name="project.project", string="Project")
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    time_plan = fields.Float(string="Hours", default=0.0)
    progress = fields.Float(string="Progress")


# class ProjectTimePlanReport(models.Model):
#     _name = "project.time.plan.report"
#     _description = "Time Plan for Department"
#     _inherit = ['mail.thread', 'mail.activity.mixin']

#     department_id = fields.Many2one('hr.department',string="Department",tracking=True)
#     project_id = fields.Many2one('project.project',string='Project',tracking=True)
#     time_plan_ids = fields.One2many('project.time.plan','department_id',domain=[('project_id', '=', project_id.id)])
#     task_ids = fields.One2many('project.task','department_id',domain=[('project_id', '=', project_id.id)])
#     department_weight = fields.Float(string="Department Weight",compute="_compute_weight")

#     @api.depends('origin_plan','time_plan')
#     def _compute_weight(self):
#         for rec in self:
#             rec.department_weight=0
#             if rec.origin_plan and rec.time_plan:
#                 rec.department_weight = (rec.time_plan / rec.origin_plan) *100
