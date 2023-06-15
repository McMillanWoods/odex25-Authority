# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime



class TenderApplicationUctom(models.Model):
    _inherit = 'tender.application'
    
    def action_tender(self):
        for rec in self:
            po = super(TenderApplicationUctom, rec).action_tender()
            if po:
                po.write({
                    'state' : 'unsign' ,
                    'department_id' : rec.tender_id.department_id.id,
                    'purpose' : rec.tender_id.purpose,
                    'category_id' : rec.tender_id.category_id.id
                })
        return po