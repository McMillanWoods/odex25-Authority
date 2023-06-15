# -*- coding: utf-8 -*-
from odoo import http

# class PrivateBudgetStructure(http.Controller):
#     @http.route('/private_budget_structure/private_budget_structure/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/private_budget_structure/private_budget_structure/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('private_budget_structure.listing', {
#             'root': '/private_budget_structure/private_budget_structure',
#             'objects': http.request.env['private_budget_structure.private_budget_structure'].search([]),
#         })

#     @http.route('/private_budget_structure/private_budget_structure/objects/<model("private_budget_structure.private_budget_structure"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('private_budget_structure.object', {
#             'object': obj
#         })