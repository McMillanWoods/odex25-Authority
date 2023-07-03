# -*- coding: utf-8 -*-

import datetime

from odoo import http
from odoo.http import request
from odoo.osv.expression import AND


class Websiteodex25_helpdesk(http.Controller):

    @http.route(['/odex25_helpdesk/rating', '/odex25_helpdesk/rating/<model("odex25_helpdesk.team"):team>'], type='http', auth="public", website=True, sitemap=True)
    def page(self, team=False, **kw):
        # to avoid giving any access rights on Helpdesk team to the public user, let's use sudo
        # and check if the user should be able to view the team (team managers only if it's not published or has no rating)
        user = request.env.user
        team_domain = [('id', '=', team.id)] if team else []
        if user.has_group('odex25_helpdesk.group_heldpesk_manager'):
            domain = AND([[('use_rating', '=', True)], team_domain])
        else:
            domain = AND([[('use_rating', '=', True), ('portal_show_rating', '=', True)], team_domain])
        teams = request.env['odex25_helpdesk.team'].search(domain)
        team_values = []
        for team in teams:
            tickets = request.env['odex25_helpdesk.ticket'].sudo().search([('team_id', '=', team.id)])
            domain = [
                ('res_model', '=', 'odex25_helpdesk.ticket'), ('res_id', 'in', tickets.ids),
                ('consumed', '=', True), ('rating', '>=', 1),
            ]
            ratings = request.env['rating.rating'].sudo().search(domain, order="id desc", limit=100)

            yesterday = (datetime.date.today()-datetime.timedelta(days=-1)).strftime('%Y-%m-%d 23:59:59')
            stats = {}
            any_rating = False
            for x in (7, 30, 90):
                todate = (datetime.date.today()-datetime.timedelta(days=x)).strftime('%Y-%m-%d 00:00:00')
                domdate = domain + [('create_date', '<=', yesterday), ('create_date', '>=', todate)]
                stats[x] = {1: 0, 3: 0, 5: 0}
                rating_stats = request.env['rating.rating'].sudo().read_group(domdate, [], ['rating'])
                total = sum(st['rating_count'] for st in rating_stats)
                for rate in rating_stats:
                    any_rating = True
                    stats[x][rate['rating']] = (rate['rating_count'] * 100) / total
            values = {
                'team': team,
                'ratings': ratings if any_rating else False,
                'stats': stats,
            }
            team_values.append(values)
        return request.render('odex25_helpdesk.team_rating_page', {'page_name': 'rating', 'teams': team_values})
