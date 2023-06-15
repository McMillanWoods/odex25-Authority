from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def _get_emp(self):
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp:
            return emp.id
        else:
            raise UserError(_('This user has no related emplyee please assign one'))
    custom_three_validation_steps = fields.Boolean("Special validation steps")
    purchase_track = fields.Selection([('from_custody', 'From petty Cash'), ('from_budget', 'From Budget')],
                                      default='from_budget')
    request_id = fields.Many2one('purchase.request', copy=False)
    
    employee_id = fields.Many2one(
        string='Employee',
        readonly=True ,
        comodel_name='hr.employee',default=_get_emp
        
    )

    send_to_commitee = fields.Boolean(
        string='send_to_commitee',
        # compute='_compute_send_to_commitee'
    )
        
    # @api.depends('state','custom_three_validation_steps','purchase_commitee')
    # def _compute_send_to_commitee(self):
    #     for record in self:
    #         if record.purchase_commitee:
                
    #             if record.state == 'in_progress' and not self.custom_three_validation_steps:
    #                 record.send_to_commitee = True

    #             if record.state == 'general supervisor' and self.custom_three_validation_steps:
    #                 record.send_to_commitee = True







    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'Confirmed'),
        ('committee', 'Committee'),
        ('purchase_manager', 'Purchase manager'),
        ('second_approve', 'Second Approval'),
        # ('legal_counsel', 'Legal Counsel'),
        ('third_approve', 'Third Approval'),
        ('finance approve', 'Financial Approval'),
        ('cs approve', 'Common Services Approval'),
        # ('legal counsel', _('Legal Counsel')),
        ('general supervisor', 'General Supervisor Approval'),
        ('accept', 'Accepted'),
        ('open', 'Bid Selection'),
        ('waiting', 'Waiting For Budget Confirmation'),
        ('checked', 'Waiting Approval'),
        ('done', 'Done'),
        ('quality', 'Quality'),
        ('user_approve', 'User Approve'),
        ('refuse', 'Refused'),
        ('approve', 'Approved'),
        ('cancel', 'cancelled'),
    ],
    )

    purchase_manager_user_id = fields.Many2one(
        string='user',
        comodel_name='res.users',
    )

    @api.multi
    def action_in_progress(self):
        super(PurchaseRequisition, self).action_in_progress()
        self.purchase_manager_user_id = self.env.user.id

    @api.multi
    def action_select_all(self):
        for line in self.line_ids:
            line.chosen = True

    @api.multi
    def action_approve(self):
        if self.custom_three_validation_steps:
            self.write({'state': 'finance approve'})
            return
        if self.purchase_commitee :
            orders = self.env['purchase.order'].search(
            [('requisition_id', '=', self.id), ('state', 'in', ['to approve', 'sign'])])
            for order in orders:
                order.write({
                    'state': 'draft'
                })
            self.write({'state': 'approve'})
            return True
        orders = self.env['purchase.order'].search(
            [('requisition_id', '=', self.id), ('state', 'in', ['to approve', 'sign'])])
        state = 'approve'
        orders_totoal = 0
        for order in orders:
            orders_totoal += order.amount_total
        if self.company_id.po_double_validation == 'one_step' \
                or (self.company_id.po_double_validation == 'two_step'
                    and orders_totoal < self.env.user.company_id.currency_id.compute(
                    self.company_id.po_double_validation_amount, self.purchase_ids[0].currency_id)):
            for order in orders:
                order.write({
                    'state': 'draft'
                })
        else:
            state = 'second_approve'
        
        self.write({
            'state': state
        })

    def button_finance_approve(self):
        for order in self:
            order.write({'state': 'cs approve'})

    # def button_legal_counsel(self):
    #     for order in self:
    #         order.write({'state': 'general supervisor'})

    def button_cs_approve(self):
        for order in self:
            order.write({'state': 'general supervisor'})

    def button_general_supervisor_approve(self):
        for order in self:
            orders = self.env['purchase.order'].search(
                [('requisition_id', '=', order.id), ('state', 'in', ['to approve', 'sign'])])

            for purchase_order in orders:
                purchase_order.write({
                    'state': 'draft'
                })
            order.write({'state': 'approve'})

    def action_view_purchase_request(self):
        action = self.env.ref('purchase_requisition_custom.purchase_request_action')
        result = action.read()[0]
        result['context'] = {}
        res = self.env.ref('purchase_requisition_custom.purchase_request_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.request_id.id
        return result
    
   

    def action_user_approve(self):
        
        # return self.prepare_state_changing_user_list()
        self.action_approve()
    
    def action_quality_approve(self):
        if not self.purchase_commitee:
            self.state = 'user_approve'
        else :
            self.to_committee()
    def check_choose_one_line_in_pr(self):
        if len(self.line_ids.filtered(lambda pr_line: pr_line.chosen is True)) <= 0:
            raise ValidationError(_('Choose At Least one product to purchase in purchase agreement'))
    

    @api.multi
    def action_check_budget(self):
        for line in self.line_ids:
            line._compute_budget_info_y()
        
        

        # if (self.purchase_cost and self.purchase_cost == 'department') or not self.purchase_cost:
        #      for line in self.line_ids:
        #        if not line.account_analytic_id and line.chosen:
        #            raise ValidationError(_('Please define department and analytic account '
        #                                     'in purchase requisition lines!'))
        #        analytic_account_lines = self.line_ids.filtered(lambda pr_line:
        #                                                        pr_line.account_analytic_id == line.account_analytic_id
        #                                                         and pr_line.chosen)
        #        analytic_lines_summation = sum(analytic_account_lines.mapped('amount'))
        #        line._compute_budget_info_y()
        #        if analytic_lines_summation > line.remaining_analytic_budget:
        #            raise ValidationError(_('Please make sure analytic accounts '
        #                                     'have sufficient budget '
        #                                     'in purchase requisition lines!'))
        for purchase in self.purchase_ids:
            if purchase.state == 'sign':
                for line in purchase.order_line:
                    line.choosen = line.requisition_line_id.chosen if line.requisition_line_id else False
                    if line.choosen:
                        line.account_analytic_id = line.requisition_line_id.account_analytic_id \
                            if line.requisition_line_id.account_analytic_id.id else False
       
        # self.state = 'user_approve'
        # if not self.purchase_commitee :
        self.state = 'quality'
        # else :
            # self.to_committee()
        
    
    def send_to_purhcse_mangager(self):
        self.check_choose_one_line_in_pr()
        purchase_orders = self.purchase_ids.filtered(lambda line: line.recomandation_order == True)
        if not purchase_orders:
            raise ValidationError(_('Please recommend one purchase offer At Least'))
        order_lines = purchase_orders.mapped('order_line')
        if len(order_lines.filtered(lambda line: line.choosen == True)) <= 0:
            raise ValidationError(_('Choose At Least on product in recommend purchase offer  to purchase'))
        self.state='purchase_manager'       
        for line in self.line_ids:
            line._compute_budget_info_y()
    @api.multi
    def refuse_requision(self,reason):
        self.write({'state': 'refuse'})
        self.message_post(_("Refuse Reason is : %s")%reason)
        
    @api.multi
    def action_purchase_requisition_view(self):
        is_singed = False
        for rec in self.purchase_ids:
            if rec.state in ('sign','draft','purchase'):
                is_singed  = True
                break
        if is_singed:
            form_view_ref = self.env.ref('purchase_custom_vro.requistion_purchase_order_form', False)
            tree_view_ref = self.env.ref('purchase_custom_vro.requistion_purchase_order_tree', False)
            return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'domain':[('requisition_id','=',self.id)],
            'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
        }
        else:
           
            action = self.env.ref('purchase_requisition.action_purchase_requisition_list', False)
            result = action.read()[0]
            result['domain'] = [('requisition_id','=',self.id)]
            return result
        
        
    # def action_purchase_requisition_select(self):
    #     action = self.env.ref('purchase_requisition.action_purchase_requisition_list', False)
    #     result = action.read()[0]
        
    #     result['domain'] = [('recomandation_order','=',True),('requisition_id','=',self._context.get('params').get('id'))]
    #     return result

    selected_order_count = fields.Integer(compute='_selected_order_count', string='Number of Orders')

    @api.multi
    @api.depends('purchase_ids')
    def _selected_order_count(self):
        for requisition in self:
            requisition.selected_order_count = len(requisition.purchase_ids.filtered(lambda m:m.recomandation_order))

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    remaining_analytic_budget = fields.Float("Cost Center Remain Balance",
                                             compute="_compute_budget_info_y",)
    requisition_purchase_ids = fields.One2many(related="requisition_id.purchase_ids")
    price_unit = fields.Float("Price Unit", compute="_compute_budget_info_y", 
                              help="Unit price copied from the selected quotation.")
    department_id = fields.Many2one("hr.department")
    account_analytic_id = fields.Many2one("account.analytic.account", related="department_id.analytic_account_id",
                                          readonly=False,store=True)
    chosen = fields.Boolean(string='Purchase', default=False)
    amount = fields.Float("Amount", compute="_compute_budget_info_y",store=True)
    budget_line_id = fields.Many2one('crossovered.budget.lines', compute="_compute_budget_info_y", store=True)
    price_tax = fields.Float(compute='_compute_budget_info_y', string='Tax', )
    price_total = fields.Float(compute='_compute_budget_info_y', string='Total', )

    # @api.depends('department_id', 'requisition_id.purchase_cost',
    #              'requisition_id.purchase_ids', 'requisition_id.purchase_ids.state')
    def _compute_budget_info_y(self):
        for rl in self:
            rl.remaining_analytic_budget = 0
            rl.price_unit = 0
            rl.amount = 0
            analytic_account = False
            if rl.requisition_id.purchase_cost == 'default':
                analytic_account = rl.env.user.company_id.purchase_analytic_account
            elif rl.department_id and rl.department_id.analytic_account_id:
                analytic_account = rl.department_id.analytic_account_id
            if not rl.requisition_id.purchase_commitee :
                purchase = rl.requisition_id.purchase_ids.filtered(lambda po: po.state in ['sign', 'purchase', 'draft'])
            else :
                purchase = rl.requisition_id.purchase_ids.filtered(lambda po: po.state in ['sign', 'purchase', 'draft','unsign'] and po.recomandation_order==True)
            for order in purchase:
                rec = order.order_line.filtered(lambda order_line: order_line.requisition_line_id==rl)
                if rec:
                    if analytic_account:
                        date_ordering = fields.Date.from_string(rl.requisition_id.ordering_date)
                        if (rec.product_id.property_account_expense_id.id or
                                rec.product_id.categ_id.property_account_expense_categ_id.id):
                            account_id = rec.product_id.property_account_expense_id or \
                                         rec.product_id.categ_id.property_account_expense_categ_id
                            budget_post = self.env['account.budget.post'].search([]).filtered(
                                lambda x: account_id in x.account_ids)
                            budget_lines = analytic_account.crossovered_budget_line.filtered(
                                lambda x: x.general_budget_id in budget_post and
                                          x.crossovered_budget_id.state == 'done' and
                                          fields.Date.from_string(x.date_from) <= date_ordering <=
                                          fields.Date.from_string(x.date_to))
                            if budget_lines and rl.requisition_id.state not in ['draft','in_progress']:
                                remain = budget_lines[0].remain
                                rl.remaining_analytic_budget = remain
                                rl.budget_line_id = budget_lines[0].id
                    # rl.price_unit = rec.price_unit
                    # rl.amount = rec.price_unit * rl.product_qty
                    taxes = rec.taxes_id.compute_all(rec.price_unit, rec.order_id.currency_id, rec.product_qty, product=rec.product_id, partner=rec.order_id.partner_id)
                    # rl.write({
                    #     'amount' :rec.price_unit * rl.product_qty,
                    #     'price_unit':rec.price_unit,
                        
                    # })
                    
                    rl.amount = rec.price_unit * rl.product_qty
                    rl.price_unit = rec.price_unit
                    rl.price_tax=sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                    rl.price_total =  taxes['total_included']
        
                

    @api.multi
    def unlink(self):

       

        if self.requisition_id.state !='draft':
            raise UserError(_('Products cannot be deleted after the draft state.'))
        return super(PurchaseRequisitionLine, self).unlink()
