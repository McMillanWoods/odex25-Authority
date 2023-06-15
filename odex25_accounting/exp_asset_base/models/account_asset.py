# -*- coding: utf-8 -*-
# © Copyright (C) 2021 Expert Co. Ltd(<http:/www.exp-sa.com>)

from odoo import models, fields, api, _
from datetime import datetime
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountAssetManufacturer(models.Model):
    _name = 'account.asset.manufacturer'
    _description = 'Asset Manufacturer'

    name = fields.Char(required=True)


class AccountAssetLocation(models.Model):
    _name = 'account.asset.location'
    _description = 'Asset Location'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(required=True)
    complete_name = fields.Char(
        'Asset Location', compute='_compute_complete_name',
        store=True)
    code = fields.Char(required=True)
    type = fields.Selection(
        selection=[('ordinary', 'Ordinary'), ('view', 'View')],
        default='ordinary', required=True
    )
    parent_id = fields.Many2one(
        comodel_name='account.asset.location',
        domain=[('type', '=', 'view')]
    )
    account_analytic_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account",
                                          required=False, )
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('account.asset.location', 'parent_id', 'Child Locations')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = '%s / %s' % (location.parent_id.complete_name, location.name)
            else:
                location.complete_name = location.name


class AccountAssetAsset(models.Model):
    _name = 'account.asset'
    _inherit = 'account.asset'

    asset_picture = fields.Binary(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    serial_no = fields.Char(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    model = fields.Char(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    manufacturer_id = fields.Many2one(
        comodel_name='account.asset.manufacturer',
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    barcode = fields.Char(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True, index=True, copy=False,
    )
    note = fields.Text(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    receive_date = fields.Date(
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    service_provider_id = fields.Many2one(
        comodel_name='res.partner',
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    next_maintenance_date = fields.Date(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    warranty_period = fields.Integer(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True, string="Warranty Period(Months)"
    )
    warranty_end_date = fields.Date(
        compute='_compute_warranty_end_date',
        readonly=True, store=True,
    )
    warranty_contract = fields.Binary(
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    value_residual = fields.Monetary(
        string='Depreciable Value',
        compute='_compute_value_residual',
        store=True
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        domain=[('property_account_expense_id.can_create_asset', '=', True),
                ('property_account_expense_id.user_type_id.internal_group', '=', 'asset')],
        states={'draft': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    responsible_dept_id = fields.Many2one(
        comodel_name='hr.department',
        string='Responsible Department',
        states={'draft': [('readonly', False)], 'model': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    responsible_user_id = fields.Many2one(
        comodel_name='res.users',
        states={'draft': [('readonly', False)], 'model': [('readonly', False)], 'unlock': [('readonly', False)]},
        readonly=True,
    )
    asset_adjustment_count = fields.Integer(
        compute='_asset_adjustment_count',
        string='# of Adjustments',
        help="Number of adjustments"
    )

    status = fields.Selection(
        selection=[('new', 'New'), ('available', 'Available')],
        default='new'
    )
    location_id = fields.Many2one(
        comodel_name='account.asset.location',
        string='Current Location'
    )
    state = fields.Selection(
        selection_add=[('unlock', 'Unlock')]
    )
    limit = fields.Float()

    _sql_constraints = [
        ('asset_barcode_uniq', 'unique (barcode)', 'Asset barcode must be unique.')
    ]

    @api.onchange('location_id')
    def onchange_location_id(self):
        if self.location_id and self.location_id.account_analytic_id:
            self.account_analytic_id = self.location_id.account_analytic_id.id

    # def action_asset_modify(self):
    #     """ Returns an action opening the asset modification wizard.
    #     """
    #     self.ensure_one()
    #     return {
    #         'name': _('Modify Asset'),
    #         'view_mode': 'form',
    #         'res_model': 'account.asset.modify',
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'context': {
    #             'default_asset_id': self.id,
    #         },
    #     }

    def action_asset_pause(self):
        """ Returns an action opening the asset pause wizard."""
        self.ensure_one()
        return {
            'name': _('Pause Asset'),
            'view_mode': 'form',
            'res_model': 'asset.pause',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_asset_id': self.id,
            },
        }

    def action_set_to_close(self):
        """ Returns an action opening the asset pause wizard."""
        self.ensure_one()

        return {
            'name': _('Sell Asset'),
            'view_mode': 'form',
            'res_model': 'asset.sell',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_asset_id': self.id,
            },
        }

    def act_unlock(self):
        self.state = 'unlock'

    def act_lock(self):
        self.state = 'open'

    def _asset_adjustment_count(self):
        for asset in self:
            asset.asset_adjustment_count = len(
                self.env['account.asset.adjustment.line'].search([('asset_id', '=', asset.id)]))

    def open_asset_adjustment(self):
        return {
            'name': _('Asset Adjustment'),
            'view_mode': 'tree',
            'res_model': 'account.asset.adjustment.line',
            'type': 'ir.actions.act_window',
            'domain': [('asset_id', '=', self.id)],
            'flags': {'search_view': True, 'action_buttons': False},
        }

    @api.depends('receive_date', 'warranty_period')
    def _compute_warranty_end_date(self):
        for asset in self:
            if asset.receive_date:
                asset.warranty_end_date = asset.receive_date + relativedelta(months=asset.warranty_period)

    @api.depends('name', 'barcode')
    def name_get(self):
        return [(r.id, r.name + (r.barcode and '-' + r.barcode or '')) for r in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('barcode', operator, name), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        assets = self.search(domain + args, limit=limit)
        return assets.name_get()

    @api.model
    def create(self, values):
        if values.get('state', False) != 'model':
            values['serial_no'] = self.env['ir.sequence'].with_context(
                ir_sequence_date=values.get('acquisition_date', fields.Date.today())).next_by_code('asset.seq')
        return super(AccountAssetAsset, self).create(values)

    def action_save_model(self):
        action = super(AccountAssetAsset, self).action_save_model()
        action['context']['default_asset_type'] = self.asset_type
        return action

    @api.model
    def _asset_cron(self):
        today = fields.Date.today()
        for asset in self.search([('next_maintenance_date', '=', today)]):
            self.env['mail.activity'].sudo().create({
                'res_model_id': self.env.ref('odex25_account_asset.model_account_asset_asset').id,
                'res_id': asset.id,
                'user_id': asset.responsible_user_id.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _('The %s with barcode %s has schedule maintenance today ,please follow.') % (
                    asset.name, asset.barcode),
                'date_deadline': asset.next_maintenance_date,
            })
        for asset in self.search([('warranty_end_date', '=', today)]):
            self.env['mail.activity'].sudo().create({
                'res_model_id': self.env.ref('odex25_account_asset.model_account_asset_asset').id,
                'res_id': asset.id,
                'user_id': asset.responsible_user_id.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _('The warrant period of %s with barcode %s has end!') % (asset.name, asset.barcode),
                'date_deadline': asset.warranty_end_date,
            })

    @api.onchange('model_id', 'original_value')
    def _onchange_model_id(self):
        super(AccountAssetAsset, self)._onchange_model_id()
        if self.model_id and self.original_value <= self.model_id.limit:
            self.method_number = 0
