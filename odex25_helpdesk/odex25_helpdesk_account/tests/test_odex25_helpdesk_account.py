# -*- coding: utf-8 -*-

from odoo.addons.odex25_helpdesk.tests import common
from odoo.tests.common import Form


class Testodex25_helpdeskAccount(common.odex25_helpdeskCommon):
    """ Test used to check that the functionalities of After sale in helpdesk (credit note).
    """

    def test_odex25_helpdesk_account_1(self):
        # give the test team ability to create credit note
        self.test_team.use_credit_notes = True
        # create a sale order and invoice
        partner = self.env['res.partner'].create({
            'name': 'Customer Credee'
        })
        product = self.env['product.product'].create({
            'name': 'product 1',
            'type': 'consu',
            'invoice_policy': 'order',
        })
        so = self.env['sale.order'].create({
            'partner_id': partner.id,
        })
        self.env['sale.order.line'].create({
            'product_id': product.id,
            'price_unit': 10,
            'product_uom_qty': 1,
            'order_id': so.id,
        })
        so.action_confirm()
        so._create_invoices()
        invoice = so.invoice_ids
        invoice.action_post()
        # odex25_helpdesk.ticket access rights
        ticket = self.env['odex25_helpdesk.ticket'].create({
            'name': 'test',
            'partner_id': partner.id,
            'team_id': self.test_team.id,
            'sale_order_id': so.id,
        })

        credit_note_form = Form(self.env['account.move.reversal'].with_context({
            'default_odex25_helpdesk_ticket_id': ticket.id,
        }), view=self.env.ref('odex25_helpdesk_account.view_account_move_reversal_inherit_odex25_helpdesk_account'))
        for inv in so.invoice_ids:
            credit_note_form.move_ids.add(inv)
        credit_note_form.reason = 'test'
        credit_note = credit_note_form.save()
        res = credit_note.reverse_moves()
        refund = self.env['account.move'].browse(res['res_id'])

        self.assertEqual(len(refund), 1, "No refund created")
        self.assertEqual(refund.state, 'draft', "Wrong status of the refund")
        self.assertEqual(refund.ref, 'Reversal of: %s, %s' % (invoice.name, credit_note_form.reason), "The reference is wrong")
        self.assertEqual(len(ticket.invoice_ids), 1,
            "The ticket should be linked to a credit note")
        self.assertEqual(ticket.invoices_count, 1,
            "The ticket should be linked to a credit note")
        self.assertEqual(refund[0].id, ticket.invoice_ids[0].id,
            "The correct credit note should be referenced in the ticket")
