from odoo import models, fields, api, _
from odoo.exceptions import ValidationError , AccessError
from odoo.tools.safe_eval import safe_eval
import ast
from datetime import datetime, date
from dateutil.relativedelta import relativedelta, SA, SU, MO
import calendar
import pytz



class SystemDashboard(models.Model):
    _name = 'system_dashboard.dashboard'
    _description = 'System Dashboard'