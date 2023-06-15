# -*- coding: utf-8 -*-
from odoo import models, fields


class RejectWizard(models.TransientModel):
    _name = 'reject.wizard'
    _description = 'Reject Wizard'

    reason = fields.Text(string='Reason/Justification')

    def button_confirm(self):
        context = dict(self._context)
        active_model = context.get('active_model')
        active_id = context.get('active_id')
        if 'record_reject_name' in context:
            rec_id = self.env[active_model].browse(active_id)
            rec_id.write({
                'reason': self.reason
            })
            reject_func = getattr(rec_id.with_context({'merge_reason': True}), context.get('record_reject_name'))
            reject_func()
        return True
