import logging
from odoo import _, http
"""
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
import json

_logger = logging.getLogger(__name__)


class WebsiteForm(WebsiteForm):
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True,
                csrf=False)
    def website_form(self, model_name, **kwargs):
        attachment = kwargs.get('attachments[0][0]').filename.split('.')[-1]
        get_param = request.env['ir.config_parameter'].sudo().get_param
        max_upload_size = get_param('odex25_helpdesk.max_upload_size')
        extensions = get_param('odex25_helpdesk.allowed_extensions')
        extensions = [extension.strip() for extension in extensions.split(",")]
        blob = kwargs.get('attachments[0][0]').read()
        size = len(blob) / 1048576
        if extensions:
            if attachment not in extensions:
                return json.dumps({
                    'error': _("Sorry, allowed file extensions are") + ' {}.'.format(extensions)
                })
        if max_upload_size:
            if size > int(max_upload_size):
                return json.dumps({
                    'error': (_("The maximum upload size is %s MB.") % max_upload_size)
                })
        return super(WebsiteForm, self).website_form(model_name, **kwargs)
"""