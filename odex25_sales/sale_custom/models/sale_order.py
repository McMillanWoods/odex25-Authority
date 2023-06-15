# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bidbond = fields.Boolean('Bid Bond')
    proposal_name = fields.Char('Name')
    project_country_id = fields.Many2one('res.country', 'Country')
    project_state_id = fields.Many2one('res.country.state', string='Region')
    city_id = fields.Many2one('res.country.city', 'City')
    industry_id = fields.Many2one('res.partner.industry', 'Industry(Classification)')
    sector_id = fields.Many2one('sector', 'Sector(Role)')
    department_id = fields.Many2one('hr.department',string='Business Unit')
    product_id = fields.Many2one('product.product',string='Services(Contract Type)')

    project_category_id = fields.Many2one('project.category', 'Project Category')
    project_manager_id = fields.Many2one('res.users', string='Project Manager',tracking=True)
    project_coordinator_id = fields.Many2one('res.users', string='Project Coordinator',tracking=True)

    project_duration = fields.Integer('Project Duration (Months) As per (SOW)')
    project_duration_internal = fields.Integer('Project Duration (Internal)')
    total_site_area = fields.Float('Total Site Area (m2) (Excluding Building Footprint)')
    main_building_prototype = fields.Float('Main Building Prototype Area (m2)')
    main_building_site = fields.Float('Main Building Site Adaptation Area (m2)')
    main_building_total = fields.Float('Main Building Total Area (m2)')
    floor_area_ratio = fields.Float('Floor Area Ratio (FAR)')
    site_works_area = fields.Float('Site Works Area (m2)')
    ancillary_building_prototype = fields.Float('Ancillary Building Prototype Area (m2)')
    ancillary_building_site = fields.Float('Ancillary Building Site Adaptation Area (m2)')
    ancillary_building_total = fields.Float('Ancillary Buildings Total Area (m2)')

    sale_department_ids = fields.One2many('sale.department', 'sale_order_id', string='Mhrs Estimate')
    sale_job_ids = fields.One2many('sale.job', 'sale_order_id', string='Manpower')

    contract_attachment_ids = fields.Many2many('ir.attachment', relation="contract_proposal_attach_rel",
                                                column1="attachment_id", column2="contract_proposal_id",
                                                string="Contract")

    proposal_attachment_ids = fields.Many2many('ir.attachment', string='Proposal Document')

    proposal_state_id = fields.Many2one('proposal.state', string="Proposal Status")
    upload_contract = fields.Boolean(related='proposal_state_id.upload_contract', store=True)
    contract_value = fields.Float('Contract Value')

    bid_bond_ids = fields.One2many('bid.bond', 'sale_order_id', string='Bid Bond')
    contract_status = fields.Selection([('draft', 'Proposal'),
                                        ('sent', 'Conrtact Sent'),
                                        ('confirm', 'Confirmed'),
                                        ('done', 'Approved'),
                                        ('cancel', 'Cancelled')], string='Contract Status', readonly=True, copy=False, index=True, tracking=True, default='draft')


    state = fields.Selection([
        ('draft', 'Proposal'),
        ('sent', 'Proposal Sent'),
        ('sale', 'Confirmed'),
        ('done', 'Approved'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    rank = fields.Integer('Rank')
    bid_opening_ids = fields.One2many('bid.opening', 'sale_order_id', string='Bid Opeing')



    def action_proposal_sent(self):

        self.state = 'sent'


    def action_confirm(self):

        self.state = 'sale'



    def action_proposal_approve(self):

        self.state = 'done'


    def action_contract_send(self):
        if not self.contract_attachment_ids:
            raise ValidationError(_('Please upload contract firstly'))
        
        self.contract_status = 'sent'


    def action_contract_confirm(self):
        
        self.contract_status = 'confirm'


    def action_contract_approve(self):

        self.contract_status = 'done'


    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        super(SaleOrder, self).onchange_sale_order_template_id()
        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

        department_lines = [(5, 0, 0)]
        for line in template.sale_department_template_line_ids:
            data = self._compute_dept_job_data_for_template_change(line)

            if line.department_id:
                data.update({
                    'department_id': line.department_id.id,
                    'no_sheet': line.no_sheet,
                    'hrs_sheet': line.hrs_sheet,
                    'cairo_hrs': line.cairo_hrs,
                    'ksa_hrs': line.ksa_hrs,
                })

            department_lines.append((0, 0, data))


        self.sale_department_ids = department_lines


        job_lines = [(5, 0, 0)]
        for line in template.sale_job_template_line_ids:
            job_data = self._compute_dept_job_data_for_template_change(line)

            if line.job_id:
                job_data.update({
                    'job_id': line.job_id.id,
                    'no_year_experience': line.no_year_experience,
                    'qty': line.qty,
                    'duration': line.duration,
                    'month_rate': line.month_rate,
                })

            job_lines.append((0, 0, job_data))


        self.sale_job_ids = job_lines


    def _compute_dept_job_data_for_template_change(self, line):
        return {
            'display_type': line.display_type,
            'name': line.name,
        }



    def _compute_project_ids(self):
        for order in self:

            project_ids = self.env['project.project'].search([('sale_order_id', '=', order.id)])

            order.project_ids = project_ids


    def create_project(self):

        project_obj = self.env['project.project']

        manpower = [(0, 0, {'job_id': man.job_id.id, 'number': man.qty, 'sale_rate': man.month_rate}) for man in self.sale_job_ids]

        project_id = project_obj.create({'name': self.opportunity_id.name, 'partner_id': self.partner_id.id, 'sale_order_id': self.id,
                                         'user_id': self.project_manager_id.id, 'coordinator_user_id': self.project_coordinator_id.id,
                                         'department_id':self.department_id.id, 'category_id': self.project_category_id.id,
                                         'country_id': self.project_country_id.id, 'state_id': self.project_state_id.id, 'city':self.city_id.id,
                                         'site_area': self.total_site_area, 'description': self.note, 'contract_type_id': self.product_id.id,
                                         'classification_id': self.industry_id.id, 'date_start': self.date_order, 'date': self.validity_date,
                                         'estimated_hours': sum(self.mapped('sale_department_ids').mapped('total_hrs')),
                                         'contract_value': self.contract_value, 'invoice_employee_ids':manpower})


        # self.project_ids = project_id
