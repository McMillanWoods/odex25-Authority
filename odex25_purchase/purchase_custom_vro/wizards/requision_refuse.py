# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class PurchaseRefues(models.TransientModel):
    _name = "purchase.requistion.refuse.wizard"
    _description = "purchase refuse Reason wizard"

    reason = fields.Char(string='Reason', required=True)
    requision_id = fields.Many2one('purchase.requisition')

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRefues, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'requision_id': active_ids[0] if active_ids else False,
        })
        return res

    def requistion_refuse_reason(self):

        self.ensure_one()
        self.requision_id.message_post(_("Refuse Reason is : %s") % self.reason)

        if self.requision_id.state == "draft":
            if self.requision_id.request_id:
                self.requision_id.request_id.state = 'draft'
                self.requision_id.request_id.message_post(_("Refuse Reason is : %s") % self.reason)
                self.requision_id.action_refuse()
                self.requision_id.write({'state': 'refuse'})
            else:
                self.requision_id.write({'state': 'draft'})
        if self.requision_id.state == 'in_progress':
            self.requision_id.write({'state': 'draft'})

            # self.requision_id.write({'state':'in_progress'})
        if self.requision_id.state == "purchase_manager":
            self.requision_id.action_refuse()
            self.requision_id.write({'state': 'in_progress'})

        if self.requision_id.state == "quality":
            self.requision_id.write({'state': 'purchase_manager'})
        if self.requision_id.state == "user_approve":
            if not self.requision_id.purchase_commitee:
                self.requision_id.write({'state': 'quality'})
            else:
                self.requision_id.write({'state': 'in_progress'})

        if self.requision_id.state == "second_approve":
            self.requision_id.write({'state': 'user_approve'})
            # con
        if self.requision_id.state == "legal_counsel":
            self.requision_id.write({'state': 'second_approve'})
            # con
        if self.requision_id.state == "third_approve":
            self.requision_id.write({'state': 'legal_counsel'})
        if self.requision_id.state == "finance approve":
            self.requision_id.write({'state': 'user_approve'})
        if self.requision_id.state == "cs approve":
            self.requision_id.write({'state': 'finance approve'})
        if self.requision_id.state == "general supervisor":
            self.requision_id.write({'state': 'cs approve'})

        return {'type': 'ir.actions.act_window_close'}
