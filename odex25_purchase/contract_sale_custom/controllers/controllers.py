# -*- coding: utf-8 -*-
# from odoo import http


# class ContractSaleCustom(http.Controller):
#     @http.route('/contract_sale_custom/contract_sale_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_sale_custom/contract_sale_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_sale_custom.listing', {
#             'root': '/contract_sale_custom/contract_sale_custom',
#             'objects': http.request.env['contract_sale_custom.contract_sale_custom'].search([]),
#         })

#     @http.route('/contract_sale_custom/contract_sale_custom/objects/<model("contract_sale_custom.contract_sale_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_sale_custom.object', {
#             'object': obj
#         })
