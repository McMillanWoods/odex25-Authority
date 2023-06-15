# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import datetime
import logging
_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "odex25_helpdesk.ticket"

    reminders_ids = fields.Many2many('helpdesk.sla.policy')
    # escalations_ids = fields.Many2many('helpdesk.sla.policy')


class HelpdeskSLA(models.Model):
    _inherit = "odex25_helpdesk.sla"

    reminder_ids = fields.One2many('helpdesk.sla.policy','sla_reminder_id')
    escalation_ids = fields.One2many('helpdesk.sla.policy','sla_escalation_id')

    @api.constrains('time_hours')
    def prevent_hours_morethan_workinghours(self):
        working_calendar = self.env.user.company_id.resource_calendar_id
        for rec in self:
            if working_calendar.is_full_day:
                if rec.time_hours > working_calendar.working_hours:
                    raise ValidationError(_("Hours Can't be more than working hours, Kindly! try again"))
            else:
                if rec.time_hours > working_calendar.shift_one_working_hours or rec.time_hours > working_calendar.shift_two_working_hours:
                    raise ValidationError(_("Hours Can't be more than working hours, Kindly! try again"))
                    
    @api.model
    def reminder_and_escalation(self):
        """
            send reminder and escalation according to sla policy
        """
        policies = self.env['odex25_helpdesk.sla'].search([])
        for sla in policies:
            if sla.reminder_ids:
                for reminder in sla.reminder_ids:
                    tickets = self.env['odex25_helpdesk.ticket'].search([('sla_id','=',sla.id),('reminders_ids','not in',reminder.id),('deadline','!=',None)])
                    _logger.error('length of tickets %s',len(tickets))
                    for ticket in tickets:
                        difference = fields.Datetime.from_string(ticket.deadline) - datetime.datetime.now()
                        difference = str(difference).split(',')
                        hour, minute = divmod(reminder.reminder_hours, 1)
                        minute *= 60
                        result = '{}:{}'.format(int(hour), int(minute))
                        result = result.split(':')
                        if len(difference) == 2:
                            days = int(difference[0].split(' ')[0])
                            hours = int(difference[1].split(':')[0])
                            minutes = int(difference[1].split(':')[1])
                        else:
                            days = 0
                            hours = int(difference[0].split(':')[0])
                            minutes = int(difference[0].split(':')[1])
                        if days <= reminder.reminder_days:
                            if hours < int(result[0]):
                                if ticket.sla_id.stage_id.id != ticket.stage_id.id:
                                    template = self.env.ref('helpdesk_sla_escalation_reminder.ticket_sla_reminder')
                                    template.email_to = ticket.user_id.partner_id.email
                                    times = str(days) + _('Days, ') + str(hours) + _(' Hours and ') + str(minutes) + _(' Minutes')
                                    if ticket.user_id:
                                        to = ticket.user_id.name
                                    else:
                                        to = _("Madam, Sir")
                                    template.sudo().with_context({
                                            'time_untill':times,
                                            'mail_to': to,
                                            'lang':self.env.user.lang,
                                        }).send_mail(ticket.id, force_send=True, raise_exception=False)
                                    ticket.write({'reminders_ids': [(4, reminder.id, 0)]})
                            elif hours == int(result[0]):
                                if minutes <= int(result[1]):
                                    if ticket.sla_id.stage_id.id != ticket.stage_id.id:
                                        template = self.env.ref('helpdesk_sla_escalation_reminder.ticket_sla_reminder')
                                        template.email_to = ticket.user_id.partner_id.email
                                        times = str(days) + _('Days, ') + str(hours) + _(' Hours and ') + str(minutes) + _(' Minutes')
                                        if ticket.user_id:
                                            to = ticket.user_id.name
                                        else:
                                            to = _("Madam, Sir")
                                        template.sudo().with_context({
                                            'time_untill':times,
                                            'mail_to': to,
                                            'lang':self.env.user.lang,
                                        }).send_mail(ticket.id, force_send=True, raise_exception=False)
                                        ticket.write({'reminders_ids': [(4, reminder.id, 0)]})
                            elif days <= -1:
                                if ticket.sla_id.stage_id.id != ticket.stage_id.id:
                                    template = self.env.ref('helpdesk_sla_escalation_reminder.ticket_sla_reminder')
                                    template.email_to = ticket.user_id.partner_id.email
                                    times = str(days) + _('Days, ') + str(hours) + _(' Hours and ') + str(minutes) + _(' Minutes')
                                    if ticket.user_id:
                                        to = ticket.user_id.name
                                    else:
                                        to = _("Madam, Sir")
                                    template.sudo().with_context({
                                            'time_untill':times,
                                            'mail_to': to,
                                            'lang':self.env.user.lang,
                                        }).send_mail(ticket.id, force_send=True, raise_exception=False)
                                    ticket.write({'reminders_ids': [(4, reminder.id, 0)]})
                        else:
                            continue
            if sla.escalation_ids:
                for escalation in sla.escalation_ids:
                    tickets = self.env['odex25_helpdesk.ticket'].search([('sla_id','=',sla.id),('reminders_ids','not in',escalation.id),('deadline','!=',None)])
                    _logger.error('length of tickets %s',len(tickets))
                    for ticket in tickets:
                        difference = datetime.datetime.now() - fields.Datetime.from_string(ticket.deadline)
                        difference = str(difference).split(',')
                        hour, minute = divmod(escalation.reminder_hours, 1)
                        minute *= 60
                        result = '{}:{}'.format(int(hour), int(minute))
                        result = result.split(':')
                        if len(difference) == 2:
                            days = int(difference[0].split(' ')[0])
                            hours = int(difference[1].split(':')[0])
                            minutes = int(difference[1].split(':')[1])
                        else:
                            days = 0
                            hours = int(difference[0].split(':')[0])
                            minutes = int(difference[0].split(':')[1])
                        if days >= escalation.reminder_days:
                            if hours > int(result[0]):
                                if ticket.sla_id.stage_id.id != ticket.stage_id.id:
                                    template = self.env.ref('odex25_helpdesk_sla_escalation_reminder.ticket_sla_escalation')
                                    template.email_to = escalation.user_id.partner_id.email
                                    times = str(days) + _('Days, ') + str(hours) + _(' Hours and ') + str(minutes) + _(' Minutes')
                                    if escalation.user_id:
                                        to = escalation.user_id.name
                                    else:
                                        to = _("Madam, Sir")
                                    template.sudo().with_context({
                                            'time_untill':times,
                                            'mail_to': to,
                                            'lang':self.env.user.lang,
                                        }).send_mail(ticket.id, force_send=True, raise_exception=False)
                                    ticket.write({'reminders_ids': [(4, escalation.id, 0)]})
                            elif hours == int(result[0]):
                                if minutes >= int(result[1]):
                                    if ticket.sla_id.stage_id.id != ticket.stage_id.id:
                                        template = self.env.ref('helpdesk_sla_escalation_reminder.ticket_sla_escalation')
                                        template.email_to = escalation.user_id.partner_id.email
                                        times = str(days) + _('Days, ') + str(hours) + _(' Hours and ') + str(minutes) + _(' Minutes')
                                        if escalation.user_id:
                                            to = escalation.user_id.name
                                        else:
                                            to = _("Madam, Sir")
                                        template.sudo().with_context({
                                                'time_untill':times,
                                                'mail_to': to,
                                                'lang':self.env.user.lang,
                                        }).send_mail(ticket.id, force_send=True, raise_exception=False)
                                        ticket.write({'reminders_ids': [(4, escalation.id, 0)]})
                        else:
                            continue


class HelpdeskSLAReminderPolicy(models.Model):
    _name = 'helpdesk.sla.policy'

    sla_reminder_id = fields.Many2one('odex25_helpdesk.sla')
    sla_escalation_id = fields.Many2one('odex25_helpdesk.sla')
    team_id = fields.Many2one(related="sla_reminder_id.team_id",store=True)

    type = fields.Selection([
        ('after','After'),
        ('before','Before'),
    ])
    reminder_hours = fields.Float()
    reminder_days = fields.Integer()
    user_id = fields.Many2one('res.users')

    @api.constrains('reminder_hours','reminder_days')
    def _prevent_zero(self):
        """
            Prevent the time to be zero if the days are zero
        """
        if self.reminder_days < 0.0 or self.reminder_hours < 0.0:
            raise ValidationError(_("Kindly, make sure that time is not less than zero"))
        if self.reminder_days == 0.0 and self.reminder_hours <= 0.0:
            raise ValidationError(_("Kindly, make sure that time is not less than or equal zero"))

    @api.onchange('team_id')
    def _domain_user_to_sla(self):
        """
            return domain in users
        """
        users = []
        if self.sla_reminder_id:
            users = self.sla_reminder_id.team_id.members_ids.mapped('member_id').ids
            users.append(self.sla_reminder_id.team_id.team_leader_id.id)
        if self.sla_escalation_id:
            users = self.sla_escalation_id.team_id.members_ids.mapped('member_id').ids
            users.append(self.sla_escalation_id.team_id.team_leader_id.id)
        return{
            'domain':{'user_id':[('id','in',users)]}
        }