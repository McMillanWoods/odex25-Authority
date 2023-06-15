# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleJobTemplateLine(models.Model):
    _name = 'sale.job.template.line'
    _description = 'Manpower Template Line'

    name = fields.Text('Description', required=True, translate=True)
    job_id = fields.Many2one('hr.job', 'Position')
    no_year_experience = fields.Char('Years of Experience')
    qty = fields.Integer('QTY')
    duration = fields.Integer('Duration')
    month_rate = fields.Float('Monthly Rate')
    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quotation Template Reference',
        required=True, ondelete='cascade', index=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(job_id=False)
        return super(SaleJobTemplateLine, self).create(values)

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_("You cannot change the type of a sale quote line. Instead you should delete the current line and create a new line of the proper type."))
        return super(SaleJobTemplateLine, self).write(values)


    @api.onchange('job_id')
    def onchange_job_id(self):
        self.name = self.job_id.name

    