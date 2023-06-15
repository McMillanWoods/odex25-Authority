# -*- coding: utf-8 -*-

from odoo import api, fields, models


class odex25_helpdeskTicketCreateTimesheet(models.TransientModel):
    _name = 'odex25_helpdesk.ticket.create.timesheet'
    _description = "Create Timesheet from ticket"

    _sql_constraints = [('time_positive', 'CHECK(time_spent > 0)', "The timesheet's time must be positive" )]

    time_spent = fields.Float('Time', digits=(16, 2))
    description = fields.Char('Description')
    ticket_id = fields.Many2one(
        'odex25_helpdesk.ticket', "Ticket", required=True,
        default=lambda self: self.env.context.get('active_id', None),
        help="Ticket for which we are creating a sales order",
    )

    def action_generate_timesheet(self):
        values = {
            'task_id': self.ticket_id.task_id.id,
            'project_id': self.ticket_id.project_id.id,
            'date': fields.Datetime.now(),
            'name': self.description,
            'user_id': self.env.uid,
            'unit_amount': self.time_spent,
        }

        timesheet = self.env['account.analytic.line'].create(values)

        self.ticket_id.write({
            'timer_start': False,
            'timer_pause': False
        })
        self.ticket_id.timesheet_ids = [(4, timesheet.id, None)]
        self.ticket_id.user_timer_id.unlink()
        return timesheet
