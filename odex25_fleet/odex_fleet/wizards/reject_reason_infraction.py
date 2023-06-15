# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class RejectReasonInfraction(models.TransientModel):
    _name = 'reject.reason.infraction.wiz'

    reason = fields.Text()
    infraction_id = fields.Many2one('vehicle.infraction')

    def action_reject(self):
        if self.infraction_id:
            self.infraction_id.sudo().write({
                'state': 'refused',
                'reason': self.reason
            })