from datetime import datetime
import time

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.model
    def get_departments(self):
        departments = self.env["hr.department"].search([("analytic_account_id", "!=", False)])
        department_list = []
        for department in departments:
            department_list.append({"id": department.id, "name": department.name})
        return department_list

    @api.model
    def get_vendors(self):
        vendors = self.env["res.partner"].search([])
        vendor_list = []
        for vendor in vendors:
            vendor_list.append({"id": vendor.id, "name": vendor.name})
        return vendor_list

    @api.model
    def get_cost_centers(self):
        cost_centers = self.env["account.analytic.account"].search([])
        cost_center_list = []
        for cost_center in cost_centers:
            cost_center_list.append({"id": cost_center.id, "name": cost_center.name})
        return cost_center_list

    @api.model
    def get_years(self):
        cr = self.env.cr
        sql = """
        SELECT date_trunc('year', date) AS year 
        FROM contract_contract
        WHERE date IS NOT NULL
        """
        cr.execute(sql, )
        years = cr.dictfetchall()
        years_list = []
        for year in years:
            years_list.append(year['year'].year)
        years_list = list(set(years_list))
        return years_list

    @api.model
    def get_annual_contract_data(self, year, contract_type, state, depts, vendors):

        domain = [
            ('date', '>=', str(year) + '-' + '01' + '-' + '01'),
            ('date', '<=', str(year) + '-' + '12' + '-' + '31'),
            ('contract_type', '=', contract_type)
        ]
        analytic_account_ids = False
        if depts is not None and len(depts) > 0:
            analytic_account_ids = self.env["account.analytic.account"].search([('id', 'in', depts)]).ids

        if state != 'all':
            domain.append(('state', '=', state))

        if vendors is not None and len(vendors) > 0:
            partner_ids = self.env["res.partner"].search([('id', 'in', vendors)]).ids
            domain.append(('partner_id', 'in', partner_ids))

        contracts = self.env['contract.contract'].search(domain)
        contract_lines = contracts.mapped("contract_line_ids")

        q1 = 0.0
        q2 = 0.0
        q3 = 0.0
        q4 = 0.0

        if analytic_account_ids is not False:
            filtered_lines = contracts.mapped('contract_line_ids').filtered(lambda col: col.analytic_account_id.id in
                                                                                        analytic_account_ids)
            contracts = filtered_lines.mapped('contract_id')
            contract_lines = filtered_lines

        for c_line in contracts.mapped('contract_line_ids'):
            c_line_order_date = datetime.strptime(str(c_line.contract_id.date), DF)
            int_year = int(year)
            if datetime(int_year, 1, 1) <= c_line_order_date <= datetime(int_year, 3, 31):
                q1 += c_line.price_subtotal + c_line.tax_amount
            if datetime(int_year, 4, 1) <= c_line_order_date <= datetime(int_year, 6, 30):
                q2 += c_line.price_subtotal + c_line.tax_amount
            if datetime(int_year, 7, 1) <= c_line_order_date <= datetime(int_year, 9, 30):
                q3 += c_line.price_subtotal + c_line.tax_amount
            if datetime(int_year, 10, 1) <= c_line_order_date <= datetime(int_year, 12, 31):
                q4 += c_line.price_subtotal + c_line.tax_amount

        q1 = round(q1, 2)
        q2 = round(q2, 2)
        q3 = round(q3, 2)
        q4 = round(q4, 2)

        year_contract_total = sum([q1, q2, q3, q4])

        partners = contracts.mapped('partner_id')

        contract_lines_by_partner = []

        for partner in partners:
            partner_contract_ids = contracts.filtered(lambda c: c.partner_id.id == partner.id)
            partner_total_contracts = sum([col.price_subtotal + col.tax_amount
                                           for col in partner_contract_ids.mapped('contract_line_ids')])
            contract_lines_by_partner.append({"name": partner.name, "y": partner_total_contracts})

        contract_lines_by_department = []

        analytic_accounts = contract_lines.mapped('analytic_account_id')

        for analytic_account in analytic_accounts:
            analytic_account_line_ids = contract_lines.filtered(
                lambda col: col.analytic_account_id.id == analytic_account.id)

            analytic_account_total_contracts = sum([col.price_subtotal + col.tax_amount
                                                    for col in analytic_account_line_ids])
            contract_lines_by_department.append({"name": analytic_account.name, "y": analytic_account_total_contracts})

        contract_count = len(contracts)

        contract_quarters_list = [{"name": "Q1", "y": q1},
                                  {"name": "Q2", "y": q2},
                                  {"name": "Q3", "y": q3},
                                  {"name": "Q4", "y": q4}]

        contract_bar_name_list = contracts.mapped('name')
        contract_bar_amount_list = contracts.mapped('with_tax_amount')
        contract_bar_remaining_list = contracts.mapped('remaining_amount')
        contract_bar_paid_list = []
        for contract in contracts:
            installments = sum(
                self.env['line.contract.installment'].search(
                    [('contract_id', '=', contract.id)]).mapped('total_amount'))
            contract_bar_paid_list.append(installments)

        result = {
            "contract_by_department": contract_lines_by_department,
            "contract_by_quarter": contract_quarters_list,
            "contract_total_year": year_contract_total,
            "contract_by_partner": contract_lines_by_partner,
            "contract_count": contract_count,
            "contract_bar_data": {
                "contract_bar_name_list": contract_bar_name_list,
                "contract_bar_amount_list": contract_bar_amount_list,
                "contract_bar_remaining_list": contract_bar_remaining_list,
                "contract_bar_paid_list": contract_bar_paid_list
            }
        }
        return result

    @api.model
    def get_period_contract_data(self, from_date, to_date, contract_type, state, depts, vendors):

        domain = [
            ('date', '>=', from_date),
            ('date', '<=', to_date),
            ('contract_type', '=', contract_type)
        ]

        analytic_account_ids = False
        if depts is not None and len(depts) > 0:
            analytic_account_ids = self.env["account.analytic.account"].search([('id', 'in', depts)]).ids

        if state != 'all':
            domain.append(('state', '=', state))

        if vendors is not None and len(vendors) > 0:
            partner_ids = self.env["res.partner"].search([('id', 'in', vendors)]).ids
            domain.append(('partner_id', 'in', partner_ids))

        contracts = self.env['contract.contract'].search(domain)
        contract_lines = contracts.mapped("contract_line_ids")

        if analytic_account_ids is not False:
            filtered_lines = contracts.mapped('contract_line_ids').filtered(lambda col: col.analytic_account_id.id in
                                                                                        analytic_account_ids)
            contracts = filtered_lines.mapped('contract_id')
            contract_lines = filtered_lines

        year_contract_total = sum([c_line.price_subtotal + c_line.tax_amount for c_line in contract_lines])

        partners = contracts.mapped('partner_id')

        contract_lines_by_partner = []

        for partner in partners:
            partner_contract_ids = contracts.filtered(lambda c: c.partner_id.id == partner.id)
            partner_total_contracts = sum([col.price_subtotal + col.tax_amount
                                           for col in partner_contract_ids.mapped('contract_line_ids')])
            contract_lines_by_partner.append({"name": partner.name, "y": partner_total_contracts})

        contract_lines_by_department = []

        analytic_accounts = contract_lines.mapped('analytic_account_id')

        for analytic_account in analytic_accounts:
            analytic_account_line_ids = contract_lines.filtered(
                lambda col: col.analytic_account_id.id == analytic_account.id)

            analytic_account_total_contracts = sum([col.price_subtotal + col.tax_amount
                                                    for col in analytic_account_line_ids])
            contract_lines_by_department.append({"name": analytic_account.name, "y": analytic_account_total_contracts})

        contract_count = len(contracts)

        contract_bar_name_list = contracts.mapped('name')
        contract_bar_amount_list = contracts.mapped('with_tax_amount')
        contract_bar_remaining_list = contracts.mapped('remaining_amount')
        contract_bar_paid_list = []
        for contract in contracts:
            installments = sum(
                self.env['line.contract.installment'].search(
                    [('contract_id', '=', contract.id)]).mapped('total_amount'))
            contract_bar_paid_list.append(installments)

        result = {
            "contract_by_department": contract_lines_by_department,
            "contract_period_total": year_contract_total,
            "contract_by_partner": contract_lines_by_partner,
            "contract_count": contract_count,
            "contract_bar_data": {
                "contract_bar_name_list": contract_bar_name_list,
                "contract_bar_amount_list": contract_bar_amount_list,
                "contract_bar_remaining_list": contract_bar_remaining_list,
                "contract_bar_paid_list": contract_bar_paid_list
            }
        }
        return result
