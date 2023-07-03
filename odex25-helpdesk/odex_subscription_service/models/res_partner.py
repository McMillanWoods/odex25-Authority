# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    po_subscription_count = fields.Integer(string='Purchase Subscriptions', compute='_po_subscription_count')
    so_subscription_count = fields.Integer(string='Sale Subscriptions', compute='_so_subscription_count')

    # New Feature for notifications
    def send_notification_message(self, subject, body, author_id=None, group=None):
        """Send notification"""
        if group:
            partner_ids = self.env.ref(group).users.mapped('partner_id').ids
            # print('group', partner_ids)
            # partner_ids = self.env['res.partner'].search([('id', 'in', users)]).mapped('id')
        else:
            partner_ids = [self.id]

        if partner_ids:
            try:
                self.message_post(type="notification", subject=subject, body=body, author_id=author_id,
                     partner_ids=partner_ids,
                     subtype_xmlid="mail.mt_comment")
            except Exception as e:
                pass
                
    # @api.multi
    def _po_subscription_count(self):
        """ Compute the  number of subscription(s) """
        for partner in self:
            partner.po_subscription_count = self.env['subscription.service'].search_count([('partner_id', "=", partner.id), ('type','=','purchase')])
    # @api.multi
    def _so_subscription_count(self):
        """ Compute the  number of subscription(s) """
        for partner in self:
            partner.so_subscription_count = self.env['subscription.service'].search_count([('partner_id', "=", partner.id), ('type','=','sale')])

    # @api.multi
    def purchase_subscription_action_res_partner(self):
        """ Action on click on the stat button in partner form """
        for partner in self:
            return {
                "type": "ir.actions.act_window",
                "res_model": "subscription.service",
                "views": [[False, "tree"], [False, "form"]],
                "domain": [["partner_id", "=", partner.id],["type","=","purchase"]],
                "context": {"create": False},
                "name": _("Purchase Subscriptions"),
            }

    # @api.multi
    def sale_subscription_action_res_partner(self):
        """ Action on click on the stat button in partner form """
        for partner in self:
            return {
                "type": "ir.actions.act_window",
                "res_model": "subscription.service",
                "views": [[False, "tree"], [False, "form"]],
                "domain": [["partner_id", "=", partner.id],["type","=","sale"]],
                "context": {"create": False},
                "name": _("Sale Subscriptions"),
            }
