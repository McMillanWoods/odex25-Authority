# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.addons.http_routing.models.ir_http import url_for


class Website(models.Model):
    _inherit = "website"

    def get_suggested_controllers(self):
        suggested_controllers = super(Website, self).get_suggested_controllers()
        suggested_controllers.append((_('Appointment'), url_for('/calendar'), 'odex25_website_calendar'))
        return suggested_controllers
