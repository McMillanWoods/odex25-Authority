# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
from dateutil import relativedelta
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.osv import expression
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class Project(models.Model):
    _inherit = "project.project"

    project_no = fields.Char("Project Number",default='/',tracking=True)
    code = fields.Char("Project Code",tracking=True)
    short_name = fields.Char("Project Short Name",tracking=True)
    department_id = fields.Many2one('hr.department',string="Department",tracking=True)
    project_id = fields.Many2one('project.project',string='Parent Project',tracking=True)
    sub_project_id = fields.One2many('project.project','project_id',string='Sub-Project',tracking=True)
    related_project_id = fields.Many2one('project.project',string='Related Project',tracking=True)
    related_project_user_id = fields.Many2one('res.users', related="related_project_id.user_id",string='Related Project Manager',tracking=True)
    customer_project_no = fields.Char(string='Customer Project No',tracking=True)
    coordinator_user_id = fields.Many2one('res.users', string='Project Coordinator',tracking=True)
    account_user_id = fields.Many2one('res.users', string='Account Manager',tracking=True)
    category_id = fields.Many2one('project.category', string='Project Category',tracking=True)
    classification_id = fields.Many2one('res.partner.industry', string='Project Classification',tracking=True)
    sub_classification_id = fields.Many2one('res.partner.industry', string='Sub-classification',domain="[('parent_id','=',classification_id)]",tracking=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',tracking=True)
    state_id = fields.Many2one("res.country.state", string='Region', ondelete='restrict', domain="[('country_id', '=', country_id)]",tracking=True)
    city = fields.Many2one('res.country.city',string="City",domain="[('country_id', '=', country_id),('state_id', '=', state_id)]",tracking=True)
    box_no = fields.Char(string="B.O Box",tracking=True)
    site_area = fields.Float(string="Site area(m2)",tracking=True)
    bua = fields.Float(string="BUA (m2)",tracking=True)
    project_component_ids = fields.One2many('project.component','project_id',string="Components Buildings")
    contract_number = fields.Char(string="Contract Number",tracking=True)
    contract_type_id =  fields.Many2one('product.product',string="Contract type",tracking=True)
    signature_date = fields.Date(string="Signature Date",tracking=True)
    launch_date = fields.Datetime("launch date",tracking=True)
    contract_value = fields.Float("Contract Value",tracking=True)
    duration_days = fields.Integer("Duration Days",compute="_compute_duration")
    duration_months = fields.Integer("Duration Months",compute="_compute_duration")
    estimated_hours = fields.Float("Estimated Hours")
    project_phase_ids = fields.One2many('project.phase','project_id',string="Project Phases")
    folder_id = fields.Many2one('dms.directory',
                                       string="Floder Workspace",
                                       ondelete="cascade",
                                       help="A workspace Folder to store all project documents.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('open', 'Open'),
        ('suspended','Suspended'),
        ('pending', 'Pending'),
        ('done','Done')], string='Status',
        copy=False, default='draft', required=True,tracking=True)
    project_type = fields.Selection([
        ('supervision', 'Supervision'),
        ('design', 'Design')
    ], string="Project type", default="design")
    invoice_employee_ids = fields.One2many('project.invoice.line.employee', 'project_id', "Invoice By Employees", copy=False,
        help="The Details of invoice By Employees")
    invoice_ids = fields.One2many('project.invoice.line', 'project_id', "Invoice", copy=False,
        help="The Details of invoice")


    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_confirm(self):
        for record in self:
            sum_bua = sum(record.project_component_ids.mapped('bua'))
            if sum_bua != record.bua:
                raise ValidationError(_("The total BUA(m2) must equal to the sum bua in project component."))
        return self.write({'state': 'confirmed'})

    def action_open(self):
        return self.write({'state': 'open'})

    def action_suspended(self):
        return self.write({'state': 'suspended'})

    def action_pending(self):
        return self.write({'state': 'pending'})

    def action_done(self):
        return self.write({'state': 'done'})

    def action_view_subproject(self):
        self.ensure_one()
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "name": "Sub-Projects",
            "views": [[False, "tree"]],
            "context": {"create": False},
            "domain": [('project_id','=',self.id)]
        }
        return action_window

    @api.depends('date_start', 'date')
    def _compute_duration(self):
        for record in self:
            if record.date_start and record.date:
                record.duration_days = record._get_number_of_days(record.date_start, record.date)['days']
                record.duration_months = record._get_number_of_days(record.date_start, record.date)['month']
            else:
                record.duration_days = 0
                record.duration_months = 0

    def _get_number_of_days(self, date_from, date_to):
        """ Returns a float equals to the timedelta between two dates given as string."""
        df = datetime.combine(date_from, datetime.min.time())
        dt = datetime.combine(date_to, datetime.min.time())
        today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
            datetime.combine(df.date(), time.min),
            datetime.combine(df.date(), time.max),
            False)
        hours = self.env.company.resource_calendar_id.get_work_hours_count(df, dt)
        days = hours / (today_hours or HOURS_PER_DAY)
        delta = relativedelta.relativedelta(date_to,date_from)
        month = delta.months
        return {'days': days, 'month': month}

    def name_get(self):
        res = []
        for record in self:
            if record.project_no:
                res.append((record.id,("["+record.project_no+"] "+record.name)))
            else:
                res.append((record.id,record.name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []

        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            connector = '&' if operator in expression.NEGATIVE_TERM_OPERATORS else '|'
            domain = [connector, ('project_no', operator, name), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def create(self, vals):
        if not vals.get('project_id', False):
            vals['project_no'] = self.env['ir.sequence'].next_by_code('project.project') or '/'
        else:
            last_rec = self.search([('project_id','=',vals['project_id'])],order='id desc',limit=1)
            if not last_rec:
                last_rec = self.browse(vals['project_id'])
            no_list = last_rec.project_no.split('-')
            string = str((int(no_list[1]) + 1)) 
            string = string.zfill(5)
            vals['project_no'] = no_list[0] +'-'+ string
        # if vals.get('deparment_id', False):
        #     deparment = self.env['hr.deparment'].browse(vals['deparment_id'])
        #     #TODO: find analytic account in department
        #     #if not deparment.analytic_account_id:
        #     #    raise Warning(_('''The Department has no analytic account,contact your system admin to create analytic account.'''))
        return super().create(vals)

class ProjectCategory(models.Model):
    _name = "project.category"

    name = fields.Char(string="Name")

class ProjectComponent(models.Model):
    _name = "project.component"
    _description = "Project Components Buildings"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    bua = fields.Float(string="BUA (m2)")
    project_id = fields.Many2one('project.project',string="Project")

class ProjectInvoiceLineEmployee(models.Model):
    _name = "project.invoice.line.employee"
    _description = "Project Invoice"

    job_id = fields.Many2one('hr.job',string="Job")
    number = fields.Integer(string="Number")
    sale_rate = fields.Float(string="Hour Sale Rate")
    total = fields.Float(string="Total",compute="_total_compute")
    project_id = fields.Many2one('project.project',string="Project")

    @api.depends('sale_rate', 'number')
    def _total_compute(self):
        for record in self:
            if record.sale_rate and record.number:
                record.total = record.sale_rate * record.number
            else:
                record.total = 0

class ProjectInvoiceLine(models.Model):
    _name = "project.invoice.line"
    _description = "Project Invoice"

    phase_id = fields.Many2one('project.phase',string="Phase")
    amount = fields.Float(string="Amount")
    project_id = fields.Many2one('project.project',string="Project")
