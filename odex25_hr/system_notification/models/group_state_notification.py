# -*- coding: utf-8 -*-
from odoo import models, fields


class BaseGroupAutomation(models.Model):
    _name = 'automation.group'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', string="Model", ondelete='cascade', required=True)
    atuomation_ids = fields.Many2many(comodel_name='base.automation', relation='automation_state_groups_rel',
                                      string='Group States ')

    def unlink(self):
        """
            Delete all record(s) from recordset
            return True on success, False otherwise

            @return: True on success, False otherwise

            #TODO: process before delete resource
        """
        for recored in self.atuomation_ids:
            recored.unlink()
        result = super(BaseGroupAutomation, self).unlink()
        return result
