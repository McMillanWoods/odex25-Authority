# -*- encoding: utf-8 -*-
import uuid

from odoo import api, models, fields
from odoo.tools import pycompat


class PublisherWarrantyContract(models.AbstractModel):
    _inherit = "publisher_warranty.contract"
    _description = "Languages"

    def update_notification(self, cron_mode=True):
        set_param = self.env['ir.config_parameter'].sudo().set_param
        remove_ids=self.env['ir.config_parameter'].sudo().search(['|', ('key', '=', 'database.expiration_date'),
                                                       ('key', '=', 'database.expiration_reason')])
        remove_ids.sudo().unlink()
        set_param('database.create_date', str(fields.Datetime.now()))
        set_param('database.secret',str(pycompat.to_text(uuid.uuid4())))
        set_param('database.uuid', str(pycompat.to_text(uuid.uuid1())))

        self.clear_caches()
        return super(PublisherWarrantyContract, self).update_notification(cron_mode=cron_mode)


PublisherWarrantyContract()
