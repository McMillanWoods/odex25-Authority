#-*- coding: utf-8 -*-
from odoo import models, fields


class SubjectType(models.Model):
    _inherit = 'cm.subject.type'

    default_value_email = fields.Boolean(string='Default value in email', help='Check if you will used in email.', default=False)


class ImportantDegree(models.Model):
    _inherit = 'cm.transaction.important'

    default_value_email = fields.Boolean(string='Default value in email', help='Check if you will used in email.', default=False)
