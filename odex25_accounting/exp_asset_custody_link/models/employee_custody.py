from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError

from odoo import SUPERUSER_ID


# from datetime import datetime , date


class EmployeeCustody(models.Model):
    _inherit = 'custom.employee.custody'

    state = fields.Selection(selection=[
        ("draft", _("Draft")),
        ("submit", _("send")),
        ("direct", _("Direct Manager")),
        ("admin", _("Human Resources Manager")),
        ("wait", _("Wait Assignment")),
        ("assign", _("Assignment")),
        ("wait_release", _("Wait Release")),
        ("done", _("Return Done")),
        ("refuse", _("Refuse"))
    ], default='draft')

    asset_line_ids = fields.One2many('asset.custody.line', 'asset_custody_line',required=True)
    asset_assign_count = fields.Integer(compute='_asset_assign_count', string='Asset Assignment')
    asset_release_count = fields.Integer(compute='_asset_release_count', string='Asset Release')
    purchase_request_count = fields.Integer(compute='_purchase_request_count', string='Purchase Request')
    purchase_request_create = fields.Boolean(string='Purchase Request Create')


    def create_asset_custody(self):
        for i in self.asset_line_ids:
            data = {
                'date': self.current_date,
                'asset_id': i.asset_id.id,
                'type': 'assignment',
                'custody_type': i.custody_type,
                'custody_period': i.custody_period,
                'state': 'draft',
                'user_id': self.env.uid,
                'new_employee_id': self.employee_id.id,
                'new_department_id': self.department_id.id,
                'emp_asset_custody_id': self.id,

            }
            self.env['account.asset.operation'].create(data)


    def asset_custody_release(self):
        for i in self.asset_line_ids:
            data = {
                'name': i.asset_id.name,
                'date': self.current_date,
                'asset_id': i.asset_id.id,
                'type': 'release',
                'custody_type': i.custody_type,
                'custody_period': i.custody_period,
                'state': 'draft',
                'user_id': self.env.uid,
                'current_employee_id': self.employee_id.id,
                'new_employee_id': self.employee_id.id,
                'current_department_id': self.department_id.id,
                'emp_asset_custody_id': self.id,

            }
            self.env['account.asset.operation'].create(data)

    def create_purchase_request(self):
        line_ids = []
        for line in self.custody_line_ids:
            line_ids.append((0, 6, {
                'name': line.name,
                'qty': line.quantity,
                'price_unit': 0,
                'uom_id': 0,
            }))
        request_id = self.env['purchase.request'].sudo().create({
            'employee_id': self.employee_id.id,
            'department_id': self.department_id.id,
            'date': self.current_date,
            'line_ids': line_ids,
            'custody_id': self.id
        })

        self.write({'purchase_request_create': True})

        return {
            'name': "Purchase Request",
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request',
            'view_mode': 'form',
            'res_id': request_id.id,
        }

    def _asset_assign_count(self):
        self.asset_assign_count = len(
            self.env['asset.custody.line'].search([('asset_custody_line', '=', self.id)]))


    def _asset_release_count(self):
        self.asset_release_count = len(
            self.env['asset.custody.line'].search([('asset_custody_line', '=', self.id)]))

    def _purchase_request_count(self):
        self.purchase_request_count = len(
            self.env['employee.custody.line'].search([('employee_custody_line', '=', self.id)]))


    def approve(self):
        if not self.asset_line_ids:
            raise exceptions.Warning(_('Please Select an asset'))
        self.create_asset_custody()
        self.write({'state': 'wait'})


    def done(self):
        self.asset_custody_release()
        self.state = "wait_release"

class EmployeeCustodyLine(models.Model):
    _name = 'asset.custody.line'

    # Asset custody fields
    type = fields.Selection([('assignment', 'Assignment')])
    custody_type = fields.Selection(selection=[('personal', 'Personal'), ('general', 'General')])
    custody_period = fields.Selection(selection=[('temporary', 'Temporary'), ('permanent', 'Permanent')])
    return_date = fields.Date()
    date = fields.Date()
    asset_id = fields.Many2one('account.asset')
    asset_custody_line = fields.Many2one(comodel_name='custom.employee.custody')  # Inverse field

class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search(
                [('res_model', '=', vals.get('res_model')), ('res_id', '=', vals.get('res_id')),
                    ('partner_id', '=', vals.get('partner_id'))])

            if len(dups):
                for p in dups:
                    p.unlink()

        res = super(Followers, self).create(vals)

        return res

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    custody_id = fields.Many2one('custom.employee.custody')





