from datetime import datetime
import time

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def get_departments(self):
        departments = self.env["hr.department"].search([("analytic_account_id", "!=", False)])
        department_list = []
        for department in departments:
            department_list.append({"id": department.id, "name": department.name})
        return department_list

    @api.model
    def get_vendors(self):
        vendors = self.env["res.partner"].search([('supplier_rank', '>', 1)])
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
        SELECT date_trunc('year', date_order) AS year 
        FROM purchase_order
        """
        cr.execute(sql, )
        years = cr.dictfetchall()
        years_list = []
        for year in years:
            years_list.append(datetime.strptime(str(year['year']), DTF).year)
        years_list = list(set(years_list))
        return years_list

    @api.model
    def get_annual_purchase_data(self, year, state, depts, vendors):
        cr = self.env.cr
        domain = []
        if depts is not None and len(depts) > 0:
            domain = [('id', 'in', depts)]

        account_analytic_ids = self.env["account.analytic.account"].search(domain)

        domain = []
        if vendors is not None and len(vendors) > 0:
            domain = [('id', 'in', vendors)]

        vendor_ids = self.env["res.partner"].search(domain)

        select_clause = """SELECT date_trunc('month', po.date_order) AS amount_month,
        ABS(COALESCE(SUM(pol.price_subtotal + COALESCE(pol.price_tax, 0)), 0)) as amount """

        from_clause = """ FROM purchase_order_line pol JOIN purchase_order po ON (pol.order_id = po.id)"""
        where_clause = """ WHERE date_part('year', po.date_order) = %s """
        group_by_clause = """ GROUP BY amount_month"""

        if state != 'all':
            where_clause += " AND po.state = %s"

        if depts is not None and len(depts) > 0:
            where_clause += " AND pol.account_analytic_id = ANY(%s)"

        if vendors is not None and len(vendors) > 0:
            where_clause += " AND po.partner_id = ANY(%s)"

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        args = [year]

        if state != 'all':
            args.append(state)

        if depts is not None and len(depts) > 0:
            args.append(account_analytic_ids.ids)

        if vendors is not None and len(vendors) > 0:
            args.append(vendor_ids.ids)

        cr.execute(sql, args)

        purchase_lines_by_month = cr.dictfetchall()
        q1 = 0.0
        q2 = 0.0
        q3 = 0.0
        q4 = 0.0
        for p_line in purchase_lines_by_month:
            p_line_order_date = datetime.strptime(str(p_line['amount_month']), DTF)
            int_year = int(year)
            if datetime(int_year, 1, 1) <= p_line_order_date <= datetime(int_year, 3, 31):
                q1 += p_line['amount']
            if datetime(int_year, 4, 1) <= p_line_order_date <= datetime(int_year, 6, 30):
                q2 += p_line['amount']
            if datetime(int_year, 7, 1) <= p_line_order_date <= datetime(int_year, 9, 30):
                q3 += p_line['amount']
            if datetime(int_year, 10, 1) <= p_line_order_date <= datetime(int_year, 12, 31):
                q4 += p_line['amount']

        q1 = round(q1, 2)
        q2 = round(q2, 2)
        q3 = round(q3, 2)
        q4 = round(q4, 2)

        year_purchase_total = sum([q1, q2, q3, q4])

        select_clause = """SELECT rp.name AS name,
        ABS(COALESCE(SUM(pol.price_subtotal + pol.price_tax), 0)) as y """

        from_clause = """ FROM purchase_order_line pol JOIN purchase_order po ON (pol.order_id = po.id)
        JOIN res_partner rp ON (po.partner_id = rp.id)"""
        where_clause = """ WHERE date_part('year', po.date_order) = %s 
        AND pol.account_analytic_id = ANY(%s) AND po.partner_id = ANY(%s)"""
        group_by_clause = """ GROUP BY rp.name"""

        if state != 'all':
            where_clause += " AND po.state = %s"

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        if state != 'all':
            cr.execute(sql, (year, account_analytic_ids.ids, vendor_ids.ids, state,))
        else:
            cr.execute(sql, (year, account_analytic_ids.ids, vendor_ids.ids,))

        purchase_lines_by_partner = cr.dictfetchall()

        select_clause = """SELECT aa.name AS name,
        ABS(COALESCE(SUM(pol.price_subtotal + pol.price_tax), 0)) as y """

        from_clause = """ FROM purchase_order_line pol 
        JOIN account_analytic_account aa ON (pol.account_analytic_id = aa.id)
        JOIN purchase_order po ON (pol.order_id = po.id)"""
        where_clause = """ WHERE date_part('year', po.date_order) = %s 
        AND pol.account_analytic_id = ANY(%s) AND po.partner_id = ANY(%s) """
        group_by_clause = """ GROUP BY aa.name"""

        if state != 'all':
            where_clause += " AND po.state = %s"

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        if state != 'all':
            cr.execute(sql, (year, account_analytic_ids.ids, vendor_ids.ids, state,))
        else:
            cr.execute(sql, (year, account_analytic_ids.ids, vendor_ids.ids,))

        purchase_lines_by_department = cr.dictfetchall()

        select_clause = """SELECT count(distinct(po.id)) AS po_count"""
        from_clause = """ FROM purchase_order_line pol JOIN purchase_order po ON (pol.order_id = po.id)"""
        where_clause = """ WHERE date_part('year', po.date_order) = %s """
        group_by_clause = """"""

        if state != 'all':
            where_clause += " AND po.state = %s"

        if depts is not None and len(depts) > 0:
            where_clause += " AND pol.account_analytic_id = ANY(%s)"

        if vendors is not None and len(vendors) > 0:
            where_clause += " AND po.partner_id = ANY(%s)"

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        args = [year]

        if state != 'all':
            args.append(state)

        if depts is not None and len(depts) > 0:
            args.append(account_analytic_ids.ids)

        if vendors is not None and len(vendors) > 0:
            args.append(vendor_ids.ids)

        cr.execute(sql, args)

        purchase_order_count = cr.fetchone()[0] or 0
        purchase_quarters_list = [{"name": "Q1", "y": q1},
                                  {"name": "Q2", "y": q2},
                                  {"name": "Q3", "y": q3},
                                  {"name": "Q4", "y": q4}]
        result = {
            "purchase_by_department": purchase_lines_by_department,
            "purchase_by_quarter": purchase_quarters_list,
            "purchase_total_year": year_purchase_total,
            "purchase_by_partner": purchase_lines_by_partner,
            "purchase_count": purchase_order_count
        }
        return result

    @api.model
    def get_period_purchase_data(self, from_date, to_date, state, depts, vendors):
        cr = self.env.cr
        domain = []
        if depts is not None and len(depts) > 0:
            domain = [('id', 'in', depts)]

        account_analytic_ids = self.env["account.analytic.account"].search(domain)

        domain = []
        if vendors is not None and len(vendors) > 0:
            domain = [('id', 'in', vendors)]

        vendor_ids = self.env["res.partner"].search(domain)

        select_clause = """SELECT rp.name AS name,
                ABS(COALESCE(SUM(pol.price_subtotal + pol.price_tax), 0)) as y """

        from_clause = """ FROM purchase_order_line pol JOIN purchase_order po ON (pol.order_id = po.id)
                JOIN res_partner rp ON (po.partner_id = rp.id)"""
        where_clause = """ WHERE po.date_order BETWEEN to_date(%s, 'mm/dd/yyyy') AND to_date(%s, 'mm/dd/yyyy')"""
        group_by_clause = """ GROUP BY rp.name"""

        if state != 'all':
            where_clause += " AND po.state = %s"

        if depts is not None and len(depts) > 0:
            where_clause += " AND pol.account_analytic_id = ANY(%s)"

        if vendors is not None and len(vendors) > 0:
            where_clause += " AND po.partner_id = ANY(%s)"

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        args = [from_date, to_date]

        if state != 'all':
            args.append(state)

        if depts is not None and len(depts) > 0:
            args.append(account_analytic_ids.ids)

        if vendors is not None and len(vendors) > 0:
            args.append(vendor_ids.ids)

        cr.execute(sql, args)

        purchase_lines_by_partner = cr.dictfetchall()
        purchase_period_total = sum([k['y'] for k in purchase_lines_by_partner])

        select_clause = """SELECT aa.name AS name,
                ABS(COALESCE(SUM(pol.price_subtotal + pol.price_tax), 0)) as y """

        from_clause = """ FROM purchase_order_line pol 
                JOIN account_analytic_account aa ON (pol.account_analytic_id = aa.id)
                JOIN purchase_order po ON (pol.order_id = po.id)"""
        where_clause = """ WHERE po.date_order BETWEEN to_date(%s, 'mm/dd/yyyy') AND to_date(%s, 'mm/dd/yyyy')
                AND pol.account_analytic_id = ANY(%s) AND po.partner_id = ANY(%s)"""
        group_by_clause = """ GROUP BY aa.name"""

        if state != 'all':
            where_clause += " AND po.state = %s"

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        if state != 'all':
            cr.execute(sql, (from_date, to_date, account_analytic_ids.ids, vendor_ids.ids, state,))
        else:
            cr.execute(sql, (from_date, to_date, account_analytic_ids.ids, vendor_ids.ids,))

        purchase_lines_by_department = cr.dictfetchall()

        select_clause = """SELECT count(distinct(po.id)) AS po_count"""
        from_clause = """ FROM purchase_order_line pol JOIN purchase_order po ON (pol.order_id = po.id)"""
        where_clause = """ WHERE po.date_order BETWEEN to_date(%s, 'mm/dd/yyyy') AND to_date(%s, 'mm/dd/yyyy')"""
        group_by_clause = """"""

        if state != 'all':
            where_clause += " AND po.state = %s"

        if depts is not None and len(depts) > 0:
            where_clause += " AND pol.account_analytic_id = ANY(%s)"

        if vendors is not None and len(vendors) > 0:
            where_clause += " AND po.partner_id = ANY(%s)"

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        args = [from_date, to_date]

        if state != 'all':
            args.append(state)

        if depts is not None and len(depts) > 0:
            args.append(account_analytic_ids.ids)

        if vendors is not None and len(vendors) > 0:
            args.append(vendor_ids.ids)

        cr.execute(sql, args)

        purchase_order_count = cr.fetchone()[0] or 0

        result = {
            "purchase_by_department": purchase_lines_by_department,
            "purchase_period_total": purchase_period_total,
            "purchase_by_partner": purchase_lines_by_partner,
            "purchase_count": purchase_order_count
        }
        return result

    @api.model
    def get_quarter_purchase_data(self, year, quarter):
       
        quarter = quarter or 'Q1'
        cr = self.env.cr
        date_condition = ""
        if quarter == 'Q1':
            date_condition = \
                "between to_date('{}-01-01', 'yyyy-mm-dd') and to_date('{}-03-31', 'yyyy-mm-dd')".format(str(year),
                                                                                                         str(year))
        if quarter == 'Q2':
            date_condition = \
                "between to_date('{}-04-01', 'yyyy-mm-dd') and to_date('{}-06-30', 'yyyy-mm-dd')".format(str(year),
                                                                                                         str(year))
        if quarter == 'Q3':
            date_condition = \
                "between to_date('{}-07-01', 'yyyy-mm-dd') and to_date('{}-09-30', 'yyyy-mm-dd')".format(str(year),
                                                                                                         str(year))
        if quarter == 'Q4':
            date_condition = \
                "between to_date('{}-10-01', 'yyyy-mm-dd') and to_date('{}-12-31', 'yyyy-mm-dd')".format(str(year),
                                                                                                         str(year))
        select_clause = """ SELECT sum(amount_total) AS total_amount """
        from_clause = """ FROM purchase_order """
        where_clause = """ WHERE date_order {} AND state IN ('done', 'purchase') """.format(date_condition)
        group_by_clause = """"""

        sql = (select_clause + from_clause + where_clause + group_by_clause)
        cr.execute(sql,)

        purchase_quarter_total = cr.fetchone()[0] or 0.0

        select_clause = """SELECT aa.name AS name,
        ABS(COALESCE(SUM(pol.price_subtotal + pol.price_tax), 0)) as y """
        from_clause = """ FROM purchase_order_line pol 
        JOIN account_analytic_account aa ON (pol.account_analytic_id = aa.id)
        JOIN purchase_order po ON (pol.order_id = po.id)"""
        where_clause = """ WHERE po.date_order {} AND po.state IN ('done', 'purchase') """.format(date_condition)
        group_by_clause = """ GROUP BY aa.name"""

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        cr.execute(sql,)

        purchase_lines_by_department = cr.dictfetchall()

        select_clause = """SELECT rp.name AS name,
               ABS(COALESCE(SUM(po.amount_total), 0)) as y """
        from_clause = """ FROM purchase_order po 
        JOIN res_partner rp ON (po.partner_id = rp.id)"""
        where_clause = """ WHERE po.date_order {} AND po.state IN ('done', 'purchase') """.format(date_condition)
        group_by_clause = """ GROUP BY rp.name"""

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        cr.execute(sql,)

        purchase_lines_by_partner = cr.dictfetchall()

        select_clause = """SELECT count(id) AS po_count """
        from_clause = """ FROM purchase_order """
        where_clause = """ WHERE date_order {} AND state IN ('done', 'purchase') """.format(date_condition)
        group_by_clause = """"""

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        cr.execute(sql,)

        purchase_order_count = cr.fetchone()[0] or 0

        select_clause = """SELECT count(id) AS pr_count"""
        from_clause = """ FROM purchase_request """
        where_clause = """ WHERE date {} AND state = 'done' """.format(date_condition)
        group_by_clause = """"""

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        cr.execute(sql,)

        purchase_request_count = cr.fetchone()[0] or 0

        select_clause = """SELECT count(id) AS cr_count"""
        from_clause = """ FROM contract_contract """
        where_clause = """ WHERE date {} AND state = 'closed' AND contract_type = 'purchase'""".format(date_condition)
        group_by_clause = """"""

        sql = (select_clause + from_clause + where_clause + group_by_clause)

        cr.execute(sql,)

        contract_count = cr.fetchone()[0] or 0

        result = {
            "purchase_by_department": purchase_lines_by_department,
            "purchase_quarter_total": purchase_quarter_total,
            "purchase_by_partner": purchase_lines_by_partner,
            "purchase_order_count": purchase_order_count,
            "purchase_request_count": purchase_request_count,
            "contract_count": contract_count,
        }
        return result
