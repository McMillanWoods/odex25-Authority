# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrderCustom(models.Model):
    _inherit = 'purchase.order'

    def action_sign(self):
        super_action = super(PurchaseOrderCustom, self).action_sign()
        if self.requisition_id and (
                self.requisition_id.purchase_track == 'from_custody' or not self.company_id.purchase_budget):
            self.requisition_id.state = 'checked'
            # self.state = 'draft'
            return super_action
        else:
            return super_action


class PurchaseRequisitionCustom(models.Model):
    _inherit = 'purchase.requisition'

    committee_type_id = fields.Many2one(comodel_name='purchase.committee.type', string='Committee Type')
    purchase_track = fields.Selection([('from_custody', 'From petty Cash'), ('from_budget', 'From Budget')])

    # def action_approve(self):
    # orders  = self.env['purchase.order'].search([('requisition_id' , '=' , self.id),('state' , 'in' , ['to approve','sign'])])
    # state = 'approve'
    # orders_totoal = 0
    # for order in orders:
    #     orders_totoal += order.amount_total
    # if self.company_id.po_double_validation == 'one_step'\
    #             or (self.company_id.po_double_validation == 'two_step'\
    #                 and orders_totoal < self.env.user.company_id.currency_id.compute(self.company_id.po_double_validation_amount, self.purchase_ids[0].currency_id)):
    #     for order in  orders:
    #         order.write({
    #             'state' : 'draft'
    #         })
    # else:
    #     state = 'second_approve'
    # self.write({
    #             'state' : state
    #         })

    def second_approval(self):
        orders = self.env['purchase.order'].search(
            [('requisition_id', '=', self.id), ('state', 'in', ['to approve', 'sign'])])
        state = 'approve'
        orders_totoal = 0
        for order in orders:
            orders_totoal += order.amount_total
        if self.company_id.po_double_validation == 'one_step' or \
                (self.company_id.po_double_validation == 'two_step'
                 and orders_totoal < self.env.user.company_id.currency_id.compute(self.company_id.second_approve,
                                                                                  self.purchase_ids[0].currency_id)):
            state = 'draft'
        else:
            state = 'third_approve'
            # state = 'legal_counsel'
        self.write({
            'state': state
        })

    """@api.multi
    def legal_counsel_approve(self):
        # if self.company_id.purchase_budget:
        #     self.action_budget()
        # else:
        for order in self.purchase_ids.filtered(lambda x: x.state == 'sign'):
            order.write({
                    'state': 'draft'
            })
        self.write({
                'state': 'third_approve'
        })"""

    def third_approve(self):
        for order in self.purchase_ids.filtered(lambda x: x.state in ('to approve', 'sign')):
            order.write({
                'state': 'draft'
            })
        self.write({
            'state': 'approve'
        })

    # @api.onchange('committee_type_id')
    # def _onchange_committee_type_id(self):
    #     if self.committee_type_id:
    #         self.committee_head = self.committee_type_id.committee_head.id
    #         self.committee_members = [(6, 0, self.committee_type_id.committee_members.ids)]
    #     else:
    #         self.committee_members = False
    #         self.committee_head = False

# Commented because the same class is already created on purchase_requisition_custom module
# class CommitteeTypes(models.Model):
#     _name = 'purchase.committee.type'
#
#     name = fields.Char('Name')
#     committe_members = fields.Many2many('res.users', string='Committee Members')
#     committe_head = fields.Many2one('res.users', string='Committee Head')
#
#     @api.constrains('committe_head','committe_members')
#     def committe_head_in_committe_constrains(self):
#         for rec in self :
#             if rec.committe_head in rec.committe_members:
#                 raise ValidationError(_("You can't add Chairman of the Committee as committe member"))


