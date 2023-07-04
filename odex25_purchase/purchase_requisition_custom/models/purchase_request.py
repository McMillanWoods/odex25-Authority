from datetime import datetime

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


# for test only
# class HrDepartment(models.Model):
#     _inherit = 'hr.department'

#     analytic_account_id = fields.Many2one('account.analytic.account',
#                                           'Analytic Account')
class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # dupicate employee request record
    def copy(self, default=None):
        data = super(PurchaseRequest, self).copy(default)
        data.state = 'draft'
        # data.line_ids = self.line_ids
        data.purchase_create = False
        return data

    @api.model
    def _default_emp(self):
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if emp:
            return emp
        else:
            raise ValidationError(_("this user has no related emplyee!"))

    @api.model
    def _get_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        p_type = self.picking_type_id
        if not (p_type and p_type.code == 'incoming' and (
                p_type.warehouse_id.company_id == self.company_id or not p_type.warehouse_id)):
            self.picking_type_id = self._get_picking_type(self.company_id.id)

            # name = fields.Char(string='Name', copy=False, default=lambda self:'/')

    name = fields.Char(string='Name', required=True,
                       readonly=True, default=lambda self: _('New'), copy=False)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  default=lambda s: s._default_emp().id, )
    department_id = fields.Many2one('hr.department', 'Department')
    line_ids = fields.One2many(comodel_name='purchase.request.line', inverse_name='request_id', copy=True)

    date = fields.Date(string='Date', default=fields.Date.context_today, copy=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('direct manager', 'Direct Manager'), ('department manager', 'Department Manager'),
         ('waiting', 'In Purchase'),
         ('done', 'Done'), ('cancel', 'Cancel'), ('refuse', 'Refuse')], default="draft", tracking=True, )
    product_category_ids = fields.Many2many('product.category', string='Items Categories')
    it_categ = fields.Boolean()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    purchase_purpose = fields.Char("Purpose", default="/")
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=Purchase.READONLY_STATES,
                                      required=True, default=_default_picking_type,
                                      domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
                                      help="This will determine operation type of incoming shipment")
    note = fields.Text(string='Note')
    partner_id = fields.Many2one(
        string='Vendor',
        comodel_name='res.partner'
    )

    # New Added
    type = fields.Selection([
        ('project', 'Project'),
        ('operational', 'Operational')
    ], default='operational')
    project_id = fields.Many2one('project.project', string='Project')
    project_stage_id = fields.Many2one('project.phase', string='Project Stage')

    # get analytic account based on type of request
    @api.onchange('type', 'line_ids')
    def on_chanage_line(self):
        for line in self.line_ids:
            if self.type == 'operational':
                line.account_id = self.department_id.analytic_account_id
            elif self.type == 'project':
                line.account_id = self.project_id.analytic_account_id
                # get analytic account onchanage project name

    @api.onchange('type', 'project_id', 'line_ids')
    def on_chanage_proj_name(self):
        for line in self.line_ids:
            if self.project_id:
                line.account_id = self.project_id.analytic_account_id

                # ddddd
            self.set_line_vendor_prices(line)
            self.set_line_maxmin_prices(line)

    # test empyty department
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

    # get max and min for product from purchase order
    def set_line_maxmin_prices(self, line):
        prices_list = []
        partner_purchase_orders = self.env['purchase.order'].search(
            [('state', '=', 'purchase'), ('partner_id', '=', self.partner_id.id)])
        for po in partner_purchase_orders:
            line_ids = po.mapped('order_line')
            for pl in line_ids:
                if line.product_id.id == pl.product_id.id:
                    prices_list.append(pl.price_unit)

        all_purchase_orders = self.env['purchase.order'].search([('state', '=', 'purchase')])
        for po in all_purchase_orders:
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
            raise ValidationError(_("Can't Confirm Requset With No Item!"))
        if not self.department_id:
            raise ValidationError(_("Please Select department for employee"))
        else:
            self.write({
                'state': 'direct manager'
            })
            # Send Notifications
            subject = _('Purchase Requset Confirmation') + ' - {}'.format(self.name)
            message = '{} '.format(self.name) + _('need your confirmation.') + '\n' + _('Create Date: ') + '{}'.format(
                self.create_date)
            group = 'purchase_requisition_custom.group_direct_manger'
            author_id = self.env.user.partner_id.id or None
            self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                               group=group)

    # create sequence for purchase request
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.request.order') or _('New')
        res = super(PurchaseRequest, self).create(vals)
        return res

    def approve_department(self):
        self.write({
            'state': 'department manager'
        })
        # Send Notifications
        subject = _('Purchase Requset Approve') + ' - {}'.format(self.name)
        message = '{} '.format(self.name) + _('need your approve.') + '\n' + _('Create Date: ') + '{}'.format(
            self.create_date)
        group = 'purchase_requisition_custom.group_department_approve'
        author_id = self.env.user.partner_id.id or None
        self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                           group=group)

    def it_approve(self):
        self.write({
            'state': 'waiting'
        })

    def action_approve(self):
        # it_categ = False
        # for product_category in self.product_category_ids:
        #     if product_category.it_categ:
        #         it_categ = True
        #         break
        #
        # for line in self.line_ids:
        #     if line.product_id.categ_id.it_categ:
        #         it_categ = True
        #         break
        #
        # if it_categ is True:
        #     self.write({
        #         'state': 'it manager'
        #     })
        #     # Send Notifications
        #     subject = _('Purchase Requset IT Approve') + ' - {}'.format(self.name)
        #     message = '{} '.format(self.name) + _('need your approve.') + '\n' + _('Create Date: ') + '{}'.format(
        #         self.create_date)
        #     group = 'purchase_requisition_custom.group_it_purchase_requisition'
        #     author_id = self.env.user.partner_id.id or None
        #     self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
        #                                                        group=group)
        #
        #     self.it_categ = True
        # else:
        #     self.write({
        #         'state': 'waiting'
        #     })
        #     self.it_categ = False
        self.write({
            'state': 'waiting'
        })

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
            'department_id': self.employee_id.department_id.id,
            'type': self.type,
            'project_id': self.project_id.id,
            'project_stage_id': self.project_stage_id.id,
            'purpose': self.purchase_purpose,
            'request_id': self.id,
            'user_id': self.env.user.id,
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
            }))

        purchase_order = self.env['purchase.order'].create({
            'category_ids': self.product_category_ids.ids,
            'origin': self.name,
            'company_id': self.env.company.id,
            'request_id': self.id,
            'project_id': self.project_id.id,
            'picking_type_id': self.picking_type_id.id,
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
    name = fields.Char(
        string='Descrption'
    )
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    max_price = fields.Float(string='Maximum Price')
    min_price = fields.Float(string='Minimum Price')

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
