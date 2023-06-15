# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.odex25_website_helpdesk.controllers.main import WebsiteHelpdesk


class WebsiteHelpdesk(WebsiteHelpdesk):

    def get_helpdesk_team_data(self, team, search=None):
        result = super(WebsiteHelpdesk, self).get_helpdesk_team_data(team, search)
        result['forum'] = team.forum_id
        domain = []
        if search:
            domain += [('name', 'ilike', search)]
        if team.forum_id:
            domain += [('forum_id', '=', result['forum'].id), ('parent_id', '=', False)]
            questions = request.env['forum.post'].search(domain)
            result['questions'] = questions[:10]
            result['questions_limit'] = len(questions)
            result['search'] = search
        return result
