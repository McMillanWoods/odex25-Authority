# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import operator
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.modules import get_module_resource


class KSIrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def ksMenu(self, ks_xml_id):

        print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        return self.env['ir.ui.menu'].search([('id','=',72)]).child_id[12].action.id

