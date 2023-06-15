# -*- coding: utf-8 -*-
from odoo import http

# class OdexOnlineTendering(http.Controller):
#     @http.route('/odex_online_tendering/odex_online_tendering/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odex_online_tendering/odex_online_tendering/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odex_online_tendering.listing', {
#             'root': '/odex_online_tendering/odex_online_tendering',
#             'objects': http.request.env['odex_online_tendering.odex_online_tendering'].search([]),
#         })

#     @http.route('/odex_online_tendering/odex_online_tendering/objects/<model("odex_online_tendering.odex_online_tendering"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odex_online_tendering.object', {
#             'object': obj
#         })