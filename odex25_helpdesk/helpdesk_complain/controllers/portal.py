# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from datetime import date, timedelta
import datetime
from odoo import  _
from werkzeug.exceptions import NotFound
from odoo.addons.rating.controllers.main import Rating

from odoo import http
from odoo.http import request, Response


class ComplainSubmit(http.Controller):

    @http.route('/rating/complain', type='http', auth="public")
    def open_rating(self, **kwargs):
        if request:
            ticket = request.env['odex25_helpdesk.ticket'].search([('id','=',request.params.get('ticket_id'))])
            complain = request.env['helpdesk.complain'].create({
                'name':request.params.get('complain'),
                'date':datetime.datetime.now(),
                'helpdesk_id':request.params.get('ticket_id'),
                'is_submitted':True,
                'customer_id':ticket.partner_id.id,
            })
            ticket = request.env['odex25_helpdesk.ticket'].search([('id','=',request.params.get('ticket_id'))])
            template = request.env.ref('helpdesk_complain.ticket_complain_email_template')
            template.with_context({'recipient_ids':False}).send_mail(ticket.id, force_send=True, raise_exception=False)
            ticket.message_post(body=_("There is a new Complain for this Ticket"))
            redirect = '/helpdesk/ticket/' + str(request.params.get('ticket_id'))
            return http.redirect_with_hash(redirect)