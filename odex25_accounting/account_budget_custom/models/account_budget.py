from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError, ValidationError


class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"
    _order = "create_date desc"

    reserved_percent = fields.Float(
        string='Reserved Percent'
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        readonly=True, required=True,
        default=lambda self: self.env.user.company_id.currency_id.id
    )

class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    """
    service_id = fields.Many2one('product.product', 'Service')
    service_budget_distrib_id = fields.Many2one(
        'service.budget.distrib', 'Service Budget')
    """
    reserved_percent = fields.Float(
        related='crossovered_budget_id.reserved_percent',
        string='Reserved Percent'
    )
    reserved_amount = fields.Float(
        string='Reserved Amount', readonly=True,
        compute='_compute_reserved_amount'
    )
    pull_out = fields.Float(
        string='Pull Out',
        compute='_compute_operations_amount', store=True, tracking=True
    )
    provide = fields.Float(
        string='Provide',
        compute='_compute_operations_amount', store=True, tracking=True
    )
    remain = fields.Float(
        string='Remain',
        compute='_compute_operations_amount', tracking=True
    )
    budget_confirm_amount = fields.Float(
        string='Confirmation Amount',
        compute='_compute_operations_amount'
    )
    purchase_remain = fields.Float(
        compute='_compute_operations_amount', tracking=True
    )
    practical_amount = fields.Float(
        compute='_compute_practical_amount',
        string='Practical Amount', digits=0,
        store=False, tracking=True
    )
    theoritical_amount = fields.Float(
        compute='_compute_theoritical_amount',
        string='Theoretical Amount', digits=0, store=True
    )
    percentage = fields.Float(
        compute='_compute_percentage',
        string='Achievement', store=False, digits=(16, 4)
    )
    from_operation_ids = fields.One2many('budget.operations', 'from_budget_line_id', string='From Operation')
    to_operation_ids = fields.One2many('budget.operations', 'to_budget_line_id', string='Cost Center')

    # Added new
    reserve = fields.Float(string='Reserve Amount', tracking=True)
    initial_reserve = fields.Float(string='Initial Reserve Amount', tracking=True)
    confirm = fields.Float(string='Confirm Amount')
    year_end = fields.Boolean(compute="get_year_end")

    def get_year_end(self):
        for rec in self:
            date = fields.Date.today()
            if rec.crossovered_budget_id.date_to <= date:
                rec.year_end = True
            else:
                rec.year_end = False


    def transfer_budget_action(self):
        formview_ref = self.env.ref('account_budget_custom.view_budget_operations', False)
        return {
            'name': ("Budget Transfer"),
            'view_mode': ' form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'budget.operations',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'views': [(formview_ref and formview_ref.id or False, 'form')],
            'context': {
                'default_operation_type': 'transfer',
                'default_from_budget_post_id': self.general_budget_id.id,
                'default_from_crossovered_budget_id': self.crossovered_budget_id.id,
                'default_from_budget_line_id': self.id,
                'default_amount': self.remain,
                'default_date': fields.Date.today(),
            }
        }
    @api.depends('from_operation_ids', 'to_operation_ids')
    def _compute_operations_amount(self):
        self.purchase_remain =0.0
        if not self.ids: return
        for line in self:
            pull_out = provide = budget_confirm_amount = 0.0
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get(
                'wizard_date_from') or line.date_from

            if line.analytic_account_id.id:
                if 'reserved' not in self.env.context:
                    self.env.cr.execute("""
                           SELECT SUM(amount)
                           FROM budget_operations
                           WHERE from_budget_line_id=%s
                               AND (date between %s AND %s)
                               AND state='confirmed'""",
                                        (line.id, date_from, date_to,))
                    pull_out = self.env.cr.fetchone()[0] or 0.0

                if 'reserved' in self.env.context:
                    self.env.cr.execute("""
                           SELECT SUM(amount)
                           FROM budget_operations
                           WHERE from_budget_line_id=%s
                               AND (date between %s AND %s)
                               AND state='confirmed' 
                               AND from_reserved=%s""",
                                        (line.id, date_from, date_to, self.env.context['reserved']))
                    pull_out = self.env.cr.fetchone()[0] or 0.0

                self.env.cr.execute("""
                       SELECT SUM(amount)
                       FROM budget_operations
                       WHERE to_budget_line_id=%s
                           AND (date between %s AND %s)
                           AND state='confirmed'""",
                                    (line.id, date_from, date_to,))
                provide = self.env.cr.fetchone()[0] or 0.0

                self.env.cr.execute("""
                       SELECT SUM(amount)
                       FROM budget_confirmation_line
                       WHERE budget_line_id=%s
                           AND (date between %s AND %s)
                           AND state='done'""",
                                    (line.id, date_from, date_to,))
                budget_confirm_amount = self.env.cr.fetchone()[0] or 0.0

            line.pull_out = pull_out
            line.provide = provide
            line.budget_confirm_amount = budget_confirm_amount


            line.remain = line.planned_amount - line.practical_amount + line.reserve +line.initial_reserve + provide - pull_out
            line.purchase_remain = abs(line.reserve + line.initial_reserve + line.practical_amount)-abs( line.practical_amount)


    # @api.depends('service_id', 'analytic_account_id', 'planned_amount', 'practical_amount')
    @api.depends('analytic_account_id', 'planned_amount', 'practical_amount')
    def name_get(self):
        result = []

        for line in self:
            name = ''
            # if line.service_id:
            #    name += line.service_id.name + ' ' + _('in') + ' '
            name += line.analytic_account_id and line.analytic_account_id.name or '' + ' ' + _('remaining') + ' '

            # check if reserved is needed
            if self.env.context.get('reserved', False):
                name += str(line.reserved_amount)

            if not self.env.context.get('reserved', False):
                name += str(line.remain)

            result.append((line.id, name))
        return result

    # @api.depends('crossovered_budget_id.reserved_percent')
    def _compute_reserved_amount(self):
        for line in self:
            reserved_amount = line.crossovered_budget_id.reserved_percent * \
                              line.planned_amount / 100.0
            if reserved_amount:
                reserved_amount -= line.with_context({'reserved': True}).pull_out
            line.reserved_amount = reserved_amount


    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get(
                'wizard_date_from') or line.date_from
            if line.analytic_account_id.id:
                analytic_ids = self.env['account.analytic.account'].search(
                    ['|', ('id', '=', line.analytic_account_id.id),
                     ('parent_id', 'child_of', line.analytic_account_id.id)])
                self.env.cr.execute(
                    """
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id IN %s
                        AND (date between %s AND %s)
                        AND general_account_id=ANY(%s)""",
                    (tuple(analytic_ids.ids), date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            # child_result = 0
            # for rec in line.analytic_account_id.child_ids:
            #     child_result += sum(rec.crossovered_budget_line.filtered(
            #         lambda row: row.general_budget_id.id == line.general_budget_id.id).mapped('practical_amount'))
            # result += child_result
            # result = abs(result)
            line.practical_amount = result

    def _check_amount(self,amount=0,transfer=False):
        for obj in self:
            # get the original reserved amount
            reserved_amount = obj.crossovered_budget_id.reserved_percent * \
                              obj.planned_amount / 100.0

            if obj.with_context({'reserved': True}).pull_out > reserved_amount:
                raise ValidationError(
                    _('''You can not take more than the reserved amount.'''))
            if obj.planned_amount < 0:
                if obj.remain != amount and transfer:
                    raise ValidationError(
                        _('''You can not take more than the remaining amount..'''))
            else:
                if obj.remain < amount:
                    raise ValidationError(
                        _('''You can not take more than the remaining amount'''))