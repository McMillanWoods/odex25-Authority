# -*- coding: utf-8 -*-

from lxml import etree
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero
from dateutil.relativedelta import relativedelta



class PurchaseRequisitionLineCustom(models.Model):
    _inherit = 'purchase.requisition.line'

    product_id = fields.Many2one('product.product', string='Product', domain=lambda self: [('purchase_ok', '=', True)],
                                 required=True)
    product_uom_id = fields.Many2one(related="product_id.uom_id")
    name = fields.Char(string="Description")
    department_id = fields.Many2one("hr.department")

    @api.model
    def create(self, vals):
        new_id = super(PurchaseRequisitionLineCustom, self).create(vals)
        return new_id


class PurchaseRequisitionCustom(models.Model):
    _inherit = 'purchase.requisition'

    # committee type
    committee_type_id = fields.Many2one('purchase.committee.type', string='Committee Type')
    state_blanket_order = fields.Selection(
        selection_add=[('purchase_manager', 'Purchase manager'), ('checked', 'Waiting Approval'),
                       ('committee', 'Committee'),
                       ('purchase_manager', 'Purchase manager'),
                       ('second_approve', 'Second Approval'),
                       ('legal_counsel', 'Legal Counsel'),
                       ('third_approve', 'Third Approval'),
                       ('accept', 'Accepted'),
                       ('open', 'Bid Selection'),
                       ('waiting', 'Waiting For Budget Confirmation'),
                       ('checked', 'Waiting Approval'),
                       ('done', 'Done'),
                       ('checked', 'Waiting Approval'),
                       ('approve', 'Approved'),
                       ('cancel', 'cancelled'),
                       ])

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'Confirmed'),
        ('committee', 'Committee'),
        ('purchase_manager', 'Purchase manager'),
        ('second_approve', 'Second Approval'),
        ('legal_counsel', 'Legal Counsel'),
        ('third_approve', 'Third Approval'),
        ('accept', 'Accepted'),
        ('open', 'Bid Selection'),
        ('waiting', 'Waiting For Budget Confirmation'),
        ('checked', 'Waiting Approval'),
        ('done', 'Done'),
        ('checked', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('cancel', 'cancelled'),

    ])
    type = fields.Selection([
        ('project', 'Project'),
        ('operational', 'Operational')
    ], default='operational')
    project_id = fields.Many2one('project.project', string='Project')
    project_stage_id = fields.Many2one('project.phase', string='Project Stage')
    sent_to_commitee = fields.Boolean('Is Sent to Commitee?', default=False)

    @api.onchange('type', 'project_id')
    def _onchange_project_id(self):
        if self.type != 'project':
            self.project_stage_id = False
            self.project_id = False

    ordering_date = fields.Date(default=fields.Datetime.now)
    name = fields.Char(string='Agreement Reference', required=True, copy=False)
    department_id = fields.Many2one('hr.department')
    purpose = fields.Char()
    category_ids = fields.Many2many('product.category', string='Categories')
    account_analytic_id = fields.Many2one("account.analytic.account")
    purchase_commitee = fields.Boolean('Purchase Commitee?')
    committe_head = fields.Many2one('res.users', 'Committe Head')

    committe_members = fields.Many2many('res.users', string='Purchase Committee')
    min_approve = fields.Integer('No. of Selections')
    min_vote = fields.Integer('No. of Vots')
    actual_vote = fields.Integer('No. of Vots')
    request_id = fields.Many2one('purchase.request', 'Request Ref.')
    purchase_cost = fields.Selection(
        [('department', 'Department'), ('default', 'Default Cost Center'), ('product_line', 'Product Line'),
         ('project', 'Project')],
        string='Purchase Cost', default='department')
    selected_purchase_id = fields.Many2one("purchase.order", compute="_compute_selected_purchase_order")

    is_purchase_budget = fields.Boolean(string="Is Purchase Budget", compute='_compute_purchase_budget')

    type_id_test = fields.Many2one('purchase.requisition.type', string="Agreement Type", required=True)
    Project_name = fields.Char(string='Project name')
    Chair_number = fields.Char(string='Chair number')
    agreement_data = fields.Date(string="Agreement data")
    city_name = fields.Char(string="City")
    department_id = fields.Many2one('hr.department')
    days_count = fields.Char(   string='days_count',compute='_compute_days')
    is_analytic = fields.Boolean("Use Analytic Account")



    # @api.onchange('purchase_cost', 'line_ids', 'lines_ids.product_id')
    # def on_change_purchase_cost(self):
    #     for line in self.line_ids:
    #         if self.purchase_cost == 'department':
    #             line.account_analytic_id = self.department_id.analytic_account_id
    #             line.department_id = self.department_id.id
    #         elif self.purchase_cost == 'default':
    #             line.account_analytic_id = self.env.user.company_id.purchase_analytic_account
    #         elif self.purchase_cost == 'project':
    #             line.account_analytic_id = self.project_id.analytic_account_id

    # @api.onchange('purchase_cost')
    # def on_change_purchase_cost_value(self):
    #     if self.purchase_cost == 'project':
    #         self.type = 'project'
    #         # get depertment when type project

    @api.onchange('purchase_cost', 'line_ids', 'department_id')
    def on_project_type_department(self):
        for line in self.line_ids:
            if self.purchase_cost == 'project' and self.department_id:
                line.department_id = self.department_id

    # @api.onchange('purchase_cost', 'type', 'line_ids', 'lines_ids.product_id')
    # def change_product_line(self):
    #     for line in self.line_ids:
    #         if self.purchase_cost == 'product_line' and self.type == 'operational':
    #             line.account_analytic_id = line.department_id.analytic_account_id
    #         elif self.purchase_cost == 'product_line' and self.project_id:
    #             line.account_analytic_id = self.project_id.analytic_account_id

    @api.onchange('department_id', 'line_ids', )
    def change_department(self):
        for line in self.line_ids:
            if self.department_id and self.purchase_cost == 'department':
                line.department_id = self.department_id

    # @api.onchange('project_id', 'line_ids', )
    # def change_project(self):
    #     for line in self.line_ids:
    #         if self.purchase_cost == 'product_line' and self.type == 'project':
    #             line.account_analytic_id = self.project_id.analytic_account_id
    #         elif self.purchase_cost == 'project' and self.type == 'project':
    #             line.account_analytic_id = self.project_id.analytic_account_id

    def _compute_purchase_budget(self):
        purchase_budget = self.env.company.purchase_budget
        for rec in self:
            if purchase_budget:
                rec.is_purchase_budget = True
            else:
                rec.is_purchase_budget = False

    def action_skip_purchase_budget(self):
        """ Skip purchase budget"""
        purchase_orders = self.env['purchase.order'].search([
            ('requisition_id', '=', self.id),
        ])

        for po_id in purchase_orders:
            # Deal with double validation process
            valid_amount = self.env.user.company_id.currency_id.compute(po_id.company_id.po_double_validation_amount,
                                                                        po_id.currency_id)
            # second_amount = self.env.user.company_id.currency_id.compute(po_id.company_id.second_approve, po_id.currency_id)
            if po_id.company_id.po_double_validation == 'one_step' \
                    or (po_id.company_id.po_double_validation == 'two_step' \
                        and po_id.amount_total > valid_amount):
                po_id.write({'state': 'to approve'})
                self.write({
                    'state': 'checked'
                })
            else:
                if po_id.email_to_vendor:
                    po_id.write({'state': 'sent'})
                else:
                    po_id.write({'state': 'draft'})

                po_id.write({'send_to_budget': False})

                self.write({
                    'state': 'approve'
                })

        # for order in self.purchase_ids.filtered(lambda x: x.state == 'sign'):
        #     order.write({
        #             'state': 'draft',
        #         })

        # self.write({
        #         'state': 'approve'
        #     })





    def _compute_days(self):
        self.days_count = _("Unknown")
        for rec in self:
            if rec.schedule_date and rec.ordering_date:
                schedule_date = fields.Date.from_string(rec.schedule_date)
                ordering_date = fields.Date.from_string(rec.ordering_date)
                diff_time = (schedule_date - ordering_date).days
                rec.days_count = diff_time

    def _compute_selected_purchase_order(self):
        for pr in self:
            if len(pr.purchase_ids) > 0:
                orders = pr.purchase_ids.filtered(lambda po: po.state in ['purchase', 'sign', 'done'])
                if len(orders) > 0:
                    pr.selected_purchase_id = orders[0]

    @api.constrains('min_approve')
    def min_approve_validation(self):
        if self.purchase_commitee and self.min_approve == 0:
            raise ValidationError(_("No. of Selections cannot be Zero"))

    @api.constrains('min_approve', 'min_vote')
    def check_min_vote_and_approve(self):
        if self.min_approve > len(self.committe_members):
            raise UserError(_("Minimum approves cannot be greater than members count = " +
                              str(len(self.committe_members))))
        elif self.min_vote > len(self.committe_members):
            raise UserError(_("Minimum votes cannot be greater than members count = " +
                              str(len(self.committe_members))))

    @api.model
    def get_seq_to_view(self):
        """
            Create the Sequence
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        """
            Set the created sequence to the name of the document
        """
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.seq') or '/'
        # vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.requisition.sequence') or '/'
        return super(PurchaseRequisitionCustom, self).create(vals)

    @api.model
    def postmessage(self):
        """
            this function is to create message in the model when the budget confirmation 
            canceled
        """
        self.message_post(
            body=_('Budget Confirmation is Canceled'),
            subtype='mail.mt_comment',
            author_id=self.create_uid.partner_id.id
        )

    # def committee_action_quotation(self):
    #     """
    #         this function is to create new purchase order from the purchase agreement
    #         when pressing Quotation button in the workflow
    #     """
    #     return {
    #         'name': " Committe Request for Quotation",
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'purchase.order',
    #         'view_mode': 'form,tree',
    #         'domain': [('requisition_id', '=', self.id)],
    #         'context': {
    #             "default_requisition_id": self.id,
    #             "default_category_id": self.category_ids.ids,
    #             "default_department_name": self.department_id.id,
    #             "default_purpose": self.purpose,
    #             "default_partner_ref": 123,
    #             "default_state": 'unsign',
    #             "default_committe_members": [(0, 0, {'user_id': user.id}) for user in  self.committe_members],
    #             "default_request_id": (self.request_id and self.request_id.id) or False},
    #     }

    def action_quotation(self):
        """
            this function is to create new purchase order from the purchase agreement
            when pressing Quotation button in the workflow
        """
        return {
            'name': "Request for Quotation",
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form,tree',
            'domain': [('requisition_id', '=', self.id)],
            'context': {
                "default_requisition_id": self.id,
                "default_department_name": self.department_id.id,
                "default_category_ids": self.category_ids.ids,
                "default_purpose": self.purpose,
                # "default_purchase_cost":'product_line',
                "default_state": 'draft',
                "default_send_to_budget": True,
                "default_request_id": self.request_id.id if self.request_id else False},
        }

    # def action_confirm(self):
    #     super(PurchaseRequisitionCustom, self).action_quotation()
    #          lines = []
    #     for l in self.order_line:
    #                 lines.append((0, 0, {
    #             "default_requisition_id": self.id,
    #                 "default_category_ids": self.category_ids.ids,
    #                 "default_department_name": self.department_id.id,
    #                 "default_purpose": self.purpose,
    #                 "default_partner_ref": 123,
    #                 "default_state": 'unsign',
    #                 "default_committe_members": [(0, 0, {'user_id': user.id}) for user in  self.committe_members],
    #                 "default_request_id": (self.request_id and self.request_id.id) or False},
    #                 ))}

    def action_in_progress(self):
        """
            This Function validate the product quantity
        """
        super(PurchaseRequisitionCustom, self).action_in_progress()

        for rec in self.line_ids:
            if rec.product_qty <= 0:
                raise ValidationError(_("Product Quantity Can't Be Zero or less"))
            # if self.line_ids.qty_ordered <= 0:
        #     raise ValidationError(_("Ordered Quantity Can't Be Zero or less"))
        if self.purchase_commitee and len(self.committe_members) == 0:
            raise ValidationError(_("Please add Committe Members"))

    def action_approve(self):
        purchase_orders = self.env['purchase.order'].search([
            ('requisition_id', '=', self.id),
        ])

        for po_id in purchase_orders:
            # Deal with double validation process
            valid_amount = self.env.user.company_id.currency_id.compute(po_id.company_id.po_double_validation_amount,
                                                                        po_id.currency_id)
            if po_id.company_id.po_double_validation == 'one_step' \
                    or (po_id.company_id.po_double_validation == 'two_step' \
                        and po_id.amount_total > valid_amount):
                po_id.write({'state': 'to approve'})
                self.write({
                    'state': 'second_approve'
                })
            else:
                if po_id.email_to_vendor:
                    po_id.write({'state': 'sent'})
                else:
                    po_id.write({'state': 'draft'})

                po_id.write({'send_to_budget': False})

                self.write({
                    'state': 'approve'
                })

    def second_approval(self):
        purchase_orders = self.env['purchase.order'].search([
            ('requisition_id', '=', self.id),
        ])

        for po_id in purchase_orders:
            # Deal with double validation process
            valid_amount = self.env.user.company_id.currency_id.compute(po_id.company_id.second_approve,
                                                                        po_id.currency_id)
            if po_id.company_id.po_double_validation == 'one_step' \
                    or (po_id.company_id.po_double_validation == 'two_step' \
                        and po_id.amount_total > valid_amount):
                po_id.write({'state': 'to approve'})
                self.write({
                    'state': 'third_approve'
                })

            else:
                if po_id.email_to_vendor:
                    po_id.write({'state': 'sent'})
                else:
                    po_id.write({'state': 'draft'})

                po_id.write({'send_to_budget': False})

                self.write({
                    'state': 'approve'
                })

    def third_approve(self):
        purchase_orders = self.env['purchase.order'].search([
            ('requisition_id', '=', self.id),
        ])

        for po_id in purchase_orders:
            if po_id.email_to_vendor:
                po_id.write({'state': 'sent'})
            else:
                po_id.write({'state': 'draft'})

            po_id.write({'send_to_budget': False})

            self.write({
                'state': 'approve'
            })

    def set_line_account_and_dept(self, line):
        department_id = self.department_id
        analytic_account = False
        if not self.is_analytic:
            analytic_account = self.department_id.analytic_account_id

        if not line.department_id:
            line.update({
                'department_id': department_id.id or False
            })
        line.update({
            'account_analytic_id': analytic_account.id or False
        })

    def action_budget(self):
        """
            This function create budget confirmation and check if the RFQ created
            and change the status of the document to the waiting
        """
        if self.order_count == 0:
            raise ValidationError(_("Please create RFQ first"))
        # Find all RFQs as sign
        purchase_orders = self.env['purchase.order'].search([('requisition_id', '=', self.id),('state', '=', 'sign')])


        if len(purchase_orders) == 0:
            raise ValidationError(_("Please Sign your RFQs first"))

        if not self.purchase_cost:
            raise ValidationError(_("No purchase cost for this agreement"))

        budget_confirmation_obj = self.env['budget.confirmation']
        analytic_account = None
        budget_lines = []


        # if not analytic_account and not product_line:
        #     raise ValidationError(_("Please put cost center to the department"))

        date = fields.Date.from_string(self.ordering_date)
        for order in purchase_orders:
            move_lines = []
            for rec in order.order_line:
                analytic_account = rec.account_analytic_id

                if not analytic_account:
                        raise ValidationError(
                            _("Please put cost center to the product line") + ': {}'.format(rec.product_id.name))

                if not (
                        rec.product_id.property_account_expense_id.id and rec.product_id.property_account_expense_id.id or rec.product_id.categ_id.property_account_expense_categ_id.id):
                    raise ValidationError(_("This product has no expense account") + ': {}'.format(rec.product_id.name))

                # Find Budget for line
                try:
                    budget_lines = analytic_account.crossovered_budget_line.filtered(
                        lambda x:
                        x.crossovered_budget_id.state == 'done' and
                        fields.Date.from_string(x.date_from) <= date and
                        fields.Date.from_string(x.date_to) >= date)
                except Exception as e:
                    budget_lines = None


                if budget_lines:

                    # Print reserve of budget_lines
                    budget_line_id = budget_lines[0].id
                    remain = abs(budget_lines[0].remain)
                    new_balance = remain - rec.price_unit
                    move_lines.append((0, 0, {
                        'amount': rec.price_subtotal,
                        'analytic_account_id': analytic_account.id,
                        'description': rec.product_id.name,
                        'budget_line_id': budget_line_id,
                        'remain': remain,
                        'new_balance': new_balance,
                        'account_id': rec.product_id.property_account_expense_id.id and rec.product_id.property_account_expense_id.id or rec.product_id.categ_id.property_account_expense_categ_id.id
                    }))

                else:
                    raise ValidationError(
                        _(''' No budget for this service ''') + ': {} - {}'.format(rec.product_id.name,
                                                                                   analytic_account.name))

            data = {
                'name': self.name,
                'date': self.ordering_date,
                'beneficiary_id': order.partner_id.id,
                'department_id': self.department_id.id,
                'type': 'purchase.order',
                'ref': self.name,
                'description': self.purpose,
                'total_amount': order.amount_untaxed,
                'lines_ids': move_lines,
                'po_id': order.id,
            }
            budget_id = budget_confirmation_obj.create(data)
            # Order to wait
            order.write({'state': 'waiting'})
            # Send Notifications
            subject = _('New Purchase Order')
            message = _(
                "New Budget Confirmation Has Been Created for Purchase Order %s to Beneficiary %s in total %s" % (
                    budget_id.name, budget_id.beneficiary_id.name, budget_id.total_amount))
            group = 'purchase.group_purchase_manager'
            author_id = self.env.user.partner_id.id or None
            self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                               group=group)

        self.write({'state': 'waiting'})

    def to_committee(self):
        orders = self.env['purchase.order'].search([
            ('requisition_id', '=', self.id),
        ])
        if not orders:
            raise ValidationError(_("Enter Quotations First!"))
        self.write({
            'state': 'committee',
            'sent_to_commitee': True,
        })

    def action_accept(self):
        """
            Change the doucment status to accept state
        """
        if self.purchase_cost == 'project':
            if not self.project_id.analytic_account_id:
                raise ValidationError(_("No analytic account for the project"))

        for line in self.line_ids:
            self.set_line_account_and_dept(line)

        self.write({
            'state': 'accept',
        })

    def action_done(self):
        """
            Change the document status to done state
        """
        self.write({
            'state': 'done',
        })

    # @api.onchange('committe_head')
    # def on_change_com_head(self):
    #     if self.committe_head:
    #         self.committe_members = [self.committe_head.id]
    #     if not self.committe_head:
    #         self.committe_members = False

    # @api.onchange('committee_type_id')
    # def on_change_com_head(self):
    # if self.committee_type_id:
    # self.committe_head = [self.committe_head.id]
    #     if not self.committe_head:
    #         self.committe_members = False
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise ValidationError(_('Sorry! You Cannot Delete not Draft Document .'))
        return super(PurchaseRequisitionCustom, self).unlink()

    @api.onchange('committee_type_id')
    def onchange_committee_type_id(self):
        member_ids = self.committee_type_id.committe_members + self.committee_type_id.committe_head
        head = self.committee_type_id.committe_head
        self.committe_members = [(6, 0, member_ids.ids)]
        self.committe_head = head.id

    @api.constrains('committe_members')
    def check_member_committe_members(self):
        member_ids = self.committee_type_id.committe_members + self.committee_type_id.committe_head
        member_ids = member_ids.mapped('id')
        if self.purchase_commitee and len(self.committe_members) <= 0:
            raise ValidationError(_('Sorry, No Committee members'))

        if self.purchase_commitee and self.committee_type_id and len(self.committe_members) > len(member_ids):
            raise ValidationError(_('Committee members does not match in numbers'))

        if self.purchase_commitee and self.committee_type_id:
            for rec in self.committe_members:
                if rec.id not in member_ids:
                    raise ValidationError(_('This member is not belong to this committee:') + ' {} '.format(rec.name))


class StockPickingCustom(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        # TDE FIXME: clean that brol
        defaults = self.default_get(['name', 'picking_type_id'])
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id',
                                                                                          defaults.get(
                                                                                              'picking_type_id')):
            vals['name'] = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
        # TDE FIXME: what ?
        # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
        # As it is a create the format will be a list of (0, 0, dict)
        if vals.get('name') == 'mosabtest':
            vals['name'] = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
        if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
            for move in vals['move_lines']:
                if len(move) == 3 and move[0] == 0:
                    move[2]['location_id'] = vals['location_id']
                    move[2]['location_dest_id'] = vals['location_dest_id']
        res = super(StockPickingCustom, self).create(vals)
        res._autoconfirm_picking()
        return res


class PurchaseOrderCustom(models.Model):
    _inherit = "purchase.order"

    def copy(self, default=None):
        data = super(PurchaseOrderCustom, self).copy(default)
        data.state = 'draft'
        return data

    state = fields.Selection([
        ('wait', 'Waiting To Be Signed'),
        ('unsign', 'UnSign'),
        ('sign', 'Sign'),
        ('waiting', 'Waiting For Budget Confirmation'),
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('budget_rejected', 'Rejected By Budget'),
        ('wait_for_send', 'Waiting For Send to Budget')])
    department_id = fields.Many2one('hr.department')  # related="requisition_id.department_id"
    purpose = fields.Char()  # related="requisition_id.purpose"
    category_ids = fields.Many2many('product.category', string='Categories')  # , related="requisition_id.category_ids"
    committe_members = fields.One2many('committe.member', inverse_name='po_id')
    no_of_approve = fields.Integer("No. of Votes", compute="_compute_no_approve")
    request_id = fields.Many2one('purchase.request', 'Request Ref.')
    employee_id = fields.Many2one('hr.employee', related="request_id.employee_id")
    # selection_reason = fields.Many2one('evaluation.criteria', "Selection Reason")
    purchase_cost = fields.Selection(
        [('department', 'Department'), ('default', 'Default Cost Center'), ('product_line', 'Product Line'),
         ('project', 'Project')],
        string='Purchase Cost')
    state_of_delivery = fields.Char(string='Delivery State', compute="_compute_delviery_order")
    select = fields.Boolean(string="Select")

    # New Added features on PO (related the cotract features)
    auto_notification = fields.Boolean()
    responsible_id = fields.Many2one('res.users')
    notify_before = fields.Integer()
    start_date = fields.Date()
    end_date = fields.Date()
    cron_end_date = fields.Date(compute="get_cron_end_date",store=True)
    contract_name = fields.Char(srting='Contract Name')
    period_type = fields.Selection(selection=[('day','Day(s)'),('week','Week(s)'),('month','Month(s)'),('year','Year(s)')])

    type = fields.Selection(
        selection=[
            ('ordinary', 'Ordinary'),
            ('contract', 'Contract'),
        ],default='ordinary',string='Type',
    )
    
    def _prepare_invoice(self):
        res = super(PurchaseOrderCustom,self)._prepare_invoice()
        res.update({'purchase_id': self.id})
        return res

    @api.onchange('type')
    def auto_type_change(self):
        if self.type != 'contract':
            self.auto_notification = False
            self.responsible_id = False
            self.notify_before = 0
            self.start_date = None
            self.end_date = None
            self.contract_name = ''
            self.period_type = ''

            return {}

    @api.constrains('end_date','start_date', 'auto_notification')
    def start_notify_constrain(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.start_date >= rec.end_date:
                    raise ValidationError(_("Start Date Should Be Less Than End Date"))

                if rec.auto_notification and rec.notify_before <1:
                    raise ValidationError(_("Notify Before End Should Be Greater Than Zero"))
    
    @api.depends('end_date','notify_before','period_type')
    def get_cron_end_date(self):
        for rec in self:
            if rec.end_date and rec.period_type:
                end = fields.Datetime.from_string(rec.end_date)
                type = self.period_type
                date_to = False
                if rec.period_type == 'day':
                    date_to = (end + relativedelta(days=-rec.notify_before))
                elif rec.period_type == 'month':
                    date_to = (end + relativedelta(months=-rec.notify_before))
                elif rec.period_type == 'week':
                    date_to = (end + relativedelta(weeks=-rec.notify_before))
                elif rec.period_type == 'year':
                    date_to = (end + relativedelta(years=-rec.notify_before))
                rec.cron_end_date = date_to

    @api.model
    def cron_po_auto_notify(self):
        date = fields.Date.today()
        records = self.env['purchase.order'].sudo().search([('state','not in',['cancel','done']),('cron_end_date','<=',str(date)),('auto_notification','=',True)])
        for rec in records:
            template = self.env.ref('purchase_requisition_custom.auto_po_notify')
            template.send_mail(rec.id, force_send=True)

    def open_convert_po_contract(self):
        context = dict(self.env.context or {})
        context['default_purchase_id'] = self.id
        context['purchase_id'] = self.id

        view = self.env.ref('purchase_requisition_custom.convert_to_contract_po_wizard')
        wiz = self.env['convert.po.contract.wizard']
        return {
          'name': _('Purchase To Contract'),
          'type': 'ir.actions.act_window',
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'convert.po.contract.wizard',
          'views': [(view.id, 'form')],
          'view_id': view.id,
          'target': 'new',
          'res_id': wiz.id,
          'context': context,
        }
    # End features on PO (related the cotract features) 

    # New Added
    email_to_vendor = fields.Boolean('Email Sent to Vendor?', default=False)
    send_to_budget = fields.Boolean('Sent to Budget?', default=False)
    # request_id = fields.Many2one('purchase.request', string="Request Source")
    project_id = fields.Many2one('project.project', string='Project',
                                 compute="_get_project_data",
                                 store=True)
    project_stage_id = fields.Many2one('project.phase', string='Project Stage',
                                       compute="_get_project_data",
                                       store=True)
    is_purchase_budget = fields.Boolean(string="Is Purchase Budget", compute='_compute_budget')
    confirmation_ids = fields.One2many('budget.confirmation', 'po_id')

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
            'context': {'create': False}
        }

    # get account_analytic related to department in order line
    @api.onchange('order_line', 'order_line.product_id')
    def on_type_cost_product(self):
        for line in self.order_line:
            if not line.account_analytic_id and line.department_name:
                line.account_analytic_id = line.department_name.analytic_account_id

    def button_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PurchaseOrderCustom, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                               submenu=submenu)
        if (view_type == 'form' or view_type == 'tree') and self.env.user.has_group(
                'purchase_requisition_custom.committe_member') and not (
                self.env.user.has_group('purchase.group_purchase_manager') or self.env.user.has_group(
            'purchase.group_purchase_user')):
            root = etree.fromstring(res['arch'])
            root.set('edit', 'false')
            root.set('create', 'false')
            root.set('duplicate', 'false')
            root.set('delete', 'false')
            res['arch'] = etree.tostring(root)
        else:
            pass

        return res

    def _compute_budget(self):
        purchase_budget = self.env.company.purchase_budget
        for rec in self:
            if purchase_budget:
                rec.is_purchase_budget = True
            else:
                rec.is_purchase_budget = False

    @api.model
    def create(self, vals):
        requisition_id = vals.get('requisition_id', False)
        purchase_cost = vals.get('purchase_cost', False)
        if not purchase_cost:
            vals['purchase_cost'] = 'product_line'

        if requisition_id:
            vals['send_to_budget'] = True
        else:
            if self.env.company.purchase_budget:
                vals['state'] = 'wait_for_send'

        return super(PurchaseOrderCustom, self).create(vals)

    def button_approve(self):
        for rec in self:
            if rec.requisition_id and rec.requisition_id.state != 'approve':
                raise ValidationError(_("Purchase agreement not approved"))
            else:
                # You can Approve
                for line in self.order_line:
                    analytic_account_id = line.account_analytic_id
                    budget_post = self.env['account.budget.post'].search([]).filtered(
                        lambda
                            x: line.product_id.property_account_expense_id.id and line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id in x.account_ids)
                    budget_lines = analytic_account_id.crossovered_budget_line.filtered(
                        lambda x:
                        x.crossovered_budget_id.state == 'done' and
                        fields.Date.from_string(x.date_from) <= fields.Date.from_string(
                            self.date_order) <= fields.Date.from_string(x.date_to))
                    budget_lines.write({'initial_reserve': abs((line.initial_amount) - budget_lines.initial_reserve)})

                super(PurchaseOrderCustom, rec).button_approve()

    @api.constrains('state')
    def _state_on_change(self):
        for obj in self:
            print("State is changed:", obj.state)
            if obj.state == 'sent':
                # print("Email Sent to Vendor!")
                obj.email_to_vendor = True

            # if obj.state in ['draft', 'sent']:
            #     print("Unlock Confirm!!")
            #     obj.send_to_budget = False

            # elif obj.requisition_id and obj.state not in ['draft', 'sent']:
            #     obj.send_to_budget = True

    @api.depends('requisition_id.project_id', 'requisition_id.project_stage_id')
    def _get_project_data(self):
        for rec in self:
            if rec.requisition_id.project_id:
                rec.project_id = rec.requisition_id.project_id.id
            if rec.requisition_id.project_stage_id:
                rec.project_stage_id = rec.requisition_id.project_stage_id.id

    def action_skip_budget(self):
        """ Skip purchase budget"""
        for po_id in self:
            if po_id.state == 'wait_for_send':
                # Deal with double validation process
                valid_amount = self.env.user.company_id.currency_id.compute(
                    po_id.company_id.po_double_validation_amount, po_id.currency_id)
                # second_amount = self.env.user.company_id.currency_id.compute(po_id.company_id.second_approve, po_id.currency_id)
                if po_id.company_id.po_double_validation == 'one_step' \
                        or (po_id.company_id.po_double_validation == 'two_step' \
                            and po_id.amount_total > valid_amount):
                    po_id.write({'state': 'to approve'})
                else:
                    if po_id.email_to_vendor:
                        po_id.write({'state': 'sent'})
                    else:
                        po_id.write({'state': 'draft'})

                    po_id.write({'send_to_budget': False})

    # @api.model
    # def _cumpute_discount_amount_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     tax_discount_policy = self.env['ir.config_parameter'].sudo().get_param(
    #         'odex25_global_discount.tax_discount_policy')
    #     for order in self:
    #         print("KKKKKKKKKKKKKKKKKKKKKK", order.discount_type, order.discount_amount)
    #         applied_discount = line_discount = sums = amount_untaxed = amount_tax = 0.0
    #         for line in order.order_line:
    #             amount_untaxed += line.price_subtotal
    #             amount_tax += line.price_tax
    #             applied_discount += line.discount_amt
    #             if line.discount_method == 'fix':
    #                 line_discount += line.discount_amount
    #             elif line.discount_method == 'per':
    #                 line_discount += (line.price_subtotal+line.price_tax) * (line.discount_amount / 100)
    #         order.is_global_discount = False
    #         if tax_discount_policy:
    #             if tax_discount_policy == 'tax':
    #                 if order.discount_type == 'line':
    #                     order.discount_amt = 0.00
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax - line_discount,
    #                         'discount_amt_line': line_discount,
    #                     })
    #                 elif order.discount_type == 'global':
    #                     order.is_global_discount = True
    #                     print("ggggggggggggggggggggggg", order.discount_type, order.discount_amount)
    #                     order.discount_amt_line = 0.00
    #                     if order.discount_method == 'per':
    #                         order_discount = (amount_untaxed+amount_tax) * (order.discount_amount / 100)
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax - order_discount,
    #                             'discount_amt': order_discount,
    #                         })
    #                     elif order.discount_method == 'fix':
    #                         order_discount = order.discount_amount
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax - order_discount,
    #                             'discount_amt': order_discount,
    #                         })
    #                     else:
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax,
    #                         })
    #                 else:
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax,
    #                     })
    #             elif tax_discount_policy == 'untax':
    #                 if order.discount_type == 'line':
    #                     order.discount_amt = 0.00
    #                     for line in order.order_line:
    #                         if line.discount_method == 'fix' and line.taxes_id.price_include == True:
    #                             price_amount = amount_untaxed - line.discount_amount
    #                             taxes = line.taxes_id.compute_all(price_amount, line.order_id.currency_id, 1,
    #                                                               product=line.product_id, partner=order.partner_id)
    #                             sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                         elif line.discount_method == 'per' and line.taxes_id.price_include == True:
    #                             price_amount = line.price_subtotal - (
    #                                         (line.discount_amount * line.price_subtotal) / 100.0)
    #                             taxes = line.taxes_id.compute_all(price_amount, line.order_id.currency_id, 1,
    #                                                               product=line.product_id, partner=order.partner_id)
    #                             sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                         elif line.discount_method == 'fix' and not line.taxes_id.price_include == True:
    #                             sums = amount_tax
    #                         elif line.discount_method == 'per' and not line.taxes_id.price_include == True:
    #                             sums = amount_tax
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': sums,
    #                         'amount_total': amount_untaxed + sums - applied_discount,
    #                         'discount_amt_line': applied_discount,
    #                     })
    #                 elif order.discount_type == 'global':
    #                     order.discount_amt_line = 0.00
    #                     if order.discount_method == 'per':
    #                         order_discount = amount_untaxed * (order.discount_amount / 100)
    #                         if order.order_line:
    #                             for line in order.order_line:
    #                                 if line.taxes_id:
    #                                     final_discount = 0.0
    #                                     try:
    #                                         final_discount = ((order.discount_amount * line.price_subtotal) / 100.0)
    #                                     except ZeroDivisionError:
    #                                         pass
    #                                     discount = line.price_subtotal - final_discount
    #                                     taxes = line.taxes_id.compute_all(discount, \
    #                                                                       order.currency_id, 1.0,
    #                                                                       product=line.product_id, \
    #                                                                       partner=order.partner_id)
    #                                     sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': sums,
    #                             'amount_total': amount_untaxed + sums - order_discount,
    #                             'discount_amt': order_discount,
    #                         })
    #                     elif order.discount_method == 'fix':
    #                         order_discount = order.discount_amount
    #                         if order.order_line:
    #                             for line in order.order_line:
    #                                 if line.taxes_id:
    #                                     final_discount = 0.0
    #                                     try:
    #                                         final_discount = (
    #                                                     (order.discount_amount * line.price_subtotal) / amount_untaxed)
    #                                     except ZeroDivisionError:
    #                                         pass
    #                                     discount = line.price_subtotal - final_discount
    #                                     taxes = line.taxes_id.compute_all(discount, \
    #                                                                       order.currency_id, 1.0,
    #                                                                       product=line.product_id, \
    #                                                                       partner=order.partner_id)
    #                                     sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': sums,
    #                             'amount_total': amount_untaxed + sums - order_discount,
    #                             'discount_amt': order_discount,
    #                         })
    #                     else:
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax,
    #                         })
    #                 else:
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax,
    #                     })
    #             else:
    #                 order.update({
    #                     'amount_untaxed': amount_untaxed,
    #                     'amount_tax': amount_tax,
    #                     'amount_total': amount_untaxed + amount_tax,
    #                 })
    #         else:
    #             order.update({
    #                 'amount_untaxed': amount_untaxed,
    #                 'amount_tax': amount_tax,
    #                 'amount_total': amount_untaxed + amount_tax,
    #             })

    # @api.depends('order_line', 'order_line.price_total', 'order_line.price_subtotal', \
    #              'order_line.product_qty', 'discount_amount', \
    #              'discount_method', 'discount_type', 'order_line.discount_amount', \
    #              'order_line.discount_method')
    # def _compute_all_global_discount(self):
    #     self._cumpute_discount_amount_all()

    # def _compute_is_global_discount(self):
    #     for rec in self:
    #         rec._cumpute_discount_amount_all()

    # @api.depends('name')
    def _compute_delviery_order(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done'):
                order.state_of_delivery = 'No'
                continue

            if any(
                    not float_is_zero(line.product_qty - line.qty_received, precision_digits=precision)
                    for line in order.order_line.filtered(lambda l: not l.display_type)
            ):
                order.state_of_delivery = 'Partially Received'
            elif (
                    all(
                        float_is_zero(line.product_qty - line.qty_received, precision_digits=precision)
                        for line in order.order_line.filtered(lambda l: not l.display_type)
                    )
                    and order.picking_ids
            ):
                order.state_of_delivery = ' Fully Received '
            else:
                order.state_of_delivery = 'Not Received'

    @api.depends('committe_members')
    def _compute_no_approve(self):
        for rec in self:
            rec.no_of_approve = len(rec.committe_members)

    def action_select_all(self):
        for line in self.order_line:
            line.choosen = True
        self._amount_all()

    @api.constrains('requisition_id', 'partner_id')
    def PreventSameVendor(self):
        """
            Constrain to prevent the same vendor in the order for the same requisition
        """
        orders = self.env['purchase.order'].search([
            ('id', '!=', self.id),
            ('requisition_id', '=', self.requisition_id.id),
            ('requisition_id', '!=', False),
            ('partner_id', '=', self.partner_id.id)
        ])
        if len(orders) != 0:
            raise ValidationError(_("This Vendor have order before"))

    # test

    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }

    '''
        override the method that calculate total amount without taxes to calculate only choosen  line
    '''

    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                if line.choosen:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    # def action_sign(self):
    #     """
    #         Move document to sign state
    #     """

    #     # if not self.selection_reason:
    #     #     raise ValidationError(_("please Add Specify the selection reason"))
    #     if self.requisition_id.purchase_commitee and self.requisition_id.actual_vote < self.requisition_id.min_vote:
    #         raise ValidationError(_("Sorry The minimum number of committee member is not satsfied"))
    #     if self.requisition_id.purchase_commitee and self.no_of_approve < self.requisition_id.min_approve:
    #         raise ValidationError(_("Sorry You cannot sign this quotation ,YOU NEED MORE COMMITTE MEMBERS TO choose it"))

    #     if len(self.order_line.filtered(lambda line: line.choosen == True)) <= 0:
    #         raise ValidationError(_('Choose At Least on product to purchase'))
    #     if self.requisition_id.type_id.exclusive == 'exclusive':
    #         orders = self.env['purchase.order'].search([
    #             ('requisition_id', '=', self.requisition_id.id),
    #             ('id', '!=', self.id)
    #         ])
    #         if len(orders) != 0:
    #             for order in orders:
    #                 order.action_unsign()
    #     for rec in self.order_line:
    #         if rec.price_unit <= 0 and rec.choosen:
    #             raise ValidationError(_("Unit Price can't be Zero Or less"))
    #     if self.amount_total == 0:
    #         raise ValidationError(_("Total Amount Can't be Zero"))
    #     self.write({'state': 'sign'})

    #     self.requisition_id.state = 'checked' if not self.company_id.purchase_budget else 'purchase_manager'
    # ooooooo
    def action_sign(self):
        """
            Move document to sign state
        """
        # if not self.selection_reason:
        #     raise ValidationError(_("please Add Specify the selection reason"))
        if self.requisition_id.purchase_commitee and self.requisition_id.actual_vote < self.requisition_id.min_vote:
            raise ValidationError(_("Sorry The minimum number of committee member is not satsfied"))
        if self.requisition_id.purchase_commitee and self.no_of_approve < self.requisition_id.min_approve:
            raise ValidationError(
                _("Sorry You cannot sign this quotation ,YOU NEED MORE COMMITTE MEMBERS TO choose it"))
        if len(self.order_line.filtered(lambda line: line.choosen == True)) <= 0:
            raise ValidationError(_('Choose At Least on product to purchase'))
        if self.requisition_id.type_id.exclusive == 'exclusive':
            orders = self.env['purchase.order'].search([
                ('requisition_id', '=', self.requisition_id.id),
                ('id', '!=', self.id)
            ])
            if len(orders) != 0:
                for order in orders:
                    order.action_unsign()
        for rec in self.order_line:
            if rec.price_unit <= 0 and rec.choosen:
                raise ValidationError(_("Unit Price can't be Zero Or less"))
        if self.amount_total == 0:
            raise ValidationError(_("Total Amount Can't be Zero"))
        self.write({'state': 'sign'})
        self.requisition_id.state = 'purchase_manager'

    def action_confirm(self):
        """
            Make Purchase requisition done 
        """
        if self.requisition_id.id != False:
            self.requisition_id.state = 'done'
        if self.request_id:
            self.request_id.write({
                'state': 'done'
            })
        self.button_confirm()

    def action_unsign(self):
        """
            Move document to unsign state
        """
        self.write({'state': 'unsign'})

    def action_select(self):
        for member in self.committe_members:
            if member.user_id.id == self.env.user.id and member.select == True:
                raise ValidationError(_('You have already select this Quotation'))
        self.requisition_id.actual_vote += 1
        return {
            'type': 'ir.actions.act_window',
            'name': 'Select Reason',
            'res_model': 'select.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }

    def action_refuse(self):
        for member in self.committe_members:
            if member.user_id.id == self.env.user.id and member.select == True:
                raise ValidationError(_('You have already refused this Quotation'))
            self.requisition_id.actual_vote += 1
        return {
            'type': 'ir.actions.act_window',
            'name': 'Refuse Reason',
            'res_model': 'refuse.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }

    def action_budget(self):
        analytic_account = False
        confirmation_lines = []
        product_line = False
        amount = 0

        # if self.purchase_cost == 'default':
        #     analytic_account = self.env.user.company_id.purchase_analytic_account
        # elif self.purchase_cost == 'department':
        #     analytic_account = self.department_id.analytic_account_id
        #
        # elif self.purchase_cost == 'project':
        #     if not self.project_id.analytic_account_id:
        #         raise ValidationError(_("No analytic account for the project"))
        #     analytic_account = self.project_id.analytic_account_id
        #
        # elif self.purchase_cost == 'product_line':
        #     product_line = True

        for rec in self.order_line:
            if product_line:
                analytic_account = rec.account_analytic_id
                if not analytic_account:
                    raise ValidationError(
                        _("Please put cost center to the product line") + ': {}'.format(rec.product_id.name))

            if not (rec.product_id.property_account_expense_id.id and rec.product_id.property_account_expense_id.id or
                    rec.product_id.categ_id.property_account_expense_categ_id.id):
                raise ValidationError(_("This product has no expense account") + ': {}'.format(rec.product_id.name))

            budget_lines = analytic_account.crossovered_budget_line.filtered(
                lambda x:
                x.crossovered_budget_id.state == 'done' and
                fields.Date.from_string(x.date_from) <= fields.Date.from_string(
                    self.date_order) <= fields.Date.from_string(x.date_to))

            if budget_lines:
                remain = abs(budget_lines[0].remain)
                amount = amount + (rec.price_subtotal + rec.price_tax)
                new_remain = remain - amount
                confirmation_lines.append((0, 0, {
                    'initial_amount': rec.initial_amount,
                    'amount': rec.price_subtotal + rec.price_tax,
                    'analytic_account_id': analytic_account.id,
                    'description': rec.product_id.name,
                    'budget_line_id': budget_lines[0].id,
                    'remain': new_remain + (rec.price_subtotal + rec.price_tax),
                    'new_balance': new_remain + rec.initial_amount,
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
                'date': self.date_order,
                'beneficiary_id': self.partner_id.id,
                'department_id': self.department_id.id,
                'type': 'purchase.order',
                'ref': self.name,
                'description': self.purpose,
                'total_amount': self.amount_untaxed,
                # 'budget_type' : budget_type,
                'lines_ids': confirmation_lines,
                'po_id': self.id
            }
            budget_id = self.env['budget.confirmation'].create(data)
            # Set RFQ to waiting
            self.write({
                'state': 'waiting'
            })
            # Send Notifications
            subject = _('New Purchase Order')
            message = _(
                "New Budget Confirmation Has Been Created for Purchase Order %s to Beneficiary %s in total %s" % (
                    budget_id.name, budget_id.beneficiary_id.name, budget_id.total_amount))
            group = 'purchase.group_purchase_manager'
            author_id = self.env.user.partner_id.id or None
            self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                               group=group)

        else:
            raise ValidationError(_("No confirmation lines"))

    def budget_resend(self):
        self.action_budget()
        self.write({
            'state': 'waiting'
        })

    # edit here wait
    def button_draft(self):
        res = super(PurchaseOrderCustom, self).button_draft()
        self.write({
            'state': 'draft'
        })


# committee type
class CommitteeTypes(models.Model):
    _name = 'purchase.committee.type'

    name = fields.Char('Name')
    committe_members = fields.Many2many('res.users', string='Committee Members')
    committe_head = fields.Many2one('res.users', string='Committee Head')
    type_cat = fields.Many2many('product.category', string='Product Category')


class CommitteMembers(models.Model):
    _name = "committe.member"
    _description = "committe.member"

    po_id = fields.Many2one('purchase.order')
    user_id = fields.Many2one('res.users', "Member Name")
    selection_reason = fields.Char("Selection Reason")
    select = fields.Boolean(string="Select")
    refusing_reason = fields.Char("Refusing Reason")


class SelectReason(models.TransientModel):
    _name = "select.reason"
    _description = "select.reason"

    select_reason = fields.Text("select reason")
    order_id = fields.Integer("order id")

    def action_select(self):
        # member_id = self.env['committe.member'].search(('user_id', '=', user.id))
        # return("this member",member_id)
        self.env['committe.member'].create({
            'po_id': self.order_id,
            'user_id': self.env.user.id,
            'selection_reason': self.select_reason,
            'select': True,

        })
        order_id = self.env['purchase.order'].browse(self.order_id)
        order_id.select = True


class RefuseReason(models.TransientModel):
    _name = "refuse.reason"
    _description = "refuse.reason"

    refuse_reason = fields.Text("refuse reason")
    order_id = fields.Integer("order id")

    def action_refuse(self):
        self.env['committe.member'].create({
            'po_id': self.order_id,
            'user_id': self.env.user.id,
            'refusing_reason': self.refuse_reason,
            'select': True,

        })
        order_id = self.env['purchase.order'].browse(self.order_id)
        order_id.select = True


class ProductCustom(models.Model):
    _inherit = 'product.product'

    def action_notify_new_product(self, product):
        # Send Notifications
        subject = _('New Product') + ' - {}'.format(product.name)
        message = _('New product was added. Product Name:') + ' {} '.format(product.name) + '\n' + _(
            'Sale Price: ') + '{}'.format(product.list_price) + '\n' + _('Description: ') + '{}'.format(
            product.description) + '\n' + _('On Date: ') + '{}'.format(fields.Date.today()) + '\n' + _(
            'Created By: ') + '{}'.format(self.env.user.name)
        group = 'purchase.group_purchase_manager'
        author_id = self.env.user.partner_id.id or None
        self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                           group=group)

    @api.model
    def create(self, vals):
        res = super(ProductCustom, self).create(vals)
        # print("Hi Added Product!", res.name)
        self.action_notify_new_product(res)

        return res


class PurchaseOrderLineCustom(models.Model):
    _inherit = 'purchase.order.line'

    attachment_ids = fields.Many2many('ir.attachment')
    choosen = fields.Boolean(string='Purchase', default=True)
    department_name = fields.Many2one("hr.department", string="Department Name")
    date_end = fields.Date(string="Date End")
    initial_amount = fields.Float(string='Initial amount', digits='Product Price')

    def _create_stock_moves(self, picking):
        '''
            override _create_stock_moves method to create move for only choosen lines
        '''
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        with self.env.norecompute():
            for line in self:
                if line.choosen:
                    for val in line._prepare_stock_moves(picking):
                        done += moves.create(val)
        self.recompute()
        return done


class Attachment(models.Model):
    _inherit = "ir.attachment"

    def unlink(self):
        for record in self:
            if record.res_model == 'purchase.order':
                purchase_order = record.env['purchase.order'].search([
                    ('id', '=', record.res_id)
                ])
                for rec in purchase_order.order_line:
                    if record.id in rec.attachment_ids.ids:
                        rec.write({'attachment_ids': (2, record.id)})
        return super(Attachment, self).unlink()

    def getLine(self, order):
        """
            this function return the line with the least amount of attachment in it
        """
        line = None
        for rec in order.order_line:
            if rec == order.order_line[0]:
                holder = len(rec.attachment_ids.ids)
            if len(rec.attachment_ids.ids) == 0:
                return rec
            elif len(rec.attachment_ids.ids) <= holder:
                line = rec
                holder = len(rec.attachment_ids.ids)
            else:
                continue
        return line


class AccountInvoice(models.Model):
    _inherit = "account.move"

    purchase_id = fields.Many2one('purchase.order', store=True, readonly=False,force_save=True)


    # def get_confirmation(self):
    #     purchase_line_ids = self.invoice_line_ids.mapped('purchase_line_id').mapped('order_id')
    #     requisition_no = purchase_line_ids.mapped('requisition_id').mapped('name')
    #     return self.env['budget.confirmation'].search([('ref', 'in', requisition_no)])

    # def action_invoice_open(self):
    #     res = super(AccountInvoice, self).action_invoice_open()
    #     budget_confirmation = self.get_confirmation()
    #     if budget_confirmation:
    #         budget_confirmation.write({'state': 'invoice_validated'})
    #     return res

    ''' why Did we do this???????'''
    # def action_invoice_cancel(self):
    #     res = super(AccountInvoice, self).action_invoice_cancel()
    #     budget_confirmation = self.get_confirmation()
    #     if budget_confirmation:
    #         budget_confirmation.cancel()
    #     return res

    '''
        get only chosen lines to purchase
    '''

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        vendor_ref = self.purchase_id.partner_ref
        if vendor_ref and (not self.reference or (
                vendor_ref + ", " not in self.reference and not self.reference.endswith(vendor_ref))):
            self.reference = ", ".join([self.reference, vendor_ref]) if self.reference else vendor_ref

        new_lines = self.env['account.move.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            if line.choosen:
                data = self._prepare_invoice_line_from_po_line(line)
                new_line = new_lines.new(data)
                new_line._set_additional_fields(self)
                new_lines += new_line

        self.invoice_line_ids += new_lines
        self.payment_term_id = self.purchase_id.payment_term_id
        self.env.context = dict(self.env.context, from_purchase_order_change=True)
        self.purchase_id = False
        return {}

    def action_post(self):
        res = super(AccountInvoice,self).action_post()
        if self.purchase_id and self.purchase_id.confirmation_ids:
            for r in self.purchase_id.confirmation_ids:
                r.confirm_invoice = True
                for l in r.lines_ids:
                    r.get_confirm_reserve(l.budget_line_id)
        return res
class RejectWizard(models.TransientModel):
    _name = 'reject.wizard'
    _description = 'reject.wizard'

    origin = fields.Integer('')
    reject_reason = fields.Text(string='Reject Reson')
    origin_name = fields.Char('')

    def action_reject(self):
        origin_rec = self.env[self.origin_name].sudo().browse(self.origin)
        if dict(self._fields).get('reject_reason') == None:
            raise ValidationError(_('Sorry This object have no field named Selection Reasoon'))
        else:
            return origin_rec.with_context({'reject_reason': self.reject_reason}).cancel()
