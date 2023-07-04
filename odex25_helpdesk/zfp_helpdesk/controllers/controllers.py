# -*- coding: utf-8 -*-
# from odoo import http


# class ZfpHelpdesk(http.Controller):
#     @http.route('/zfp_helpdesk/zfp_helpdesk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zfp_helpdesk/zfp_helpdesk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zfp_helpdesk.listing', {
#             'root': '/zfp_helpdesk/zfp_helpdesk',
#             'objects': http.request.env['zfp_helpdesk.zfp_helpdesk'].search([]),
#         })

#     @http.route('/zfp_helpdesk/zfp_helpdesk/objects/<model("zfp_helpdesk.zfp_helpdesk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zfp_helpdesk.object', {
#             'object': obj
#         })
