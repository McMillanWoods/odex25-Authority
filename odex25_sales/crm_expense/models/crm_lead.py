# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'


    expense_count = fields.Float('Expenses', compute="_compute_expense_count")
    expense_ids = fields.One2many('hr.expense', 'crm_lead_id', 'Expenses')

    def _compute_expense_count(self):

        self.expense_count = sum(self.expense_ids.mapped('total_amount'))


    def action_view_expense(self):
        action = self.env["ir.actions.actions"]._for_xml_id("hr_expense.hr_expense_actions_my_unsubmitted")
        action['context'] = {
            'default_crm_lead_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
        action['domain'] = [('crm_lead_id', '=', self.id)]
        return action