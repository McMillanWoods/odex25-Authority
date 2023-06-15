# -*- encoding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID


class ReminderPopupAlert(http.Controller):

    @http.route('/reminder/notifications', type='json', auth="user")
    def load_messages_alert(self, **kw):
        cr, uid = request.cr, SUPERUSER_ID
        cr.execute(
            """select mail_message_id from mail_message_res_partner_needaction_rel where res_partner_id = """ + str(
                request.env.user.partner_id.id))
        Messages_ids = []
        for line in cr.fetchall():
            s = request.env['mail.message'].browse(line[0])
            for li in s:
                for x in li.notification_ids:
                    if x.res_partner_id.id == request.env.user.partner_id.id and x.is_read == False:
                        Messages_ids.append(line[0])
        list_item = []
        Messages = http.request.env['mail.message'].search([('id', 'in', Messages_ids)], order='date asc')
        base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for message in Messages:
            action_id = ''
            if message.model:
                reminder_line_ids = http.request.env['late.email.reminder.line'].sudo().search(
                    [('model_id', '=', message.model)])
                # for reminder_line_id in reminder_line_ids:
                #     for group in reminder_line_id.group_ids:
                #         if request.env.user.id in group.users.ids:
                #             # if reminder_line_id.menu_id.action:
                #     action_id = reminder_line_id.menu_id.action.id
            item = {
                'subject': message.body,
                'id': message.id,
                'res_id': message.res_id,
                'res_model': message.model,
                'base_url': base_url,
                # 'action_id' : action_id,
            }
            list_item.append(item)
        return list_item
