# -*- coding: utf-8 -*-
import datetime
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError


class JobTitle(models.Model):
    _name = 'cm.job.title'
    _description = 'Job Titles'

    name = fields.Char(string='Job Title')


class Entity(models.Model):
    _name = 'cm.entity'
    _description = 'Transactions Contacts'
    _order = 'name'

    @api.model
    def _name_search(self, name, args=None, operator='like', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
            print(domain)
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    @api.constrains('code')
    def _check_code(self):
        count = self.search_count([('code', '=', self.code), ('id', '!=', self.id)])
        if self.code:
            if count:
                raise ValidationError(_("Validation Error Entity Code Must Be unique !"))
            if self.type == 'unit':
                x = ''
                if len(self.code) == 3 or len(self.code) == 2:
                    x = 'a'
                if self.code.isalpha() == False or x == '':
                    raise ValidationError(_("Validation Error Entity Code Must Be Composed from 3/2 characters"))

    code = fields.Char(string='Code')
    # sequence = fields.Integer(string='Sequence')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', readonly=False, ondelete='cascade',
                                 copy=False)
    name = fields.Char(string='Name', related='partner_id.name', store=True)
    type = fields.Selection(string='Entity Type', selection=[('unit', _('Internal Unit')), ('employee', _('Employee')),
                                                             ('external', _('External Unit'))], default='unit')
    parent_id = fields.Many2one(comodel_name='cm.entity', string='Parent Entity')
    department_id = fields.Many2one('hr.department')
    manager_id = fields.Many2one(comodel_name='cm.entity', string='Unit Manager')
    secretary_id = fields.Many2one(comodel_name='cm.entity', string='Employee in charge of transactions')
    user_id = fields.Many2one(comodel_name='res.users', string='Related User', related='employee_id.user_id')
    # job_title_id = fields.Many2one(comodel_name='cm.job.title', string='Job Title')
    job_title_id = fields.Many2one(comodel_name='hr.job', string='Job Title')
    need_approve = fields.Boolean(string='Need Aprove')
    executive_direction = fields.Boolean(string='Executive direction')
    is_secret = fields.Boolean(string='Is Secret')
    person_id = fields.Char(string='Person ID')
    person_id_issue_date = fields.Date(string='Person ID Issue Date')
    employee_assignment_date = fields.Date(string='Employee Assignment Date')
    employee_id = fields.Many2one('hr.employee')
    phone = fields.Char()
    email = fields.Char()
    child_ids = fields.Many2many(comodel_name='cm.entity', relation='employee_entity_rel', column1='employee_id',
                                 column2='entity_id', string='Related Units')
    establish_date = fields.Date(string='Establish Date')
    unit_location = fields.Char(string='Unit Location')
    sketch_attachment_id = fields.Many2one(comodel_name='ir.attachment', string='Sketch Attachment')
    dynamic_year = fields.Char(string='Year', default=datetime.datetime.now().strftime('%Y'))
    year_increment = fields.Boolean(string='Continue Increment every year?', help='''
                Check if you want to continue incrementing in the start of every new year.
            ''', default=True)

    @api.onchange('department_id')
    def onchange_department_id(self):
        self.name = self.department_id.name

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.job_title_id = self.employee_id.job_id

    @api.onchange('partner_id', 'employee_id')
    def onchange_partner_id(self):
        self.email = self.partner_id.email
        self.phone = self.partner_id.phone

    ####################################################
    # ORM Overrides methods
    ####################################################
    @api.model
    def create(self, vals):
        if vals.get('type', False) == 'employee':
            vals['partner_id'] = self.env['hr.employee'].search(
                [('id', '=', vals['employee_id'])]).user_id.partner_id.id
        if 'partner_id' not in vals:
            print("*******************")
            if vals.get('type', False) == 'employee':
                user_id = vals.get('user_id', False)
                if user_id:
                    vals['partner_id'] = self.env['res.users'].search([('id', '=', user_id)]).partner_id.id
            else:
                partner = self.env['res.partner'].create({
                    'name': vals.get('name', ''),
                    'email': vals.get('email', ''),
                    'city': vals.get('city', _('Riyadh')),
                    'is_company': vals.get('is_company', True),
                    'country_id': self.env.ref('base.sa', True).id,
                })
                vals['partner_id'] = partner.id
        sequence = {
            'employee': '01',
            'unit': '02',
            'external': '03',
        }
        if not vals.get('code', False):
            seq = self.env['ir.sequence'].get('cm.entity')
            s = u'{}-{}'.format(sequence[vals.get('type', 'employee')], seq)

            if vals.get('type') == 'employee' or vals.get('type') == 'external':
                vals['code'] = s
        return super(Entity, self).create(vals)

    def write(self, vals):
        sequence = {
            'employee': '01',
            'unit': '02',
            'external': '03',
        }
        if not vals.get('code', False):
            seq = self.env['ir.sequence'].get('cm.entity')
            s = u'{}-{}'.format(sequence[vals.get('type', 'employee')], seq)
            if vals.get('type') == 'employee' or vals.get('type') == 'external':
                vals['code'] = s
        return super(Entity, self).write(vals)

    def copy(self, default=None):
        raise UserError(_('You cannot duplicate an entity!'))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_transaction_entity = fields.Boolean('Is Transaction Entity?')

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        if values.get('is_transaction_entity'):
            entity = self.env['cm.entity'].create({
                'name': values.get('name', ''),
                'partner_id': values.get('id'),
            })
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if vals.get('is_transaction_entity'):
            if not self.env['cm.entity'].search([('partner_id', '=', self.id)]):
                entity = self.env['cm.entity'].create({
                    'name': self.name,
                    'partner_id': vals.get('id'),
                })
        return res
