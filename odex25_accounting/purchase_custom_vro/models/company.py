# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    
   
    general_supervisor_id = fields.Many2one(
       string='General Supervisor',
       comodel_name='hr.employee',
   )
   
