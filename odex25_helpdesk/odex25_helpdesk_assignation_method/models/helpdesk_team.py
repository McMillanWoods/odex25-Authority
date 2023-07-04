# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "odex25_helpdesk.ticket"

    team_leader_id = fields.Many2one(related='team_id.team_leader_id')

    @api.onchange('service_id')
    def get_user_and_assign_it(self):
        for rec in self:
            result = rec._onchange_ticket_type_values(rec.team_id,rec.service_id)
            rec.user_id = result['user_id']

    def _onchange_ticket_type_values(self, team, ticket_type=None):
        return {
            'user_id': team.get_new_user(ticket_type),
        }


    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        result = self._onchange_ticket_type_values(res.team_id,res.service_id)
        res.user_id = result['user_id']
        return res

class HelpdeskTeam(models.Model):
    _inherit = "odex25_helpdesk.team"

    team_leader_id = fields.Many2one('res.users',domain=lambda self: [('groups_id', 'in', self.env.ref('odex25_helpdesk.group_odex25_helpdesk_manager').id)])
    members_ids = fields.One2many('helpdesk.team.member','team_id')
    member_ids = fields.Many2many('res.users', string='Team Members', domain=lambda self: [('groups_id', 'in', self.env.ref('odex25_helpdesk.group_odex25_helpdesk_user').id)])

    @api.onchange('members_ids')
    def _onchange_members_ids(self):
        """
            update the member_ids based on members_ids
        """
        for team in self:
            for rec in team.member_ids:
                rec = False
            members = [member.member_id.id for member in self.members_ids]
            addmember = [(6,0,members)]
            team.update({
                'member_ids': addmember
            })

    @api.constrains('assign_method', 'members_ids')
    def _check_members_assignation(self):
        if not self.members_ids and self.assign_method != 'manual':
            raise ValidationError(_("You must have team members assigned to change the assignation method."))

    def get_new_user(self, ticket_type=None):
        for rec in self:
            rec.ensure_one()
            new_user = self.env['res.users']
            members_ids = []
            if ticket_type:
                for member in rec.members_ids:
                    if ticket_type in member.service_id:
                        members_ids.append(member.member_id.id)
                members_ids = sorted(members_ids)
            elif len(members_ids) == 0:
                members_ids = sorted([member.member_id.id for member in rec.members_ids])
            if members_ids:
                if rec.assign_method == 'randomly':
                    # randomly means new ticketss get uniformly distributed
                    previous_assigned_user = self.env['odex25_helpdesk.ticket'].search([('team_id', '=', rec.id)], order='create_date desc', limit=1).user_id
                    # handle the case where the previous_assigned_user has left the team (or there is none).
                    if previous_assigned_user and previous_assigned_user.id in members_ids:
                        previous_index = members_ids.index(previous_assigned_user.id)
                        new_user = new_user.browse(members_ids[(previous_index + 1) % len(members_ids)])
                    else:
                        new_user = new_user.browse(members_ids[0])
                elif rec.assign_method == 'balanced':
                    read_group_res = self.env['odex25_helpdesk.ticket'].read_group([('stage_id.is_close', '=', False), ('user_id', 'in', members_ids)], ['user_id'], ['user_id'])
                    # add all the members in case a member has no more open tickets (and thus doesn't appear in the previous read_group)
                    count_dict = dict((m_id, 0) for m_id in members_ids)
                    count_dict.update((data['user_id'][0], data['user_id_count']) for data in read_group_res)
                    new_user = new_user.browse(min(count_dict, key=count_dict.get))
            return new_user
    

class HelpdeskTeamMemebers(models.Model):
    _name = "helpdesk.team.member"

    team_id = fields.Many2one('odex25_helpdesk.team')
    member_id = fields.Many2one('res.users',domain=lambda self: [('groups_id', 'in', self.env.ref('odex25_helpdesk.group_odex25_helpdesk_user').id)])
    # ticket_type_ids = fields.Many2many('odex25_helpdesk.ticket.type')
    service_id = fields.Many2many('helpdesk.service')

#
#
# class InheritUser(models.Model):
#     _inherit = 'res.users'
#
#     @api.model
#     def name_search(self, name='', args=None, operator='ilike', limit=100):
#         if self._context.get('members', []):
#             member_id = self.env['odex25_helpdesk.team'].new('members_ids',self._context.get('members', []))
#             args.append(('id', 'not in',
#                          [isinstance(d['member_id'], tuple) and d['member_id'][0] or d['member_id']
#                           for d in member_id]))
#         return super(InheritUser, self).name_search(name, args=args, operator=operator, limit=limit)