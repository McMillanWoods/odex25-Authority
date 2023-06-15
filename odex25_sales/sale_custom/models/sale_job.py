# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleJob(models.Model):
    _name = 'sale.job'
    _description = 'Manpower'

    name = fields.Text('Description', required=True, translate=True)
    job_id = fields.Many2one('hr.job', 'Position')
    no_year_experience = fields.Char('Years of Experience')
    qty = fields.Integer('QTY')
    duration = fields.Integer('Duration')
    month_rate = fields.Float('Monthly Rate')
    total = fields.Float('Total', compute="_compute_total", sort=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade', index=True, copy=False)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(job_id=False)
        return super(SaleJob, self).create(values)

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_("You cannot change the type of a sale quote line. Instead you should delete the current line and create a new line of the proper type."))
        return super(SaleJob, self).write(values)


    @api.onchange('job_id')
    def onchange_job_id(self):
        self.name = self.job_id.name

    
    @api.depends('qty', 'duration', 'month_rate')
    def _compute_total(self):

        for rec in self:

            rec.total = rec.qty * rec.duration * rec.month_rate