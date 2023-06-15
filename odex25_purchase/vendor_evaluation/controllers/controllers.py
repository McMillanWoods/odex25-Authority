# -*- coding: utf-8 -*-
from odoo import http

# class VendorEvaluation(http.Controller):
#     @http.route('/vendor_evaluation/vendor_evaluation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vendor_evaluation/vendor_evaluation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vendor_evaluation.listing', {
#             'root': '/vendor_evaluation/vendor_evaluation',
#             'objects': http.request.env['vendor_evaluation.vendor_evaluation'].search([]),
#         })

#     @http.route('/vendor_evaluation/vendor_evaluation/objects/<model("vendor_evaluation.vendor_evaluation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vendor_evaluation.object', {
#             'object': obj
#         })