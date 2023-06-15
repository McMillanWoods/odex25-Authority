# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from odoo import models, fields, api
from odoo.tools.misc import format_date
import pytz
import dateutil.parser


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_start_date = fields.Datetime(string="Project Start Date",
                                         default=datetime.today())


def check_gantt_date(value):
    if isinstance(value, str):
        return dateutil.parser.parse(value, ignoretz=True)
    else:
        return value


class ProjectTask(models.Model):
    _inherit = 'project.task'

    duration = fields.Integer(string="Duration (days)", default=-1)
    duration_unit = fields.Char(string="Duration Unit", default='d')

    percent_done = fields.Integer(string="Done %", default=0)
    parent_index = fields.Integer(string="Parent Index", default=0)

    assigned_ids = fields.Many2many('res.users', relation='assigned_resources', string="Assigned resources")
    assigned_resources = fields.One2many('project.task.assignment',
                                     inverse_name='task',
                                     string='Assignments')

    baselines = fields.One2many('project.task.baseline',
                                      inverse_name='task',
                                      string='Baselines')

    effort = fields.Integer(string="Effort (hours)", default=0)
    gantt_calendar = fields.Selection([
        ('general', 'General'),
        ('business', 'Business'),
        ('night', 'Night shift')
    ], string="Gantt Calendar", default='general')
    linked_ids = fields.One2many('project.task.linked',
                                 inverse_name='to_id',
                                 string='Linked')
    scheduling_mode = fields.Selection([
        ('Normal', 'Normal'),
        ('FixedDuration', 'Fixed Duration'),
        ('FixedEffort', 'Fixed Effort'),
        ('FixedUnits', 'Fixed Units')
    ], string='Scheduling Mode')
    constraint_type = fields.Selection([
        ('muststarton', 'Must start on'),
        ('mustfinishon', 'Must finish on'),
        ('startnoearlierthan', 'Start no earlier than'),
        ('startnolaterthan', 'Start no later than'),
        ('finishnoearlierthan', 'Finish no earlier than'),
        ('finishnolaterthan', 'Finish no later than')
    ], string='Constraint Type')
    constraint_date = fields.Datetime(string="Constraint Date")
    effort_driven = fields.Boolean(string="Effort Driven", default=False)
    manually_scheduled = fields.Boolean(string="Manually Scheduled",
                                        default=False)

    def write(self, vals):
        response = super(ProjectTask, self).write(vals)
        # one_day = timedelta(days=1)
        #
        # if 'planned_date_end' in vals:
        #     end_date = check_gantt_date(vals['planned_date_end'])
        #
        #     if isinstance(end_date, bool) or end_date is None:
        #         return response
        #
        #     if not self.planned_date_begin:
        #         self.planned_date_begin = end_date - one_day
        #     if self.planned_date_begin >= end_date:
        #         self.planned_date_end = self.planned_date_begin + one_day
        #
        # if 'planned_date_begin' in vals:
        #     begin_date = check_gantt_date(vals['planned_date_begin'])
        #
        #     if isinstance(begin_date, bool) or begin_date is None:
        #         return response
        #
        #     if not self.planned_date_end:
        #         self.planned_date_end = begin_date + one_day
        #     if self.planned_date_end <= begin_date:
        #         self.planned_date_begin = self.planned_date_end - one_day

        return response

    @api.onchange('constraint_type')
    def _onchange_constraint_type(self):
        if not self.constraint_type:
            self.constraint_date = None
        else:
            self.constraint_date = {
                'muststarton': self.planned_date_begin,
                'mustfinishon': self.planned_date_end,
                'startnoearlierthan': self.planned_date_begin,
                'startnolaterthan': self.planned_date_begin,
                'finishnoearlierthan': self.planned_date_end,
                'finishnolaterthan': self.planned_date_end
            }[self.constraint_type]


class ProjectTaskLinked(models.Model):
    _name = 'project.task.linked'
    _description = 'Project Task Linked'

    from_id = fields.Many2one('project.task', ondelete='cascade', string='From')
    to_id = fields.Many2one('project.task', ondelete='cascade', string='To')
    lag = fields.Integer(string="Lag", default=0)
    lag_unit = fields.Char(string="Lag Unit", default='d')


class ProjectTaskAssignmentUser(models.Model):
    _name = 'project.task.assignment'
    _description = 'Project Task User Assignment'

    task = fields.Many2one('project.task', ondelete='cascade', string='Task')
    resource = fields.Many2one('res.users', ondelete='cascade', string='Resource')
    units = fields.Integer(string="Units", default=0)

class ProjectTaskBaseline(models.Model):
    _name = 'project.task.baseline'
    _description = 'Project Task User Assignment'

    task = fields.Many2one('project.task', ondelete='cascade', string='Task')
    name = fields.Char(string="Name", default='')
    planned_date_begin = fields.Datetime("Start date")
    planned_date_end = fields.Datetime("End date")
