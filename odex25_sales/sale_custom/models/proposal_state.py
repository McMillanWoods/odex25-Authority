# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProposalState(models.Model):
    _name = 'proposal.state'
    _description = 'Proposal State'

    name = fields.Char('Description', required=True, translate=True)
    upload_contract = fields.Boolean('Upload Contract')