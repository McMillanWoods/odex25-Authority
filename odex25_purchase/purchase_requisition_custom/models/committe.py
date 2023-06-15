from odoo import fields, models

class CommitteOfPurchase(models.Model):
    _name = 'purchase.committee'

    head_of_committe = fields.Many2one('res.users', 'Committe Head')
    minimum_approve = fields.Integer('Number of Selections')
    minimum_vote = fields.Integer('Number of Vots')