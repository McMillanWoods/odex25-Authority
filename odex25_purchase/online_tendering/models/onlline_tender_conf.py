from odoo import api, fields, models

class ActivityTypes(models.Model):
    _name = 'activity.type'

    name = fields.Char('Name')

