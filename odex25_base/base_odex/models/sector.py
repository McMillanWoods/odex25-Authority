# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Sector(models.Model):
    _name = 'sector'
    _description = 'Sector'

    name = fields.Char('Name', required=True)
