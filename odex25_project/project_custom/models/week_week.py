# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models,_

class WeekWeek(models.Model):
    _name = "week.week"

    name = fields.Char("Code")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")

