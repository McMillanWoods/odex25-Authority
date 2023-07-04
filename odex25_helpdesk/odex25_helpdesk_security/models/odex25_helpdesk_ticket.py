# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import  ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'odex25_helpdesk.ticket'

    @api.model
    def create(self, vals):
        """
            prevent creating ticket for other teams for normal users
        """
        if 'team_id' in vals:
            team = self.env['odex25_helpdesk.team'].browse(vals['team_id'])
            if not team.team_leader_id and not team.member_ids and not self.env.user.has_group('odex25_helpdesk_security.group_helpdesk_normal_manager'):
                raise ValidationError(
                    _("Can't create ticket in team without leader and members except for helpdesk manager"))

            if team.team_leader_id and not team.member_ids and self.env.user.id != team.team_leader_id.id:
                raise ValidationError(
                    _("Can't create ticket in team , only team leader can create ticket in this channel"))

        if self.env.user.has_group('odex25_helpdesk_security.group_helpdesk_normal_user'):
            if 'team_id' in vals and vals['team_id']:
                team = self.env['odex25_helpdesk.team'].search([('id','=',vals['team_id'])])
                members = [member.id for member in team.member_ids]
                members.append(team.team_leader_id.id)
                if self.env.user.id not in members:
                    raise ValidationError(_("You're not allowed to create ticket in this team, please select a team that you are a member in."))
        res = super(HelpdeskTicket,self).create(vals)
        return res

    def unlink(self):
        """
            prevent deleting for normal users
        """
        if self.env.user.has_group('odex25_helpdesk_security.group_helpdesk_normal_user'):
            raise ValidationError(_("You don't have permission to delete this record, please contact Helpdesk Manager"))
        return super(HelpdeskTicket,self).unlink()


class HelpdeskStage(models.Model):
    _inherit = 'odex25_helpdesk.stage'

    def unlink(self):
        """
            prevent deleting for normal users
        """
        if self.env.user.has_group('odex25_helpdesk_security.group_helpdesk_normal_user'):
            raise ValidationError(_("You don't have permission to delete this record, please contact Helpdesk Manager"))
        return super(HelpdeskStage,self).unlink()

    # @api.multi
    # def write(self,vals):
    #     """
    #         prevent writing for normal users
    #     """
    #     if self.env.user.has_group('odex25_helpdesk_security.group_helpdesk_normal_user'):
    #         raise ValidationError(_("You don't have permission to  this record, please contact Helpdesk Manager"))
    #     return super(HelpdeskStage,self).unlink()