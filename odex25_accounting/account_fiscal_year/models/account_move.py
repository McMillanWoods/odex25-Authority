# -*- coding: utf-8 -*-
##############################################################################
#
#    Expert Co. Ltd.
#    Copyright (C) 2018 (<http://www.exp-sa.com/>).
#
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError
import datetime


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    period_id = fields.Many2one('fiscalyears.periods',
                                string='Period', required=True, readonly=True,
                                states={'draft': [('readonly', False)]},
                                help='''The fiscalyear period
                                used for this receipt.''')

    @api.onchange('date')
    def _onchange_date_period(self):
        for rec in self:
            if rec.date:
                periods = self.env['fiscalyears.periods'].search(
                    [('state', '=', 'open'),
                     ('date_from', '<=', rec.date),
                     ('date_to', '>=', rec.date)])
                if periods:
                    rec.period_id = periods[0].id
                else:
                    raise ValidationError(
                        _('There is no openning fiscal year periods in this date.'))

    @api.constrains('date', 'period_id')
    def _check_date_period(self):
        """
        Check date and period_id are in the same date range
        """
        for rec in self:
            if rec.date and rec.period_id:
                date = fields.Date.from_string(rec.date)
                period_start_date = fields.Date.from_string(
                    rec.period_id.date_from)
                period_end_date = fields.Date.from_string(
                    rec.period_id.date_to)
                if not (date >= period_start_date and
                        date <= period_end_date):
                    raise ValidationError(
                        _('''Date and period must be in the same date range'''))
            else:
                raise ValidationError(
                    _('''You must enter date and period for this record'''))

    @api.model
    def create(self, vals):
        date = vals.get('date', False)
        if not date:
            date = datetime.date.today()
        period_id = vals.get('period_id', False)
        if date and not period_id:
            periods = self.env['fiscalyears.periods'].search( [('state', '=', 'open'),
                                                               ('date_from', '<=', date),
                                                               ('date_to', '>=', date)])
            if periods:
                vals.update({'period_id': periods[0].id})
            else:
                raise Warning(_('Their is no open periods for date %s') % (date))
        return super(AccountMove, self).create(vals)


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"
    
    period_id = fields.Many2one('fiscalyears.periods',
                                related='move_id.period_id', store=True,
                                string='Period', related_sudo=False,
                                help='''The fiscalyear period
                                used for this move line.''')
