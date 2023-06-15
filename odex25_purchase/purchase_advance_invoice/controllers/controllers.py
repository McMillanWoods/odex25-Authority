# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseAdvanceInvoice(http.Controller):
#     @http.route('/purchase_advance_invoice/purchase_advance_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_advance_invoice/purchase_advance_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_advance_invoice.listing', {
#             'root': '/purchase_advance_invoice/purchase_advance_invoice',
#             'objects': http.request.env['purchase_advance_invoice.purchase_advance_invoice'].search([]),
#         })

#     @http.route('/purchase_advance_invoice/purchase_advance_invoice/objects/<model("purchase_advance_invoice.purchase_advance_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_advance_invoice.object', {
#             'object': obj
#         })