# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.addons.odex25_helpdesk.models.odex25_helpdesk_ticket import TICKET_PRIORITY


class odex25_helpdeskSLAReport(models.Model):
    _name = 'odex25_helpdesk.sla.report.analysis'
    _description = "SLA Status Analysis"
    _auto = False
    _order = 'create_date DESC'

    ticket_id = fields.Many2one('odex25_helpdesk.ticket', string='Ticket', readonly=True)
    create_date = fields.Date("Ticket Create Date", readonly=True)
    priority = fields.Selection(TICKET_PRIORITY, string='Minimum Priority', readonly=True)
    user_id = fields.Many2one('res.users', string="Assigned To", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    ticket_type_id = fields.Many2one('odex25_helpdesk.ticket.type', string="Ticket Type", readonly=True)
    ticket_stage_id = fields.Many2one('odex25_helpdesk.stage', string="Ticket Stage", readonly=True)
    ticket_deadline = fields.Datetime("Ticket Deadline", readonly=True)
    ticket_failed = fields.Boolean("Ticket Failed", group_operator="bool_or", readonly=True)
    ticket_closed = fields.Boolean("Ticket Closed", readonly=True)
    ticket_close_hours = fields.Integer("Time to close (hours)", group_operator="avg", readonly=True)
    ticket_open_hours = fields.Integer("Open Time (hours)", group_operator="avg", readonly=True)
    ticket_assignation_hours = fields.Integer("Time to first assignment (hours)", group_operator="avg", readonly=True)

    sla_id = fields.Many2one('odex25_helpdesk.sla', string="SLA", readonly=True)
    sla_stage_id = fields.Many2one('odex25_helpdesk.stage', string="SLA Stage", readonly=True)
    sla_deadline = fields.Datetime("SLA Deadline", group_operator='min', readonly=True)
    sla_reached_datetime = fields.Datetime("SLA Reached Date", group_operator='min', readonly=True)
    sla_status = fields.Selection([('failed', 'Failed'), ('reached', 'Reached'), ('ongoing', 'Ongoing')], string="Status", readonly=True)
    sla_status_failed = fields.Boolean("SLA Status Failed", group_operator='bool_or', readonly=True)
    sla_exceeded_days = fields.Integer("Day to reach SLA", group_operator='avg', readonly=True, help="Day to reach the stage of the SLA, without taking the working calendar into account")

    team_id = fields.Many2one('odex25_helpdesk.team', string='Team', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'odex25_helpdesk_sla_report_analysis')
        self.env.cr.execute("""
            CREATE VIEW odex25_helpdesk_sla_report_analysis AS (
                SELECT
                    ST.id as id,
                    T.create_date AS create_date,
                    T.id AS ticket_id,
                    T.team_id,
                    T.stage_id AS ticket_stage_id,
                    T.ticket_type_id,
                    T.user_id,
                    T.partner_id,
                    T.company_id,
                    T.priority AS priority,
                    T.sla_reached_late OR T.sla_deadline < NOW() AT TIME ZONE 'UTC' AS ticket_failed,
                    T.sla_deadline AS ticket_deadline,
                    T.close_hours AS ticket_close_hours,
                    EXTRACT(HOUR FROM (COALESCE(T.assign_date, NOW()) - T.create_date)) AS ticket_open_hours,
                    T.assign_hours AS ticket_assignation_hours,
                    STA.is_close AS ticket_closed,
                    ST.sla_id,
                    SLA.stage_id AS sla_stage_id,
                    ST.deadline AS sla_deadline,
                    ST.reached_datetime AS sla_reached_datetime,
                    ST.exceeded_days AS sla_exceeded_days,
                    CASE
                        WHEN ST.reached_datetime IS NOT NULL AND ST.reached_datetime < ST.deadline THEN 'reached'
                        WHEN ST.reached_datetime IS NOT NULL AND ST.reached_datetime >= ST.deadline THEN 'failed'
                        WHEN ST.reached_datetime IS NULL AND ST.deadline > NOW() THEN 'ongoing'
                        ELSE 'failed'
                    END AS sla_status,
                    ST.reached_datetime >= ST.deadline OR (ST.reached_datetime IS NULL AND ST.deadline < NOW() AT TIME ZONE 'UTC') AS sla_status_failed
                FROM odex25_helpdesk_ticket T
                    LEFT JOIN odex25_helpdesk_stage STA ON (T.stage_id = STA.id)
                    LEFT JOIN odex25_helpdesk_sla_status ST ON (T.id = ST.ticket_id)
                    LEFT JOIN odex25_helpdesk_sla SLA ON (ST.sla_id = SLA.id)
                )
            """)
