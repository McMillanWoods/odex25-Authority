# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError




class CalendarEventPlace(models.Model):
    _name = 'calendar.event.room'

    name = fields.Char("Name", required=True)
    branch_id = fields.Many2one("res.branch", string="Branch")
    team_id = fields.Many2one("odex25_helpdesk.team", string="Technical Team")


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    event_room_id = fields.Many2one("calendar.event.room", string="Meeting Room")
    is_tech_service = fields.Boolean("Technical Services ?")

    @api.constrains('event_room_id', 'start', 'stop', 'allday')
    def _check_date(self):
        for event in self :
            if event.event_room_id :
                domain = [
                ('start', '<', event.stop),
                ('stop', '>', event.start),
                ('event_room_id', '=', event.event_room_id.id),
                ('id', '!=', event.id),
            ]
                nevents = self.search_count(domain)
                if nevents:
                    raise ValidationError(_('Meeting room is not available at this time !'))


    def create_notify(self):
        notification_vals = []
        if self.user_id :
            notification_vals.append((0, 0, {'notification_type' : 'inbox', 'res_partner_id' : self.user_id.partner_id.id}))
        
        if self.is_tech_service :
            if self.event_room_id and self.event_room_id.team_id.team_leader_id :
                notification_vals.append((0, 0, {'notification_type' : 'inbox', 'res_partner_id' : self.event_room_id.team_id.team_leader_id.partner_id.id}))
            for user in self.event_room_id.team_id.member_ids :
                notification_vals.append((0, 0, {'notification_type' : 'inbox', 'res_partner_id' : user.partner_id.id}))
        if notification_vals :
            self.env['mail.message'].create({
                'message_type':"notification",
                'body': _("New Meeting At %s")%(self.start),
                'subject': _("New Meeting"),
                'model': self._name,
                'res_id': self.id,
                'partner_ids' : [self.user_id.partner_id.id],
                'notification_ids' : notification_vals,
            })


    def update_notify(self, vals={}):
        notification_vals = []
        if self.user_id :
            notification_vals.append((0, 0, {'notification_type' : 'inbox', 'res_partner_id' : self.user_id.partner_id.id}))
        
        if self.is_tech_service or 'is_tech_service' in vals :
            if self.event_room_id.team_id.team_leader_id :
                notification_vals.append((0, 0, {'notification_type' : 'inbox', 'res_partner_id' : self.event_room_id.team_id.team_leader_id.partner_id.id}))
        for user in self.event_room_id.team_id.member_ids :
                notification_vals.append((0, 0, {'notification_type' : 'inbox', 'res_partner_id' : user.partner_id.id}))
                
        if notification_vals :
            self.env['mail.message'].create({
                'message_type':"notification",
                'body': _("Meeting Details has been Update"),
                'subject': _("Meeting Update"),
                'model': self._name,
                'res_id': self.id,
                'partner_ids' : [self.user_id.partner_id.id],
                'notification_ids' : notification_vals,
            })
        
    @api.model
    def create(self, vals):
        obj = super(CalendarEvent, self).create(vals)
        obj.create_notify()
        return obj

    def write(self, vals) :
        res = super(CalendarEvent, self).write(vals)
        if self.user_id :
            if "start" in vals or "stop" in vals or 'event_room_id' in vals or 'is_tech_service' in vals:
                self.update_notify(vals)        
