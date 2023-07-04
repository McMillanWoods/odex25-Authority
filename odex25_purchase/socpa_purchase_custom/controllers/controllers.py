# -*- coding: utf-8 -*-
from odoo import http

# class SocpaPurchaseCustom(http.Controller):
#     @http.route('/socpa_purchase_custom/socpa_purchase_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/socpa_purchase_custom/socpa_purchase_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('socpa_purchase_custom.listing', {
#             'root': '/socpa_purchase_custom/socpa_purchase_custom',
#             'objects': http.request.env['socpa_purchase_custom.socpa_purchase_custom'].search([]),
#         })

#     @http.route('/socpa_purchase_custom/socpa_purchase_custom/objects/<model("socpa_purchase_custom.socpa_purchase_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('socpa_purchase_custom.object', {
#             'object': obj
#         })