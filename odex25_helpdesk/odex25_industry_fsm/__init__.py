# -*- coding: utf-8 -*-

from . import models
from . import report
from odoo import api, SUPERUSER_ID, _


def create_field_service_project(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fsm_project = env.ref('odex25_industry_fsm.fsm_project', raise_if_not_found=False)
    project_vals = (env['res.company'].search([]) - fsm_project.company_id)._get_field_service_project_values()
    env['project.project'].create(project_vals)
