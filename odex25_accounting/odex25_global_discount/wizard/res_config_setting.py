# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
                                           string='Discount Applies On', default='untax',
                                           config_parameter='odex25_global_discount.tax_discount_policy',
                                           default_model='sale.order')
    sale_account_id = fields.Many2one('account.account', 'Sale Discount Account',
                                      domain=[('user_type_id.name', '=', 'Expenses'), ('discount_account', '=', True)],
                                      config_parameter='odex25_global_discount.sale_account_id')
    purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',
                                          domain=[('user_type_id.name', '=', 'Income'),
                                                  ('discount_account', '=', True)],
                                          config_parameter='odex25_global_discount.purchase_account_id')


ResConfigSettings()
