# -*- coding: utf-8 -*-
from lxml.builder import E

from odoo import _, api, models
from odoo.exceptions import UserError


class Base(models.AbstractModel):
    _inherit = 'base'

    _start_name = 'date_start'
    _stop_name = 'date_stop'

    @api.model
    def _get_default_map_view(self):
        view = E.map()

        if 'partner_id' in self._fields:
            view.set('res_partner', 'partner_id')
        else:
            raise UserError(_("You need to set a Contact field on this model to use the Map View"))

        return view

    @api.model
    def _get_default_gantt_view(self):
        view = E.gantt(string=self._description)

        gantt_field_names = {
            '_start_name': ['date_start', 'start_date', 'x_date_start', 'x_start_date'],
            '_stop_name': ['date_stop', 'stop_date', 'date_end', 'end_date', 'x_date_stop', 'x_stop_date', 'x_date_end',
                           'x_end_date'],
        }
        for name in gantt_field_names.keys():
            if getattr(self, name) not in self._fields:
                for dt in gantt_field_names[name]:
                    if dt in self._fields:
                        setattr(self, name, dt)
                        break
                else:
                    raise UserError(_("Insufficient fields for Gantt View!"))
        view.set('date_start', self._start_name)
        view.set('date_stop', self._stop_name)

        return view

    @api.model
    def gantt_unavailability(self, start_date, end_date, scale, group_bys=None, rows=None):
        return rows
