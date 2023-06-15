from odoo import models
from odoo.addons.cmis_field import fields


class InternalTransaction(models.Model):
    _inherit = 'internal.transaction'

    cmis_folder = fields.CmisFolder()
