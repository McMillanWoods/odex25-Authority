from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.mail.controllers.main import MailController
from odoo.osv.expression import OR
from odoo.tools import consteq, pycompat

class MailController(MailController):

    @http.route('/mail/view', type='http', auth='none')
    def mail_action_view(self, model=None, res_id=None, message_id=None, access_token=None, **kwargs):
        user = request.session.uid
        if message_id:
            try:
                message = request.env['mail.message'].sudo().browse(int(message_id)).exists()
            except:
                message = request.env['mail.message']
            if message:
                model, res_id = message.model, message.res_id
            else:
                # either a wrong message_id, either someone trying ids -> just go to messaging
                return self._redirect_to_messaging()
        elif res_id and isinstance(res_id, str):
            res_id = int(res_id)

        if request.session.uid:
            user = request.env['res.users'].search([('id','=',request.session.uid)])
            if not user.has_group('odex25_helpdesk_security.group_helpdesk_normal_manager') and not user.has_group('odex25_helpdesk_security.group_helpdesk_normal_user'):
                return False
            else:
                return self._redirect_to_record(model, res_id, access_token)
        return self._redirect_to_record(model, res_id, access_token)
        