from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class CustomResPartner(models.Model):
    _inherit = 'res.partner'

    final_evaluation = fields.Float(string='Final Evaluation',compute="_value_compute")
    evaluation_ids = fields.One2many(comodel_name='cumulative.vendor.evaluation', inverse_name='vendor_id', string='')


    @api.depends('evaluation_ids.cumulative_eval')
    def _value_compute(self):
        sum = 0
        for rec in self:
            for line in rec.evaluation_ids:
                sum += line.cumulative_eval
            if len(rec.evaluation_ids) > 0:
                rec.final_evaluation = sum /len(rec.evaluation_ids)
            else:
                rec.final_evaluation = 0
            sum = 0


    


