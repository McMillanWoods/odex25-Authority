# -*- coding: utf-8 -*-

import uuid
import json
import logging
import base64
import requests
import markupsafe
from odoo import models, fields, api
from odoo.tools import float_repr, html2plaintext

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_sa_zatca_document = fields.Binary(string="Document", required=False, )
    l10n_sa_zatca_uuid = fields.Char(string="UUID Document", )

    @api.model
    def create(self, values):
        values['l10n_sa_zatca_uuid'] = str(uuid.uuid4())
        return super(AccountMove, self).create(values)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.company_id.country_id.code == 'SA':
            self.create_zatca_document()
        return res

    def create_zatca_document(self):
        self.ensure_one()
        # Create file content.
        # xml_content = markupsafe.Markup("<?xml version='1.0' encoding='UTF-8'?>")
        # xml_content += self.env.ref('l10_sa_edi_zatca.export_ubl_invoice')._render(self._get_ubl_values())
        content = self.env.ref('l10_sa_edi_zatca.export_ubl_invoice')._render(self._get_ubl_values())
        xml_content = b'<?xml version="1.0" encoding="UTF-8"?>' + content
        xml_name = '%s_ubl_2_1.xml' % (self.name.replace('/', '_'))
        self.env['ir.attachment'].create({
            'name': xml_name,
            'datas': base64.encodebytes(xml_content),
            'res_model': 'account.move',
            'res_id': self.id,
            'mimetype': 'application/xml'
        })
        self.l10n_sa_zatca_document = base64.encodebytes(xml_content)

    def _get_ubl_values(self):
        ''' Get the necessary values to generate the XML. These values will be used in the qweb template when
        rendering. Needed values differ depending on the implementation of the UBL, as (sub)template can be overriden
        or called dynamically.
        :returns:   a dictionary with the value used in the template has key and the value as value.
        '''

        def format_monetary(amount):
            # Format the monetary values to avoid trailing decimals (e.g. 90.85000000000001).
            return float_repr(amount, self.currency_id.decimal_places)

        return {
            **self._prepare_edi_vals_to_export(),
            'tax_details': self._prepare_edi_tax_details(),
            'ubl_version': 2.1,
            'type_code': 388 if self.move_type == 'out_invoice' else 381,
            'type_code_name': '02' if self.move_type == 'out_invoice' else '01',
            'payment_means_code': 42 if self.journal_id.bank_account_id else 10,
            'bank_account': self.partner_bank_id,
            'note': html2plaintext(self.narration) if self.narration else False,
            'format_monetary': format_monetary,
            'customer_vals': {'partner': self.commercial_partner_id},
            'supplier_vals': {'partner': self.company_id.partner_id.commercial_partner_id},
        }

    def _prepare_edi_vals_to_export(self):
        ''' The purpose of this helper is to prepare values in order to export an invoice through the EDI system.
        This includes the computation of the tax details for each invoice line that could be very difficult to
        handle regarding the computation of the base amount.

        :return: A python dict containing default pre-processed values.
        '''
        self.ensure_one()

        res = {
            'record': self,
            'balance_multiplicator': -1 if self.is_inbound() else 1,
            'invoice_line_vals_list': [],
        }

        # Invoice lines details.
        for index, line in enumerate(self.invoice_line_ids.filtered(lambda line: not line.display_type), start=1):
            line_vals = line._prepare_edi_vals_to_export()
            line_vals['index'] = index
            res['invoice_line_vals_list'].append(line_vals)

        # Totals.
        res.update({
            'total_price_subtotal_before_discount': sum(
                x['price_subtotal_before_discount'] for x in res['invoice_line_vals_list']),
            'total_price_discount': sum(x['price_discount'] for x in res['invoice_line_vals_list']),
        })

        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _prepare_edi_vals_to_export(self):
        ''' The purpose of this helper is the same as '_prepare_edi_vals_to_export' but for a single invoice line.
        This includes the computation of the tax details for each invoice line or the management of the discount.
        Indeed, in some EDI, we need to provide extra values depending the discount such as:
        - the discount as an amount instead of a percentage.
        - the price_unit but after subtraction of the discount.

        :return: A python dict containing default pre-processed values.
        '''
        self.ensure_one()

        res = {
            'line': self,
            'price_unit_after_discount': self.price_unit * (1 - (self.discount / 100.0)),
            'price_subtotal_before_discount': self.move_id.currency_id.round(self.price_unit * self.quantity),
            'price_subtotal_unit': self.move_id.currency_id.round(
                self.price_subtotal / self.quantity) if self.quantity else 0.0,
            'price_total_unit': self.move_id.currency_id.round(
                self.price_total / self.quantity) if self.quantity else 0.0,
        }

        res['price_discount'] = res['price_subtotal_before_discount'] - self.price_subtotal

        return res
