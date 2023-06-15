# -*- coding: utf-8 -*-

from odoo import api, models,fields
from odoo.addons.http_routing.models.ir_http import slug


class HelpdeskTeam(models.Model):
    _name = "odex25_helpdesk.team"
    _inherit = ['odex25_helpdesk.team', 'website.published.mixin']




    def _compute_website_url(self):
        super(HelpdeskTeam, self)._compute_website_url()
        for team in self:
            team.website_url = "/odex25_helpdesk/%s" % slug(team)

    @api.onchange('use_website_helpdesk_form', 'use_website_helpdesk_forum', 'use_website_helpdesk_slides')
    def _onchange_use_website_helpdesk(self):
        if not (self.use_website_helpdesk_form or self.use_website_helpdesk_forum or self.use_website_helpdesk_slides) and self.website_published:
            self.is_published = False

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            vals['is_published'] = False
        return super(HelpdeskTeam, self).write(vals)

    def action_view_all_rating(self):
        """ Override this method without calling parent to redirect to rating website team page """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Redirect to the Website Helpdesk Rating Page",
            'target': 'self',
            'url': "/odex25_helpdesk/rating/"
        }
