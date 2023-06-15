# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, models
from odoo.tools import float_round
from odoo.tools import float_is_zero, OrderedSet



class StockMove(models.Model):
    _inherit = 'stock.move'

    # @override
   
    def _action_done(self,cancel_backorder=False):
        # Init a dict that will group the moves by valuation type, according to `move._is_valued_type`.
        valued_moves = {valued_type: self.env['stock.move'] for valued_type in self._get_valued_types()}
        for move in self:
            if float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding):
                continue
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move

        # AVCO application
        valued_moves['in'].product_price_update_before_done()

        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

        # '_action_done' might have created an extra move to be valued
        for move in res - self:
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move

        stock_valuation_layers = self.env['stock.valuation.layer'].sudo()
        # Create the valuation layers in batch by calling `moves._create_valued_type_svl`.
        for valued_type in self._get_valued_types():
            todo_valued_moves = valued_moves[valued_type]
            if todo_valued_moves:
                todo_valued_moves._sanity_check_for_valuation()
                stock_valuation_layers |= getattr(todo_valued_moves, '_create_%s_svl' % valued_type)()

        for svl in stock_valuation_layers:
            if not svl.product_id.valuation == 'real_time':
                continue
            if svl.currency_id.is_zero(svl.value):
                continue
            svl.stock_move_id._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)

        stock_valuation_layers._check_company()

        # For every in move, run the vacuum for the linked product.
        products_to_vacuum = valued_moves['in'].mapped('product_id')
        company = valued_moves['in'].mapped('company_id') and valued_moves['in'].mapped('company_id')[0] or self.env.company
        for product_to_vacuum in products_to_vacuum:
            product_to_vacuum._run_fifo_vacuum(company)

        return res
   
    def _account_entry_move(self, qty, description, svl_id, cost):
        self.ensure_one()
        res = super()._account_entry_move(qty, description, svl_id, cost)
        if res is not None and not res:
            return res

        self = self.with_context(forced_quantity=-self.product_qty)

        location_from = self.location_id
        location_to = self.location_dest_id

        # get valuation accounts for product
        if self._is_internal():
            product_valuation_accounts \
                = self.product_id.product_tmpl_id.get_product_accounts()
            stock_valuation = product_valuation_accounts.get('stock_valuation')
            stock_journal = product_valuation_accounts.get('stock_journal')

            if location_from.force_accounting_entries \
                    and location_to.force_accounting_entries:
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id)
            elif location_from.force_accounting_entries:
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    stock_valuation.id,
                    stock_journal.id)
            elif location_to.force_accounting_entries:
                self._create_account_move_line(
                    stock_valuation.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id)

        return res

   
    def _is_internal(self):
        self.ensure_one()
        return self.location_id.usage == 'internal' \
            and self.location_dest_id.usage == 'internal'


    @api.model
    def _get_valued_types(self):
        res = super()._get_valued_types() 
        res.append('internal')
        return res

   
    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        journal_id, acc_src, acc_dest, acc_valuation \
            = super()._get_accounting_data_for_valuation()
        # intercept account valuation, use account specified on internal
        # location as a local valuation
        if self._is_in() and self.location_dest_id.force_accounting_entries:
            # (acc_src if not dest.usage == 'customer') => acc_valuation
            acc_valuation \
                = self.location_dest_id.valuation_in_account_id.id
        if self._is_out() and self.location_id.force_accounting_entries:
            # acc_valuation => (acc_dest if not dest.usage == 'supplier')
            acc_valuation \
                = self.location_id.valuation_out_account_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
