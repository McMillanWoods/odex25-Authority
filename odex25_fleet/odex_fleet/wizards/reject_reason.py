# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class RejectReasonFleet(models.TransientModel):
    _name = 'reject.reason.fleet.wiz'
    _description = 'Reject Wiz'

    reason = fields.Text()
    delegation_id = fields.Many2one('vehicle.delegation')
    maintenance_id = fields.Many2one('fleet.maintenance')
    request_id = fields.Many2one('fleet.quotation')

    def action_reject(self):
        if self.delegation_id:
            self.delegation_id.sudo().write({
                'state': 'refused',
                'reason': self.reason
            })
        elif self.request_id:
            self.request_id.sudo().write({
                'approve': False,
                'reason': self.reason
            })
