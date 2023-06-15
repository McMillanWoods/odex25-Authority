# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleDepartmentTemplateLine(models.Model):
    _name = 'sale.department.template.line'
    _description = 'Mhrs Estimate Template Line'

    name = fields.Text('Description', required=True, translate=True)
    department_id = fields.Many2one('hr.department', 'Activity')
    no_sheet = fields.Integer('No of Sheet')
    hrs_sheet = fields.Float('Hrs Sheet')
    cairo_hrs = fields.Float('Cairo Hrs')
    ksa_hrs = fields.Float('KSA Hrs')
    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quotation Template Reference',
        required=True, ondelete='cascade', index=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(department_id=False)
        return super(SaleDepartmentTemplateLine, self).create(values)

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_("You cannot change the type of a sale quote line. Instead you should delete the current line and create a new line of the proper type."))
        return super(SaleDepartmentTemplateLine, self).write(values)


    @api.onchange('department_id')
    def onchange_department_id(self):
        self.name = self.department_id.name

        
