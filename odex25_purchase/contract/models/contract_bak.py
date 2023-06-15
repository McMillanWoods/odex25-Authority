# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

from hijri_converter import convert

from odoo import api, fields, models, exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class ContractContract(models.Model):
    _name = 'contract.contract'
    _description = "Contract"
    _order = 'id desc'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'contract.abstract.contract',
    ]

    active = fields.Boolean(default=True)
    code = fields.Char(string="Reference")
    group_id = fields.Many2one(
        string="Group",
        comodel_name='account.analytic.account',
        ondelete='restrict',
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
    )
    contract_template_id = fields.Many2one(
        string='Contract Template',
        comodel_name='contract.template'
    )
    contract_line_ids = fields.One2many(
        string='Contract lines',
        comodel_name='contract.line',
        inverse_name='contract_id',
        copy=True,
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )
    create_invoice_visibility = fields.Boolean(compute='_compute_create_invoice_visibility')
    recurring_next_date = fields.Date(
        compute='_compute_recurring_next_date',
        string='Date of Next Invoice',
        store=True,
    )
    date_end = fields.Date(
        compute='_compute_date_end',
        string='Date End',
        store=True,
        readonly=False
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Payment Terms',
        index=True
    )
    invoice_count = fields.Integer(compute="_compute_invoice_count")
    payment_count = fields.Integer(compute="_compute_payment_count")
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal Position',
        ondelete='restrict',
    )
    invoice_partner_id = fields.Many2one(
        string="Invoicing contact",
        comodel_name='res.partner',
        ondelete='restrict',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        inverse='_inverse_partner_id',
        required=True
    )
    commercial_partner_id = fields.Many2one(
        'res.partner',
        related='partner_id.commercial_partner_id',
        store=True,
        string='Commercial Entity',
        index=True
    )
    type_of_contraction = fields.Selection(
        selection=[('subs', 'Subscription'),
                   ('contract', 'Legal Contract')],
        string='Contraction Type',
        default='contract'
    )
    installment_count = fields.Integer(compute="compute_installment_count")
    type = fields.Selection(
        related='contract_template_id.journal_id.type',
        string='Type',
        readonly=True
    )
    state = fields.Selection(
        selection=[('new', _('New')),
                    ('to_confirm' ,_('To Confirm')),
                   ('confirmed', _('Confirmed')),
                   ('in_progress', _('In progress')),
                   ('suspended', _('Suspended')),
                   ('closed', _('Closed')),
                   ('cancel', _('Cancel'))],
        default="new", tracking=True,
    )
    total_amount = fields.Integer(
        compute='_compute_total_amount',
        string='Total Amount',
        store=True,
        readonly=True,
    )
    date_start = fields.Date(string='Date Start')
    note = fields.Html(string='Note')
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Taxes')
    tax_amount = fields.Float(
        compute='_compute_amount_tax',
        string='Tax Amount',
        readonly=True,
        store=True
    )
    with_tax_amount = fields.Float(
        compute='_compute_with_tax_amount',
        store=True, string='Amount With Tax',
        readonly=True
    )
    # ADD by fatima 25/3/2020
    contract_report_template = fields.Many2one('contract.report.template', string='Contract Report Template')
    # ADD by fatima 15/3/2020
    contract_template = fields.Html(string='Template', related='contract_report_template.contract_template')
    # ADD by fatima 16/3/2020
    first_party = fields.Many2one('res.partner', string="First party")
    # ADD by fatima 17/3/2020
    sale_order = fields.Many2one('sale.order', string="Sale Order")
    project_period = fields.Float(string="Project Duration")
    date = fields.Date(string='Date')
    
    penalty = fields.Float(
        string='Penalty Amount',
    )
    
    penalty_type = fields.Selection(
        string='Penalty type',
        selection=[('fix', 'Fixed'), ('percent', 'Percent')],
        default='fix'
    )

    
    percent_amount = fields.Float(
        string='percent',
    )

    
    is_penalty = fields.Boolean(
        string='Penalty',
    )
    
    name_seq = fields.Char(string='Sequence', default='/',
    readonly=True,
    copy=False
    )
    
    
    remaining_amount = fields.Float(
        string='Remaining',
        compute='_compute_installments',
        )
    
    @api.onchange('date_start', 'date_end')
    def _compute_project_period(self):
        if self.date_start and self.date_end:
            date_start = fields.Date.from_string(self.date_start)
            date_end = fields.Date.from_string(self.date_end)
            if date_end <= date_start:
                self.date_end = None
                raise ValidationError(_("End date should be greater than start date"))

            self.project_period = float(abs((date_end - date_start).days))
        else:
            self.project_period = 0.0

    def _compute_installments(self):
        for record in self:
            installments = sum(self.env['line.contract.installment'].search([('contract_id', '=', record.id)]).mapped('total_amount'))
            record.remaining_amount = record.with_tax_amount - installments
    
    @api.onchange('percent_amount')
    def onchange_percent_amount(self):
        if self.percent_amount:
            self.penalty = self.total_amount * self.percent_amount / 100
    
    def action_resume(self):
        self.write({'state': 'in_progress'})
        try:
            # Send Notifications
            subject = _('Contract Resumed')
            message = _('Contract has been resumed') + ' - {}'.format(self.name)
            author_id = self.env.user.partner_id.id or None
            self.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id)
        except Exception as e:
            pass
        # self.message_post(_('Contract has been resumed...'))
       
    

    
    def compute_hijri_date(self, date):
        if date:
            date = date.split('-')
            year = int(date[0])
            day = int(date[1])
            month = int(date[2])
            hijri_date = convert.Gregorian(year, month, day).to_hijri()
            return hijri_date

    def installment_table(self):
        installment = self.get_related_instalment()
        instellment_table = ''
        total_letter = self.num_to_letter(self.total_amount)
        for rec in installment:
            instellment_table += "<tr style='border: 1px solid gray'><td style='width:5%;border: 1px solid gray;background-color:#002d4d;color:white;'>" + rec.name + "</td>"
            instellment_table += "<td style='width:10%;border: 1px solid gray'>" + str(rec.percent) + "</td>"
            instellment_table += "<td style='width:10%;border: 1px solid gray'>" + str(rec.amount) + "</td>"
            if rec.description:
                instellment_table += "<td style='width:40%;;border: 1px solid gray;word-break:break-all'>" + rec.description + "</td></tr>"
            else:
                instellment_table += "<td style='width:40%;;border: 1px solid gray;word-break:break-all'>" "</td></tr>"
        body = """<table dir="rtl" style="width:90%;font-color:black;border: 1px solid black">
                                             <tbody>
                                         <tr style="color:white;border: 1px solid black">
                                             <td style="background-color:#002d4d;width:10%;border: 1px solid gray;text-align:right">الدفعة</td>
                                             <td style="background-color:#002d4d;width:10%;border: 1px solid gray;text-align:right">نسبة</td>
                                             <td style="background-color:#002d4d;width:10%;border: 1px solid gray;text-align:right;">المبلغ</td>
                                            <td style="background-color:#002d4d;width:40%;border: 1px solid gray;text-align:right;" align="center;word-break:break-all">الوصف</td>
                                         </tr>
                                     """"" + instellment_table + """""
                                     </tbody>
                                     <tr style="color:black;border: 1px solid black">
                                     <td style="border: 1px solid gray;text-align:right;background-color:#002d4d;color:white" align="center">الإجمالي</td>
                                     <td style="border: 1px solid gray;text-align:right" align="center"></td>
                                     <td style="border: 1px solid gray;text-align:right" align="center">%s</td>
                                     <td style="border: 1px solid gray;text-align:right" align="center">%s(شامل قيمة الضريبة المضافة)</td>
                                     </tr>
                                 </table>
                                     """ % (self.total_amount, total_letter)
        body = body.replace('""', '')
        return body

    def num_to_letter(self, number):
        num_to_word = self.env['odex.num']
        numb_arbic = num_to_word.convertNumber(number)
        last_arbic_number = numb_arbic.replace('فاصل', 'و')
        return last_arbic_number

    def get_contract_content(self, content):
        installment = self.installment_table()
        total_letter = self.num_to_letter(self.total_amount)
        project_period_letter = self.num_to_letter(self.project_period)
        project_period_letter = project_period_letter.replace('ريال', '')
        hdate = self.compute_hijri_date(self.date)
        body = content.replace('second party name', self.partner_id.name).replace('installment', installment). \
            replace('hdate', str(hdate)).replace('date', self.date if self.date else ''). \
            replace('first party name', self.first_party.name if self.first_party.name else ''). \
            replace('commercial', self.first_party.commercial_register if self.first_party.commercial_register else ''). \
            replace('address', self.first_party.street if self.first_party.street else ''). \
            replace('fCEO', self.first_party.executive_manager if self.first_party.executive_manager else ''). \
            replace('saddress', self.partner_id.street if self.partner_id.street else ''). \
            replace('scommercial', self.partner_id.commercial_register if self.partner_id.commercial_register else '') \
            .replace('sCEO', self.partner_id.executive_manager if self.partner_id.executive_manager else ''). \
            replace('specialist', self.partner_id.specialist if self.partner_id.specialist else '').replace('SOname',
                                                                                                            self.sale_order.name if self.sale_order else ''). \
            replace('SOD', self.sale_order.date_order if self.sale_order.date_order else ''). \
            replace('POname', self.sale_order.ref_order if self.sale_order.ref_order else ''). \
            replace('POD', self.sale_order.ref_date if self.sale_order.ref_date else ''). \
            replace('total', str(self.total_amount)).replace('letter', total_letter).replace('project period',
                                                                                             str(self.project_period)). \
            replace('Pperiod', project_period_letter).replace('Fresponsible', '').replace('Femail', ''). \
            replace('Sresponsible', self.partner_id.appointed if self.partner_id.appointed else ''). \
            replace('Semail', self.partner_id.app_email if self.partner_id.app_email else '')
        return body

    
    def set_to_draft(self):
        self.write({'state': 'new'})

    
    def confirmed_state(self):
        if not self.date_start:
            raise ValidationError(_('Please Enter Contract Start Date!!'))
        if self.type_of_contraction == 'contract' and self.installment_count == 0:
            raise ValidationError(_("Please enter the installments!"))
        self.write({'state': 'confirmed'})

    
    def in_progress_state(self):
        self.write({'state': 'in_progress'})

    
    def suspended_state(self):
        self.write({'state': 'suspended'})
        # self.message_post(_('Contract has been suspended...'))
        try:
            # Send Notifications
            subject = _('Contract Suspended')
            message = _('Contract has been suspended') + ' - {}'.format(self.name)
            author_id = self.env.user.partner_id.id or None
            self.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id)
        except Exception as e:
            pass
        
    
    def closed_state(self):
        self.write({'state': 'closed'})

    
    def cancel_state(self):
        self.write({'state': 'cancel'})

    
    def get_related_instalment(self):
        self.ensure_one()
        installments = (self.env['line.contract.installment'].search([('contract_id', '=', self.id)]))
        return installments

    
    def compute_installment_count(self):
        for item in self:
            item.installment_count = len(item.get_related_instalment())

    
    def _inverse_partner_id(self):
        for rec in self:
            if not rec.invoice_partner_id:
                rec.invoice_partner_id = rec.partner_id.address_get(['invoice'])['invoice']

    
    def _get_related_invoices(self):
        self.ensure_one()
        # invoices = (
        #     self.env['account.move.line'].search([('contract_line_id', 'in', self.contract_line_ids.ids)]).mapped(
        #         'invoice_id'))
        invoices = self.env['account.move'].search([('contract_id', '=', self.id)])
        return invoices

    
    def _get_related_payment(self):
        self.ensure_one()
        # contract_payment = self.env['account.payment'].search([('contract_id', '=', self.id)])
        # invoices = self.env['account.move'].search([('contract_id', '=', self.id)]).ids
        # inv_payment = self.env['account.payment'].search(['|',('reconciled_invoice_ids', 'in', invoices),('reconciled_bill_ids', 'in', invoices)])
        # count = len(contract_payment) + len(inv_payment)
        # return count

        invoices = self.env['account.move'].search([('contract_id', '=', self.id), ('state', '=','posted'), ('payment_state', '=','paid')])
        inv_payment = self.env['account.payment'].search(['|', ('reconciled_invoice_ids', 'in', invoices.ids if invoices else []),('reconciled_bill_ids', 'in', invoices.ids if invoices else [])])
        count = len(inv_payment)
        return count

        # contract_payment = self.env['account.payment'].search([('contract_id', '=', self.id)])
        # return len(contract_payment)

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec._get_related_invoices())

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = rec._get_related_payment()

    def unlink(self):
        for i in self:
            if i.state != 'new':
                raise exceptions.Warning(_('You cannot delete record in state not new'))
        return super(ContractContract, self).unlink()

    
    def action_show_invoices(self):
        self.ensure_one()
        tree_view_ref = (
            'account.move_supplier_tree'
            if self.contract_type == 'purchase'
            else 'account.move_tree_with_onboarding'
        )
        form_view_ref = (
            'account.move_supplier_form'
            if self.contract_type == 'purchase'
            else 'account.move_form'
        )
        tree_view = self.env.ref(tree_view_ref, raise_if_not_found=False)
        form_view = self.env.ref(form_view_ref, raise_if_not_found=False)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id,'create' : False}
        }
        if tree_view and form_view:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        return action

    
    def action_show_payment(self):
        self.ensure_one()
        # invoices = self.env['account.move'].search([('contract_id', '=', self.id)]).ids
        # inv_payment = self.env['account.payment'].search(['|',('reconciled_invoice_ids', 'in', invoices),('reconciled_bill_ids', 'in', invoices)]).ids
        
        invoices = self.env['account.move'].search([('contract_id', '=', self.id), ('state', '=','posted'), ('payment_state', '=','paid')])
        payments = self.env['account.payment'].search(['|', ('reconciled_invoice_ids', 'in', invoices.ids if invoices else []),('reconciled_bill_ids', 'in', invoices.ids if invoices else [])])

        # tree_view_ref = (
        #     'account.view_account_supplier_payment_tree'
        #     if self.contract_type == 'purchase'
        #     else 'account.view_account_payment_tree'
        # )
        # form_view_ref = (
        #     'account.view_account_payment_form'
        #     if self.contract_type == 'purchase'
        #     else 'account.view_account_payment_form'
        # )
        # tree_view = self.env.ref(tree_view_ref, raise_if_not_found=False)
        # form_view = self.env.ref(form_view_ref, raise_if_not_found=False)

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            # 'domain': [('contract_id', '=', self.id)],
            'domain': [('id', 'in', payments.ids if payments else [])],
            'context': {'default_contract_id': self.id,'create' : False}
        }
        # action = {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Payments',
        #     'res_model': 'account.payment',
        #     'context':{'default_contract_id':self.id,'create' : False},
        #     'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
        #     'domain': ['|', ('contract_id', '=', self.id), ('id', 'in', inv_payment)],
        # }


        # if tree_view and form_view:
        #     action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        return action

    @api.depends('contract_line_ids.date_end')
    def _compute_date_end(self):
        for contract in self:
            contract.date_end = False
            date_end = contract.contract_line_ids.mapped('date_end')
            if date_end and all(date_end):
                contract.date_end = max(date_end)

    @api.depends(
        'contract_line_ids.recurring_next_date',
        'contract_line_ids.is_canceled',
    )
    def _compute_recurring_next_date(self):
        for contract in self:
            recurring_next_date = contract.contract_line_ids.filtered(
                lambda l: l.recurring_next_date and not l.is_canceled
            ).mapped('recurring_next_date')
            if recurring_next_date:
                contract.recurring_next_date = min(recurring_next_date)

    @api.depends('contract_line_ids.create_invoice_visibility')
    def _compute_create_invoice_visibility(self):
        for contract in self:
            contract.create_invoice_visibility = any(
                contract.contract_line_ids.mapped(
                    'create_invoice_visibility'
                )
            )

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        """Update the contract fields with that of the template.

        Take special consideration with the `contract_line_ids`,
        which must be created using the data from the contract lines. Cascade
        deletion ensures that any errant lines that are created are also
        deleted.
        """
        contract_template_id = self.contract_template_id
        if not contract_template_id:
            return
        for field_name, field in contract_template_id._fields.items():
            if field.name == 'contract_line_ids':
                lines = self._convert_contract_lines(contract_template_id)
                self.contract_line_ids = lines
            elif not any(
                    (field.compute,
                     field.related,
                     field.automatic,
                     field.readonly,
                     field.company_dependent,
                     field.name in self.NO_SYNC)):
                self[field_name] = self.contract_template_id[field_name]

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist.id
        self.fiscal_position_id = self.partner_id.property_account_position_id
        if self.contract_type == 'purchase':
            self.payment_term_id = \
                self.partner_id.property_supplier_payment_term_id
        else:
            self.payment_term_id = \
                self.partner_id.property_payment_term_id
        self.invoice_partner_id = self.partner_id.address_get(['invoice'])[
            'invoice'
        ]
        return {
            'domain': {'invoice_partner_id': ['|', ('id', 'parent_of', self.partner_id.id),
                                              ('id', 'child_of', self.partner_id.id)]}}
    # function cron of supplier contract 
    def cron_contract_supplier_experation(self):
        date_now = (datetime.now() + timedelta(days=1)).date()
        contracts = self.search([])
        for i in contracts:
            if i.date_end:
                exp_date = fields.Date.from_string(i.date_end) - timedelta(days=30)
                if date_now >= exp_date:
                    mail_content = "Hello, Mr. " + i.user_id.name + ". Notice about the end date of the contract: " + "name of contract " + i.name + " for customer " + i.partner_id.name
                    main_content = {
                        'subject': _('Contract-%s Expired On %s') % (i.name, i.date_end),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.user_id.login,
                        'email_cc': self.env.user.company_id.email,
                    }
                    self.env['mail.mail'].create(main_content).send()
    
    def _convert_contract_lines(self, contract):
        self.ensure_one()
        new_lines = self.env['contract.line']
        contract_line_model = self.env['contract.line']
        for contract_line in contract.contract_line_ids:
            vals = contract_line._convert_to_write(contract_line.read()[0])
            # Remove template link field
            vals.pop('contract_template_id', False)
            vals['date_start'] = fields.Date.context_today(contract_line)
            vals['recurring_next_date'] = fields.Date.context_today(
                contract_line
            )
            new_lines += contract_line_model.new(vals)
        new_lines._onchange_date_start()
        new_lines._onchange_is_auto_renew()
        return new_lines

    
    def _prepare_invoice(self, date_invoice, journal=None):
        self.ensure_one()
        if not journal:
            journal = (
                self.journal_id
                if self.journal_id.type == self.contract_type
                else self.env['account.journal'].search([
                    ('type', '=', self.contract_type),
                    ('company_id', '=', self.company_id.id)], limit=1))
        if not journal:
            raise ValidationError(
                _("Please define a %s journal for the company '%s'.")
                % (self.contract_type, self.company_id.name or '')
            )
        currency = (
                self.pricelist_id.currency_id
                or self.partner_id.property_product_pricelist.currency_id
                or self.company_id.currency_id
        )
        invoice_type = 'out_invoice'
        if self.contract_type == 'purchase':
            invoice_type = 'in_invoice'
        return {
            'name': self.code,
            'type': invoice_type,
            'partner_id': self.invoice_partner_id.id,
            'currency_id': currency.id,
            'invoice_date': date_invoice,
            'journal_id': journal.id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id,
            'contract_id' : self.id
        }

    
    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref('contract.email_contract_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='contract.contract',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def _finalize_invoice_values(self, invoice_values):
        """
        This method adds the missing values in the invoice lines dictionaries.

        If no account on the product, the invoice lines account is
        taken from the invoice's journal in _onchange_product_id
        This code is not in finalize_creation_from_contract because it's
        not possible to create an invoice line with no account

        :param invoice_values: dictionary (invoice values)
        :return: updated dictionary (invoice values)
        """
        # If no account on the product, the invoice lines account is
        # taken from the invoice's journal in _onchange_product_id
        # This code is not in finalize_creation_from_contract because it's
        # not possible to create an invoice line with no account
        new_invoice = self.env['account.move'].new(invoice_values)
        for invoice_line in new_invoice.invoice_line_ids:
            name = invoice_line.name
            account_analytic_id = invoice_line.account_analytic_id
            price_unit = invoice_line.price_unit
            invoice_line.invoice_id = new_invoice
            invoice_line._onchange_product_id()
            invoice_line.update(
                {
                    'name': name,
                    'account_analytic_id': account_analytic_id,
                    'price_unit': price_unit,
                }
            )
        return new_invoice._convert_to_write(new_invoice._cache)

    @api.model
    def _finalize_invoice_creation(self, invoices):
        for invoice in invoices:
            payment_term = invoice.payment_term_id
            fiscal_position = invoice.fiscal_position_id
            invoice._onchange_partner_id()
            invoice.payment_term_id = payment_term
            invoice.fiscal_position_id = fiscal_position
        invoices.compute_taxes()

    @api.model
    def _finalize_and_create_invoices(self, invoices_values):
        """
        This method:
         - finalizes the invoices values (onchange's...)
         - creates the invoices
         - finalizes the created invoices (onchange's, tax computation...)
        :param invoices_values: list of dictionaries (invoices values)
        :return: created invoices (account.move)
        """
        if isinstance(invoices_values, dict):
            invoices_values = [invoices_values]
        final_invoices_values = []
        for invoice_values in invoices_values:
            final_invoices_values.append(
                self._finalize_invoice_values(invoice_values)
            )
        invoices = self.env['account.move'].create(final_invoices_values[0])
        for invoice in invoices:
            for line in invoice.invoice_line_ids:
                line.tax_ids = line.contract_line_id.tax_id and [(4,line.contract_line_id.tax_id.id)]
        self._finalize_invoice_creation(invoices)
        return invoices

    @api.model
    def _get_contracts_to_invoice_domain(self, date_ref=None):
        """
        This method builds the domain to use to find all
        contracts (contract.contract) to invoice.
        :param date_ref: optional reference date to use instead of today
        :return: list (domain) usable on contract.contract
        """
        domain = []
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain.extend([('recurring_next_date', '<=', date_ref),('type_of_contraction' , '=' , 'subs')])
        return domain

    
    def _get_lines_to_invoice(self, date_ref):
        """
        This method fetches and returns the lines to invoice on the contract
        (self), based on the given date.
        :param date_ref: date used as reference date to find lines to invoice
        :return: contract lines (contract.line recordset)
        """
        self.ensure_one()
        return self.contract_line_ids.filtered(
            lambda l: not l.is_canceled
                      and l.recurring_next_date
                      and l.recurring_next_date <= date_ref
        )

    
    def _prepare_recurring_invoices_values(self, date_ref=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        invoices_values = []
        for contract in self:
            if not date_ref:
                date_ref = contract.recurring_next_date
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            invoice_values = contract._prepare_invoice(date_ref)
            for line in contract_lines:
                invoice_values.setdefault('invoice_line_ids', [])
                invoice_line_values = line._prepare_invoice_line(
                    invoice_id=False
                )
                if invoice_line_values:
                    invoice_values['invoice_line_ids'].append(
                        (0, 0, invoice_line_values)
                    )
            invoices_values.append(invoice_values)
            contract_lines._update_recurring_next_date()
        return invoices_values

    
    def recurring_create_invoice(self):
        """
        This method triggers the creation of the next invoices of the contracts
        even if their next invoicing date is in the future.
        """
        return self._recurring_create_invoice()

    
    def _recurring_create_invoice(self, date_ref=False):
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        return self._finalize_and_create_invoices(invoices_values)

    @api.model
    def cron_recurring_create_invoice(self):
        domain = self._get_contracts_to_invoice_domain()
        contracts_to_invoice = self.search(domain)
        date_ref = fields.Date.context_today(contracts_to_invoice)
        contracts_to_invoice._recurring_create_invoice(date_ref)
    @api.depends('contract_line_ids.price_subtotal','contract_line_ids.price_unit')
    def _compute_total_amount(self):
        sum_amount = 0.0
        for price in self.contract_line_ids:
            sum_amount += price.price_subtotal
        self.total_amount = sum_amount

    
    @api.depends('tax_id', 'total_amount')
    def _compute_amount_tax(self):
        self.tax_amount = 0
        for rec in self:
            if rec.tax_id:
                if rec.tax_id.amount_type == 'percent':
                    rec.tax_amount = rec.total_amount * rec.tax_id.amount / 100
                if rec.tax_id.amount_type == 'fixed':
                    rec.tax_amount = rec.tax_id.amount
            else:
                rec.tax_amount = sum(rec.contract_line_ids.mapped('tax_amount'))

    
    @api.depends('tax_amount', 'total_amount')
    def _compute_with_tax_amount(self):
        for rec in self:
            rec.with_tax_amount = rec.total_amount + rec.tax_amount

    def cron_contract_experation(self):
        date_now = (datetime.now() + timedelta(days=1)).date()
        contracts = self.search([])
        for i in contracts:
            if i.date_end:
                exp_date = fields.Date.from_string(i.date_end) - timedelta(days=30)
                if date_now >= exp_date:
                    mail_content = "Hello, Mr. " + i.user_id.name + ". Notice about the end date of the contract: " + "name of contract " + i.name + " for customer " + i.partner_id.name
                    main_content = {
                        'subject': _('Contract-%s Expired On %s') % (i.name, i.date_end),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.user_id.login,
                        'email_cc': self.env.user.company_id.hr_email,
                    }
                    self.env['mail.mail'].create(main_content).send()

    def cron_invoice_payment(self):
        date_now = datetime.now().date()
        invoices = self.env['account.move'].search([('contract_id', '=', self.id)])
        for i in invoices:
            if i.invoice_date_due:
                exp_date = fields.Date.from_string(i.invoice_date_due)
                payment_exp_date = fields.Date.from_string(i.invoice_date_due) - timedelta(days=30)
                if date_now == exp_date:
                    mail_content = "Hello, Mr. " + i.user_id.name + ". It is time to pay the bill number " + i.sequence_number_next_prefix + i.sequence_number_next + " for the customer " + i.partner_id.name + "on " + i.invoice_date_due
                    main_content = {
                        'subject': _('Contract-%s Expired On %s') % (i.name, i.invoice_date_due),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': self.user_id.login,
                        'email_cc': self.env.user.company_id.hr_email,
                    }
                    self.env['mail.mail'].create(main_content).send()
                if payment_exp_date <= date_now < fields.Date.from_string(i.invoice_date_due):
                    mail_content = "Hello, Mr. " + i.user_id.name + ". Notice that the payment date of the invoice number  " + i.sequence_number_next_prefix + i.sequence_number_next + " for the customer " + i.partner_id.name + " is approaching on " + i.invoice_date_due
                    main_content = {
                        'subject': _('Contract-%s Expired On %s') % (i.name, i.invoice_date_due),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': self.user_id.login,
                        'email_cc': self.env.user.company_id.hr_email,
                    }
                    self.env['mail.mail'].create(main_content).send()


    @api.model
    def create(self, values):
        sequence_code = 'contract.contract.seq'
        values['name_seq'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(ContractContract, self).create(values)
