from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from odoo.tools.misc import get_lang



# for test only
# class HrDepartment(models.Model):
#     _inherit = 'hr.department'

#     analytic_account_id = fields.Many2one('account.analytic.account',
#                                           'Analytic Account')
class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def _default_emp(self):
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if emp:
            return emp  # .id
        else:
            raise ValidationError(_("this user has no related emplyee!"))

    name = fields.Char(string='Name', copy=False, default=lambda self: '/')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  default=lambda s: s._default_emp().id)
    department_id = fields.Many2one('hr.department', 'Department')
    line_ids = fields.One2many(comodel_name='purchase.request.line', inverse_name='request_id', string='')

    date = fields.Date(string='Date', default=fields.Date.context_today, )
    state = fields.Selection(
        [('draft', 'Draft'), ('direct manager', 'Direct Manager'),
          ('send_budget', 'Send to Budget Confirmation'), ('wait_budget', 'Wait Budget'),
         ('budget_approve', 'Budget Approved'), ('waiting', 'In Purchase'),
         ('done', 'Done'), ('cancel', 'Cancel'), ('refuse', 'Refuse')], default="draft", tracking=True, )
    product_category_ids = fields.Many2many('product.category', string='Items Categories')
    it_categ = fields.Boolean()
    purchase_purpose = fields.Char("Purpose", default="/")
    note = fields.Text(string='Note')
    amount_total = fields.Float(string="Amount Total")
    partner_id = fields.Many2one(string='Vendor', comodel_name='res.partner')

    # New Added
    type = fields.Selection([
        ('project', 'Project'),
        ('operational', 'Operational')
    ], default='operational')
    project_id = fields.Many2one('project.project', string='Project')
    project_stage_id = fields.Many2one('project.phase', string='Project Stage')
    is_analytic = fields.Boolean("Use Analytic Account")

    type_id = fields.Many2one('purchase.requisition.type', string="Agreement Type")

    requesting_administration = fields.Selection([
        ('planned for', 'Planned For'),
        ('emergency', 'Emergency')
    ], string="Requesting Administration(hghh)")

    planned_for = fields.Boolean(string="Planned For")
    emergency = fields.Boolean(string="Emergency")

    available = fields.Boolean(string="Available")
    unavailable = fields.Boolean(string="Unavailable")
    specifications_conform = fields.Boolean(string="Technical specifications conform")
    specifications_not_conform = fields.Boolean(string="Technical specifications do not match")
    confirmation_ids = fields.One2many('budget.confirmation','request_id')

    def open_confirmation(self):
        formview_ref = self.env.ref('account_budget_custom.view_budget_confirmation_form', False)
        treeview_ref = self.env.ref('account_budget_custom.view_budget_confirmation_tree', False)
        return {
            'name': ("Budget  Confirmation"),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'budget.confirmation',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % self.confirmation_ids.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {'create':False}
        }

    # get analytic account based on type of request
    # @api.onchange('type', 'line_ids')
    # def on_change_line(self):
    #     for line in self.line_ids:
    #         if self.type == 'operational':
    #             line.account_id = self.department_id.analytic_account_id
    #         elif self.type == 'project':
    #             line.account_id = self.project_id.analytic_account_id
    #             # # get analytic account onchanage project name

    # @api.onchange('type', 'project_id', 'line_ids')
    # def on_change_proj_name(self):
    #     for line in self.line_ids:
    #         if self.project_id:
    #             line.account_id = self.project_id.analytic_account_id
    #         self.set_line_vendor_prices(line)
    #         self.set_line_maxmin_prices(line)

    # test empty department
    @api.onchange('employee_id', 'department_id', 'line_ids')
    def onchange_emp_depart(self):
        for line in self.line_ids:
            if self.employee_id and not self.department_id:
                raise ValidationError(_("Please Select department for employee"))

    # get vendor price
    def set_line_vendor_prices(self, line):
        price = 0
        sellers = line.product_id.seller_ids.filtered(lambda seller: seller.name.id == self.partner_id.id)
        if len(sellers) >= 1:
            price = sellers[0].price

        if line.price_unit <= 0:
            line.update({
                'price_unit': price,
            })

    # get max and min
    def set_line_maxmin_prices(self, line):
        prices_list = []
        purchase_orders = self.env['purchase.order'].search([('partner_id', '=', self.partner_id.id)])
        for po in purchase_orders:
            line_ids = po.mapped('order_line')
            for pl in line_ids:
                if line.product_id.id == pl.product_id.id:
                    prices_list.append(pl.price_unit)

        if prices_list:
            line.write({
                'max_price': max(prices_list),
                'min_price': min(prices_list),
            })

    @api.onchange('type', 'project_id')
    def _onchange_project_id(self):
        if self.type != 'project':
            self.project_stage_id = False
            self.project_id = False

    purchase_create = fields.Boolean(string='Purchase Create')
    by_purchase = fields.Boolean('Requested by Purchase')

    @api.onchange('employee_id', 'by_purchase')
    def change_employee_id(self):
        if self.employee_id and self.by_purchase:
            self.department_id = self.employee_id.department_id.id
        else:
            self.employee_id = self._default_emp().id
            self.department_id = self._default_emp().department_id.id

    def action_confirm(self):
        if len(self.line_ids) == 0:
            raise ValidationError(_("Can't Confirm Request With No Item!"))
        if not self.department_id:
            raise ValidationError(_("Please Select department for employee"))
        else:
            self.write({
                'state': 'direct manager'
            })
            # Send Notifications

            subject = _('Purchase Request Confirmation') + ' - {}'.format(self.name)
            message = '{} '.format(self.name) + _('need your confirmation.') + '\n' + _('Create Date: ') + '{}'.format(
                self.create_date)
            group = 'purchase_requisition_custom.group_direct_manger'
            author_id = self.env.user.partner_id.id or None
            self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                               group=group)

        if self.name == '/':
            self.name = self.env['ir.sequence'].next_by_code('stock.request.order') or '/'

    def approve_department(self):
        self.write({
            'state': 'send_budget'
        })
        # Send Notifications
        subject = _('Purchase Requset Approve') + ' - {}'.format(self.name)
        message = '{} '.format(self.name) + _('need your approve.') + '\n' + _('Create Date: ') + '{}'.format(
            self.create_date)
        group = 'purchase_requisition_custom.group_department_approve'
        author_id = self.env.user.partner_id.id or None
        self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                           group=group)


    def action_refuse(self):
        self.write({
            'state': 'refuse'
        })

    def action_refuse_department(self):
        self.write({
            'state': 'refuse'
        })

    def action_done(self):
        self.write({
            'state': 'done'
        })


    def action_budget(self):
        confirmation_lines = []
        amount = 0
        for rec in self.line_ids:
            if rec.request_id.is_analytic:
                analytic_account = rec.account_id
            else:
                analytic_account = rec.request_id.department_id.analytic_account_id
            if not analytic_account:
                raise ValidationError(_('There is no analytic account for this purchase request'))
            if not (rec.product_id.property_account_expense_id.id and
                    rec.product_id.property_account_expense_id.id or
                    rec.product_id.categ_id.property_account_expense_categ_id.id):
                raise ValidationError(_("This product has no expense account") + ': {}'.format(rec.product_id.name))
            budget_lines = analytic_account.crossovered_budget_line.filtered(
                lambda x:
                x.crossovered_budget_id.state == 'done' and
                fields.Date.from_string(x.date_from) <= fields.Date.from_string(
                    self.date) <= fields.Date.from_string(x.date_to))
            if budget_lines:
                remain = abs(budget_lines[0].remain)
                amount = amount + rec.sum_total
                new_remain = remain - amount
                confirmation_lines.append((0, 0, {
                    'amount': rec.sum_total,
                    'analytic_account_id': analytic_account.id,
                    'description': rec.product_id.name,
                    'budget_line_id': budget_lines[0].id,
                    'remain': new_remain + rec.sum_total,
                    'new_balance': new_remain,
                    'account_id': rec.product_id.property_account_expense_id.id and rec.product_id.property_account_expense_id.id or rec.product_id.categ_id.property_account_expense_categ_id.id
                }))
            else:
                raise ValidationError(
                    _(''' No budget for this service ''') + ': {} - {}'.format(rec.product_id.name,
                                                                               analytic_account.name))

                # Create budget.confirmation
        if confirmation_lines:
            data = {
                'name': self.name,
                'date': self.date,
                'beneficiary_id': self.partner_id.id,
                'department_id': self.department_id.id,
                'type': 'purchase.request',
                'ref': self.name,
                'description': self.purchase_purpose,
                'total_amount': amount,
                'lines_ids': confirmation_lines,
                'request_id': self.id,
                'planned_for': self.planned_for,
                'emergency': self.emergency,
                'available': self.available,
                'unavailable': self.unavailable,
                'specifications_conform': self.specifications_conform,
                'specifications_not_conform': self.specifications_not_conform,
            }
            budget_id = self.env['budget.confirmation'].create(data)
            subject = _('New Purchase Request')
            message = _(
                "New Budget Confirmation Has Been Created for Purchase Request %s to Beneficiary %s in total %s" % (
                    budget_id.name, budget_id.beneficiary_id.name, budget_id.total_amount))
            group = 'purchase.group_purchase_manager'
            author_id = self.env.user.partner_id.id or None
            self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                               group=group)
            self.write({'state': 'wait_budget'})




    def create_requisition(self):
        if not self.employee_id.department_id:
            raise ValidationError(_("Choose A Department For this Employee!"))
        line_ids = []
        for line in self.line_ids:
            line_ids.append((0, 6, {
                'product_id': line.product_id.id,
                'department_id': line.request_id.department_id.id or False,
                'product_qty': line.qty,
                'name': line.name,
                'account_analytic_id': line.account_id.id,
            }))
        requisition_id = self.env['purchase.requisition'].sudo().create({
            'category_ids': self.product_category_ids.ids,
            'type_id_test': self.type_id.id,
            'department_id': self.employee_id.department_id.id,
            'type': self.type,
            'project_id': self.project_id.id,
            'project_stage_id': self.project_stage_id.id,
            'purpose': self.purchase_purpose,
            'request_id': self.id,
            'user_id': self.employee_id.user_id.id,
            'is_analytic': self.is_analytic,
            'line_ids': line_ids
        })
        self.write({
            'purchase_create': True
        })

        return {
            'name': "Request for Quotation",
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'view_mode': 'form',
            'res_id': requisition_id.id,
        }


    def create_purchase_order2(self):
        line_ids = []
        for line in self.line_ids:
            line_ids.append((0, 6, {
                'product_id': line.product_id.id,
                'product_qty': line.qty,
                'name': line.product_id.name,
                'department_name': self.employee_id.department_id.id,
                'account_analytic_id': line.account_id.id,
                'initial_amount': line.sum_total,
            }))

        purchase_order = self.env['purchase.order'].sudo().create({
            'category_ids': self.product_category_ids.ids,
            'origin': self.name,
            'request_id': self.id,
            'project_id': self.project_id.id,
            'project_stage_id': self.project_stage_id.id,
            'partner_id': self.partner_id.id,
            'purpose': self.purchase_purpose,
            'purchase_cost': 'product_line',
            'order_line': line_ids
        })
        self.write({
            'purchase_create': True
        })

        return {
            'name': "Purchase orders from employee",
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': purchase_order.id,
        }

    def create_po(self):
        if not self.employee_id.department_id:
            raise ValidationError(_("Choose A Department For this Employee!"))
        if not self.partner_id:
            raise ValidationError(_("Please Select A Vendor."))
        line_ids = []
        state = None
        if self.env.user.company_id.purchase_budget:
            state = 'wait_for_send'
        else:
            state = 'draft'
        analytic_account = False
        if self.department_id and self.department_id.analytic_account_id:
            analytic_account = self.department_id.analytic_account_id.id
        for line in self.line_ids:
            line_ids.append((0, 6, {
                'product_id': line.product_id.id,
                'product_qty': line.qty,
                'name': line.product_id.name,
                'date_planned': datetime.today(),
                'product_uom': line.product_id.uom_id.id,
                'account_analytic_id': analytic_account,
                'price_unit': 0,
            }))

            po = self.env['purchase.order'].sudo().create({
                'category_ids': self.product_category_ids.ids,
                'origin': self.name,
                'request_id': self.id,
                'date_order': datetime.today(),
                'project_id': self.project_id.id,
                'project_stage_id': self.project_stage_id.id,
                'partner_id': self.partner_id.id,
                'purpose': self.purchase_purpose,
                'purchase_cost': 'product_line',
                'department_id': self.employee_id.department_id.id,
            })

        self.write({
            'purchase_create': True
        })

        return {
            'name': "Request for Quotation",
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
        }

    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You cant delete record not in darft state!"))
        res = super().unlink()
        return res


class PurchaseRequestLine(models.Model):
        _name = 'purchase.request.line'
        _description = 'purchase request line'

        # for test
        account_id = fields.Many2one('account.analytic.account',
                                     'Analytic Account')
        request_id = fields.Many2one(comodel_name='purchase.request', string='Request Ref.')
        product_id = fields.Many2one(comodel_name='product.product', string='Item')
        qty = fields.Integer(string='Qty')
        name = fields.Char(string='Descrption')
        name_text = fields.Char(string='category')
        name_text1 = fields.Char(string='Specifications')
        price_unit = fields.Float(string='Unit Price', digits='Product Price')
        max_price = fields.Float(string='Maximum Price')
        min_price = fields.Float(string='Minimum Price')
        uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
        sum_total = fields.Float(String="sum_total")

        @api.onchange('qty', 'price_unit')
        def total_sum_lines(self):
            sum_total = 0
            # for line in self.line_ids:
            if self.price_unit and self.qty:
                self.sum_total = self.qty * self.price_unit

        # get price for product
        def _product_id_change(self):
            if not self.product_id:
                return

            product_lang = self.product_id.with_context(
                lang=get_lang(self.env, self.partner_id.lang).code,
                partner_id=self.partner_id.id,
                company_id=self.company_id.id,
            )
            self.name = self._get_product_purchase_description(product_lang)

        @api.constrains('qty')
        def qty_validation(self):
            for rec in self:
                if rec.qty <= 0:
                    raise ValidationError(_("Item Quantity MUST be at Least ONE!"))


    # search on purchase request or  purchase order
# search on purchase request or  purchase order
class ProductsSearch(models.Model):
    _inherit = 'product.product'
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        product_ids = []
        res = super(ProductsSearch, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                           name_get_uid=name_get_uid)
        if name:
            product_ids = list(self._search([('description', 'ilike', name)] + args, limit=limit))
        if product_ids:
            res += product_ids
        return res


class Employee(models.Model):
    _inherit = 'hr.employee'

    def name_get(self):
        get_all = self.env.context.get('get_all', False)
        department = self.env.context.get('department', False)
        employees = None
        result = []
        domain = []
        if department:
            domain += [('department_id', '=', department)]
        if get_all:
            employees = self.env['hr.employee'].sudo().search(domain)
            result = [(employee.id, employee.name) for employee in employees]
            return result
        else:
            return super(Employee, self).name_get()
