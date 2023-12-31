# -*- coding: utf-8 -*-
import requests
import json

from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, date_utils
from datetime import datetime
from dateutil.relativedelta import relativedelta

"""
This module manage an "online account" for a journal. It can't be used in standalone,
other module have to be install (like Plaid or Yodlee). Theses modules must be given
for the online_account reference field. They manage how the bank statement are retrived
from a web service.
"""

class ProviderAccount(models.Model):
    _name = 'account.online.provider'
    _description = 'Provider for online account synchronization'
    _inherit = ['mail.thread']

    name = fields.Char(help='name of the banking institution', string="Institution")
    provider_type = fields.Selection([], readonly=True)
    provider_account_identifier = fields.Char(help='ID used to identify provider account in third party server', readonly=True)
    provider_identifier = fields.Char(readonly=True, help='ID of the banking institution in third party server used for debugging purpose')
    status = fields.Char(string='Synchronization status', readonly=True, help='Update status of provider account')
    status_code = fields.Char(readonly=True, help='Code to identify problem')
    message = fields.Char(readonly=True, help='Techhnical message from third party provider that can help debugging')
    action_required = fields.Boolean(readonly=True, help='True if user needs to take action by updating account', default=False)
    last_refresh = fields.Datetime(readonly=True, default=fields.Datetime.now())
    next_refresh = fields.Datetime("Next synchronization", compute='_compute_next_synchronization')
    account_online_journal_ids = fields.One2many('account.online.journal', 'account_online_provider_id')
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)

    def _compute_next_synchronization(self):
        for rec in self:
            rec.next_refresh = self.env['ir.cron'].sudo().search([('id', '=', self.env.ref('odex25_account_online_sync.online_sync_cron').id)], limit=1).nextcall

    def open_action(self, action_name, number_added):
        action = self.env['ir.actions.act_window']._for_xml_id(action_name)
        self.env[action["res_model"]].check_access_rights('write')
        ctx = self.env.context.copy()
        ctx.update({'default_number_added': number_added})
        action.update({'context': ctx})
        return action

    def log_message(self, message):
        # Usually when we are performing a call to the third party provider to either refresh/fetch transaction/add user, etc,
        # the call can fail and we raise an error. We also want the error message to be logged in the object in the case the call
        # is done by a cron. This is why we are using a separate cursor to write the information on the chatter. Otherwise due to
        # the raise(), the transaction would rollback and nothing would be posted on the chatter.
        # There is a particuler use case with this, is when we are trying to unlink an account.online.provider,
        # we usually also perform a call to the third party provider to delete it from the third party provider system.
        # This call can also fail and if this is the case we do not want to prevent the user from deleting the object in odoo.
        # Problem is that if we try to log the error message, it will result in an error since a transaction will delete the object
        # and another transaction will try to write on the object. Therefore, we need to pass a special key in the context in those
        # cases to prevent writing on the object
        if not self._context.get('no_post_message'):
            subject = _("An error occurred during online synchronization")
            message = _('The following error happened during the synchronization: %s', message)
            with self.pool.cursor() as cr:
                self.with_env(self.env(cr=cr)).message_post(body=message, subject=subject)

    def _get_favorite_institutions(self, country):
        resp_json = {}
        try:
            url = self.sudo().env['ir.config_parameter'].get_param('odoo.online_sync_proxy') or 'https://onlinesync.odoo.com'
            resp = requests.post(url=url + '/onlinesync/search/favorite', data={'country': country, 'provider': json.dumps(self._get_available_providers())}, timeout=60)
            resp_json = resp.json()
        except requests.exceptions.Timeout:
            raise UserError(_('Timeout: the server did not reply within 60s'))
        except (ValueError, requests.exceptions.ConnectionError):
            raise UserError(_('Server not reachable, please try again later'))
        return resp_json

    def get_institutions(self, searchString, country):
        if len(searchString) == 0:
            raise UserError(_('Please enter at least a character for the search'))
        resp_json = {}
        try:
            data = {
                'include_environment': self.env["ir.config_parameter"].sudo().get_param("plaid.include.environment") or False,
                'query': searchString,
                'country': country,
                'provider': json.dumps(self._get_available_providers())
            }
            url = self.sudo().env['ir.config_parameter'].get_param('odoo.online_sync_proxy') or 'https://onlinesync.odoo.com'
            resp = requests.post(url=url + '/onlinesync/search/', data=data, timeout=60)
            resp_json = resp.json()
        except requests.exceptions.Timeout:
            raise UserError(_('Timeout: the server did not reply within 60s'))
        except (ValueError, requests.exceptions.ConnectionError):
            raise UserError(_('Server not reachable, please try again later'))
        return json.dumps(resp_json)

    def show_result(self, values):
        """ This method is used to launch the end process of adding/refreshing/editing an online account provider
            It will create a wizard where user will be notified of the result of the call and if new accounts have
            been fetched, he will be able to link them to different journals
        """
        number_added = len(values.get('added', []))
        status = 'success'
        if values.get('status') == 'FAILED' or values.get('status') == '3':
            status = 'failed'
        if values.get('status') == 'ACTION_ABANDONED' or values.get('status') == '1':
            status = 'cancelled'
        if values.get('transactions'):
            transactions = "<br/><br/><p>%s</p>" % (_('The following transactions have been loaded in the system.'),)
            for tr in values.get('transactions'):
                transactions += '<br/><p>%s: <strong>%s</strong> - %s %s</p>' % (_('Journal'), tr.get('journal'), tr.get('count'), _('transactions loaded'))
        else:
            transactions = '<br/><br/><p>%s</p>' % (_('No new transactions have been loaded in the system.'),)
        hide_table = False
        if number_added == 0:
            hide_table = True
        transient = self.env['account.online.wizard'].create({
            'number_added': number_added,
            'status': status,
            'method': values.get('method'),
            'message': values.get('message', _('Unknown reason')),
            'transactions': transactions,
            'hide_table': hide_table,
        })
        for account in values.get('added', []):
            vals = {'online_account_id': account.id, 'account_online_wizard_id': transient.id}
            # If we are adding an account for the first time and only have one, link it to journal
            if (number_added == 1 and values.get('method') == 'add'):
                vals['journal_id'] = values.get('journal_id')
            self.env['account.online.link.wizard'].create(vals)

        action = self.env["ir.actions.actions"]._for_xml_id("odex25_account_online_sync.action_account_online_wizard_form")
        action['res_id'] = transient.id
        return action

    """ Methods that need to be override by sub-module"""

    def _get_available_providers(self):
        return []

    def get_login_form(self, site_id, provider, beta=False):
        """ This method is used to fetch and display the login form of the institution choosen in
            get_institutions method. Usually this method should return a client action that will
            render the login form
        """
        return []

    def manual_sync(self):
        """ This method is used to ask the third party provider to refresh the account and
            fetch the latest transactions.
        """
        return False

    @api.model
    def cron_fetch_online_transactions(self):
        return False

    @api.model
    def get_manual_configuration_form(self):
        view_id = self.env.ref('account.setup_bank_account_wizard').id
        ctx = self.env.context.copy()
        # if this was called from kanban box, active_model is in context
        if self.env.context.get('active_model') == 'account.journal':
            ctx.update({
                'default_linked_journal_id': ctx.get('journal_id', False)
            })
        return {'type': 'ir.actions.act_window',
                'name': _('Create a Bank Account'),
                'res_model': 'account.setup.bank.manual.config',
                'target': 'new',
                'view_mode': 'form',
                'context': ctx,
                'views': [[view_id, 'form']],
        }

    def update_credentials(self):
        pass


class OnlineAccount(models.Model):
    """
    This class is used as an interface.
    It is used to save the state of the current online accout.
    """
    _name = 'account.online.journal'
    _description = 'Interface for Online Account Journal'

    name = fields.Char(string="Journal Name", required=True)
    account_online_provider_id = fields.Many2one('account.online.provider', ondelete='cascade', readonly=True)
    journal_ids = fields.One2many('account.journal', 'account_online_journal_id', string='Journal', domain=[('type', '=', 'bank')])
    account_number = fields.Char()
    last_sync = fields.Date("Last synchronization")
    online_identifier = fields.Char(help='id use to identify account in provider system', readonly=True)
    provider_name = fields.Char(related='account_online_provider_id.name', string="Provider", readonly=True)
    balance = fields.Float(readonly=True, help='balance of the account sent by the third party provider')

    @api.depends('name', 'account_online_provider_id.name')
    def name_get(self):
        res = []
        for account_online in self:
            name = "%s: %s" % (account_online.provider_name, account_online.name)
            if account_online.account_number:
                name += " (%s)" % (account_online.account_number)
            res += [(account_online.id, name)]
        return res

    def retrieve_transactions(self):
        # This method must be implemented by plaid and yodlee services
        raise UserError(_("Unimplemented"))

    @api.model
    def _find_partner_from_location(self, location):
        """
        Return a recordset of partner if the address of the transaction exactly match the address of a partner
        location : a dictionary of type:
                   {'state': x, 'address': y, 'city': z, 'zip': w}
                   state and zip are optional

        """
        partners = self.env['res.partner']
        domain = []
        if 'address' in location and 'city' in location:
            domain.append(('street', '=', location['address']))
            domain.append(('city', '=', location['city']))
            if 'state' in location:
                domain.append(('state_id.name', '=', location['state']))
            if 'zip' in location:
                domain.append(('zip', '=', location['zip']))
            return self._find_partner(domain)
        return False

    @api.model
    def _find_partner(self, domain):
        """
        Return a recordset of partner iff we have only one partner associated to the value passed as parameter
        value : a String send by Yodlee to identify the account or merchant from which the transaction was made
        field: name of the field where to search for the information
        """
        partners = self.env['res.partner'].search(domain)
        if len(partners) == 1:
            return partners.id
        else:
            # It is possible that all partners share the same commercial partner, in that case, use the commercial partner
            commercial_partner = list(set([p.commercial_partner_id for p in partners]))
            if len(commercial_partner) == 1:
                return commercial_partner[0].id
        return False

class OnlineAccountLinkWizard(models.TransientModel):
    _name = 'account.online.link.wizard'
    _description = 'Link synchronized account to a journal'

    journal_id = fields.Many2one('account.journal', domain="[('type', '=', 'bank'), ('account_online_journal_id', '=', False)]")
    online_account_id = fields.Many2one('account.online.journal')
    action = fields.Selection([('create', 'Create new journal'), ('link', 'Link to existing journal'), ('drop', 'Do not link')], default='link')
    name = fields.Char(related='online_account_id.name', readonly=True, string="Account name")
    balance = fields.Float(related='online_account_id.balance', readonly=True)
    account_online_wizard_id = fields.Many2one('account.online.wizard')
    account_number = fields.Char(related='online_account_id.account_number', readonly=True)
    journal_statements_creation = fields.Selection(selection=lambda x: x.env['account.journal'].get_statement_creation_possible_values(), default='none', string="Synchronization frequency")

    @api.onchange('journal_id')
    def _onchange_account_ids(self):
        if self.journal_id:
            self.journal_statements_creation = self.journal_id.bank_statement_creation

        if self.action == 'drop':
            self.journal_id = None
            self.journal_statements_creation = None


class OnlineAccountWizard(models.TransientModel):
    _name = 'account.online.wizard'
    _description = 'Wizard to link synchronized accounts to journal'

    number_added = fields.Integer(readonly=True)
    transactions = fields.Html(readonly=True)
    status = fields.Selection([('success', 'Success'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], readonly=True)
    method = fields.Selection([('add', 'add'), ('edit', 'edit'), ('refresh', 'refresh')], readonly=True)
    message = fields.Char(readonly=True)
    sync_date = fields.Date('Fetch transactions from', default=lambda a: fields.Date.context_today(a) - relativedelta(days=15))
    account_ids = fields.One2many('account.online.link.wizard', 'account_online_wizard_id', 'Synchronized accounts')
    hide_table = fields.Boolean(help='Technical field to hide table in view')

    def _get_journal_values(self, account, create=False):
        vals = {
            'account_online_journal_id': account.online_account_id.id,
            'bank_statements_source': 'online_sync',
            'bank_statement_creation': account.journal_statements_creation,
        }
        if create:
            vals['name'] = account.name
            vals['type'] = 'bank'
        return vals

    def sync_now(self):
        # Link account to journal
        journal_already_linked = []
        for account in self.account_ids:
            account.online_account_id.write({'last_sync': self.sync_date})
            if account.action == 'link':
                if not account.journal_id:
                    raise UserError(_('Please link your accounts to a journal or select "do not link" as action to do'))
                if account.journal_id.id in journal_already_linked:
                    raise UserError(_('You can not link two accounts to the same journal'))
                journal_already_linked.append(account.journal_id.id)
                account.journal_id.write(self._get_journal_values(account))
            elif account.action == 'create':
                vals = self._get_journal_values(account, create=True)
                self.env['account.journal'].create(vals)
        # call to synchronize
        self.env['account.journal'].cron_fetch_online_transactions()
        # Reload dashboard
        return self.env["ir.actions.actions"]._for_xml_id("account.open_account_journal_dashboard_kanban")

    def open_accounting_dashboard(self):
        return self.env["ir.actions.actions"]._for_xml_id("account.open_account_journal_dashboard_kanban")


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _select_action_to_open(self):
        self.ensure_one()
        if not self._context.get('action_name') and self.type == 'bank' and self.bank_statements_source == 'online_sync':
            return 'action_bank_statement_line'
        return super()._select_action_to_open()

    def __get_bank_statements_available_sources(self):
        rslt = super(AccountJournal, self).__get_bank_statements_available_sources()
        rslt.append(("online_sync", _("Automated Bank Synchronization")))
        return rslt

    @api.model
    def get_statement_creation_possible_values(self):
        return [('none', 'Create one statement per synchronization'),
                ('day', 'Create daily statements'),
                ('week', 'Create weekly statements'),
                ('bimonthly', 'Create bi-monthly statements'),
                ('month', 'Create monthly statements')]

    next_synchronization = fields.Datetime("Next synchronization", compute='_compute_next_synchronization')
    account_online_journal_id = fields.Many2one('account.online.journal')
    account_online_provider_id = fields.Many2one('account.online.provider', related='account_online_journal_id.account_online_provider_id', readonly=False)
    synchronization_status = fields.Char(related='account_online_provider_id.status', readonly=False)
    bank_statement_creation = fields.Selection(selection=get_statement_creation_possible_values,
                                               help="""Defines when a new bank statement
                                               will be created when fetching new transactions
                                               from your bank account.""",
                                               default='none',
                                               string='Creation of Bank Statements')

    def _compute_next_synchronization(self):
        next_sync = self.env['ir.cron'].sudo().search([
            ('id', '=', self.env.ref('odex25_account_online_sync.online_sync_cron').id)
        ], limit=1).nextcall

        for rec in self:
            rec.next_synchronization = next_sync

    def action_choose_institution(self):
        sync_error_message = ''
        ctx = self.env.context.copy()
        country = self.company_id.country_id
        ctx.update({'dialog_size': 'medium', 'country': country.code, 'country_name': country.name, 'journal_id': self.id})
        starred_inst = []
        try:
            # Get starred institutions
            starred_inst = self.env['account.online.provider']._get_favorite_institutions(country.code).get('result', [])

        except UserError as err:
            sync_error_message = err.args[0]

        return {
            'type': 'ir.actions.client',
            'tag': 'online_sync_institution_selector',
            'name': _('Add a Bank Account'),
            'params': {
                'starred_inst': starred_inst,
                'sync_error_message': sync_error_message,
            },
            'target': 'new',
            'context': ctx,
        }

    def manual_sync(self):
        if self.account_online_journal_id:
            return self.account_online_journal_id.account_online_provider_id.manual_sync()

    def open_online_sync_form(self):
        return {
                'type': 'ir.actions.act_window',
                'name': _('Online Synchronization'),
                'res_model': 'account.online.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref("view_account_online_wizard_form").id,
                'target': 'new',
               }

    @api.model
    def cron_fetch_online_transactions(self):
        journals = self.search([('account_online_journal_id', '!=', False)])
        if len(journals):
            account_online_providers = journals.mapped('account_online_journal_id').mapped('account_online_provider_id')
            for account_online_provider in account_online_providers:
                try:
                    account_online_provider.cron_fetch_online_transactions()
                except UserError:
                    continue

    def unlink(self):
        acc_online_provider = False
        if self.account_online_journal_id:
            acc_online_provider = self.account_online_journal_id.account_online_provider_id
        super(AccountJournal, self).unlink()
        if acc_online_provider and len(acc_online_provider.account_online_journal_ids.filtered(lambda j: len(j.journal_ids) > 0)) == 0:
            # If we have no more linked journal to the account provider, delete it.
            acc_online_provider.unlink()


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_validate(self):
        res = super().button_validate()
        for statement in self:
            for line in statement.line_ids:
                if line.partner_id and (line.online_partner_vendor_name or line.online_partner_bank_account):
                    # write value for account and merchant on partner only if partner has no value, in case value are different write False
                    value_acc = line.partner_id.online_partner_bank_account or line.online_partner_bank_account
                    value_acc = value_acc if value_acc == line.online_partner_bank_account else False
                    value_merchant = line.partner_id.online_partner_vendor_name or line.online_partner_vendor_name
                    value_merchant = value_merchant if value_merchant == line.online_partner_vendor_name else False
                    line.partner_id.online_partner_vendor_name = value_merchant
                    line.partner_id.online_partner_bank_account = value_acc
        return res

    @api.model
    def online_sync_bank_statement(self, transactions, journal, ending_balance):
        """
         build a bank statement from a list of transaction and post messages is also post in the online_account of the journal.
         :param transactions: A list of transactions that will be created in the new bank statement.
             The format is : [{
                 'id': online id,                  (unique ID for the transaction)
                 'date': transaction date,         (The date of the transaction)
                 'name': transaction description,  (The description)
                 'amount': transaction amount,     (The amount of the transaction. Negative for debit, positive for credit)
                 'partner_id': optional field used to define the partner
                 'online_partner_vendor_name': optional field used to store information on the statement line under the
                    online_partner_vendor_name field (typically information coming from plaid/yodlee). This is use to find partner
                    for next statements
                 'online_partner_bank_account': optional field used to store information on the statement line under the
                    online_partner_bank_account field (typically information coming from plaid/yodlee). This is use to find partner
                    for next statements
             }, ...]
         :param journal: The journal (account.journal) of the new bank statement
         :param ending_balance: ending balance on the account

         Return: The number of imported transaction for the journal
        """
        # Since the synchronization succeeded, set it as the bank_statements_source of the journal
        journal.sudo().write({'bank_statements_source': 'online_sync'})
        if not len(transactions):
            return 0

        transactions_identifiers = [line['online_identifier'] for line in transactions]
        existing_transactions_ids = self.env['account.bank.statement.line'].search([('online_identifier', 'in', transactions_identifiers), ('journal_id', '=', journal.id)])
        existing_transactions = [t.online_identifier for t in existing_transactions_ids]

        sorted_transactions = sorted(transactions, key=lambda l: l['date'])
        min_date = date_utils.start_of(sorted_transactions[0]['date'], 'month')
        if journal.bank_statement_creation == 'week':
            # key is not always the first of month
            weekday = min_date.weekday()
            min_date = date_utils.subtract(min_date, days=weekday)
        max_date = sorted_transactions[-1]['date']
        total = sum([t['amount'] for t in sorted_transactions])

        statements_in_range = self.search([('date', '>=', min_date), ('journal_id', '=', journal.id)])

        # For first synchronization, an opening bank statement is created to fill the missing bank statements
        all_statement = self.search_count([('journal_id', '=', journal.id)])
        digits_rounding_precision = journal.currency_id.rounding if journal.currency_id else journal.company_id.currency_id.rounding
        if all_statement == 0 and not float_is_zero(ending_balance - total, precision_rounding=digits_rounding_precision):
            opening_transaction = [(0, 0, {
                'date': date_utils.subtract(min_date, days=1),
                'payment_ref': _("Opening statement: first synchronization"),
                'amount': ending_balance - total,
            })]
            statement = self.create({
                'name': _('Opening statement'),
                'date': date_utils.subtract(min_date, days=1),
                'line_ids': opening_transaction,
                'journal_id': journal.id,
                'balance_end_real': ending_balance - total,
            })
            statement.button_post()

        transactions_in_statements = []
        statement_to_reset_to_draft = self.env['account.bank.statement']
        transactions_to_create = {}

        number_added = 0
        for transaction in sorted_transactions:
            if transaction['online_identifier'] in existing_transactions:
                continue
            line = transaction.copy()
            number_added += 1
            if journal.bank_statement_creation == 'day':
                # key is full date
                key = transaction['date']
            elif journal.bank_statement_creation == 'week':
                # key is first day of the week
                weekday = transaction['date'].weekday()
                key = date_utils.subtract(transaction['date'], days=weekday)
            elif journal.bank_statement_creation == 'bimonthly':
                if transaction['date'].day >= 15:
                    # key is the 15 of that month
                    key = transaction['date'].replace(day=15)
                else:
                    # key if the first of the month
                    key = date_utils.start_of(transaction['date'], 'month')
                # key is year-month-0 or year-month-1
            elif journal.bank_statement_creation == 'month':
                # key is first of the month
                key = date_utils.start_of(transaction['date'], 'month')
            else:
                # key is last date of transactions fetched
                key = max_date

            # Decide if we have to update an existing statement or create a new one with this line
            stmt = statements_in_range.filtered(lambda x: x.date == key)
            if stmt and stmt[0].id:
                line['statement_id'] = stmt[0].id
                transactions_in_statements.append(line)
                statement_to_reset_to_draft += stmt[0]
            else:
                if not transactions_to_create.get(key):
                    transactions_to_create[key] = []
                transactions_to_create[key].append((0, 0, line))

        # Create the lines that should be inside an existing bank statement and reset those stmt in draft
        if len(transactions_in_statements):
            for st in statement_to_reset_to_draft:
                if st.state == 'confirm':
                    st.message_post(body=_('Statement has been reset to draft because some transactions from online synchronization were added to it.'))
                    st.state = 'posted'

            posted_statements = statement_to_reset_to_draft.filtered(lambda st: st.state == 'posted')
            posted_statements.state = 'open'
            statement_lines = self.env['account.bank.statement.line'].create(transactions_in_statements)
            posted_statements.state = 'posted'

            # Post only the newly created statement lines if the related statement is already posted.
            statement_lines.filtered(lambda line: line.statement_id.state == 'posted')\
                .mapped('move_id')\
                .with_context(skip_account_move_synchronization=True)\
                ._post()

            # Recompute the balance_end_real of the first statement where we added line
            # because adding line don't trigger a recompute and balance_end_real is not updated.
            # We only trigger the recompute on the first element of the list as it is the one
            # the most in the past and this will trigger the recompute of all the statements
            # that are next.
            statement_to_reset_to_draft[0]._compute_ending_balance()

        # Create lines inside new bank statements
        st_vals_list = []
        for date, lines in transactions_to_create.items():
            # balance_start and balance_end_real will be computed automatically
            name = _('Online synchronization of %s') % (date,)
            if journal.bank_statement_creation in ('bimonthly', 'week', 'month'):
                name = _('Online synchronization from %s to %s')
                end_date = date
                if journal.bank_statement_creation == 'month':
                    end_date = date_utils.end_of(date, 'month')
                elif journal.bank_statement_creation == 'week':
                    end_date = date_utils.add(date, days=6)
                elif journal.bank_statement_creation == 'bimonthly':
                    if end_date.day == 1:
                        end_date = date.replace(day=14)
                    else:
                        end_date = date_utils.end_of(date, 'month')
                name = name % (date, end_date)
            st_vals_list.append({
                'name': name,
                'date': date,
                'line_ids': lines,
                'journal_id': journal.id
            })
        statements = self.env['account.bank.statement'].create(st_vals_list)
        statements.button_post()

        # write account balance on the last statement of the journal
        # That way if there are missing transactions, it will show in the last statement
        # and the day missing transactions are fetched or manually written, everything will be corrected
        last_bnk_stmt = self.search([('journal_id', '=', journal.id)], limit=1)
        if last_bnk_stmt:
            last_bnk_stmt.balance_end_real = ending_balance
            if last_bnk_stmt.state == 'posted' and last_bnk_stmt.balance_end != last_bnk_stmt.balance_end_real:
                last_bnk_stmt.button_reopen()
        # Set last sync date as the last transaction date
        journal.account_online_journal_id.sudo().write({'last_sync': max_date})
        return number_added


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    online_identifier = fields.Char("Online Identifier")
    online_partner_vendor_name = fields.Char(readonly=True, help='Technical field used to store information from plaid/yodlee to match partner (used when a purchase is made)')
    online_partner_bank_account = fields.Char(readonly=True, help='Technical field used to store information from plaid/yodlee to match partner')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    online_partner_vendor_name = fields.Char(readonly=True, help='Technical field used to store information from plaid/yodlee to match partner (used when a purchase is made)')
    online_partner_bank_account = fields.Char(readonly=True, help='Technical field used to store information from plaid/yodlee to match partner')
