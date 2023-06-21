# -*- coding: utf-8 -*-
from odoo import http

# class StandardCustomTheme(http.Controller):
#     @http.route('/standard_custom_theme/standard_custom_theme/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/standard_custom_theme/standard_custom_theme/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('standard_custom_theme.listing', {
#             'root': '/standard_custom_theme/standard_custom_theme',
#             'objects': http.request.env['standard_custom_theme.standard_custom_theme'].search([]),
#         })

#     @http.route('/standard_custom_theme/standard_custom_theme/objects/<model("standard_custom_theme.standard_custom_theme"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('standard_custom_theme.object', {
#             'object': obj
#         })