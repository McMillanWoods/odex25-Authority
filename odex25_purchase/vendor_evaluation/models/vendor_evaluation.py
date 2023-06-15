from odoo import models, fields, api,_ , exceptions
from datetime import datetime
from odoo.exceptions import ValidationError

class CumulativeVendorEvaluation(models.Model):
    _name = 'cumulative.vendor.evaluation'
    _description = 'Vendor Evaluation'

    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor')
    name = fields.Char(related="vendor_id.name")
    cumulative_eval = fields.Float(string='Cumulative',compute="_value_compute")
    last_eval = fields.Float('Last Evaluation')
    owner = fields.Selection([
        ('account', 'Finance'),
        ('purchase' , 'Purchase'),
        ('stock' , 'Stock'),
    ], string='Department')
    line_ids = fields.One2many(comodel_name='vendor.evaluation', inverse_name='evaluation_id', string='')


    @api.depends('line_ids.value')
    def _value_compute(self):
        sum = 0
        last_eval = 0 
        for rec in self:
            for line in rec.line_ids:
                sum += line.value
                last_eval = line.value
            if len(rec.line_ids) > 0:
                rec.cumulative_eval = sum /len(rec.line_ids)
            else:
                rec.cumulative_eval = 0
            rec.write({
                'last_eval' : last_eval
            })
            sum = 0


class VendoeEvaluation(models.Model):
    _name = 'vendor.evaluation'
    _description = 'description'


    evaluation_id = fields.Many2one(comodel_name='cumulative.vendor.evaluation', string='Cumulative Evaluation')
    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor')
    inv_vendor_id = fields.Integer(related='vendor_id.id')
    owner = fields.Selection([
        ('account', 'Finance'),
        ('purchase' , 'Purchase'),
        ('stock' , 'Stock'),
    ], string='Department' )
    inv_owner = fields.Selection([
        ('account', 'Finance'),
        ('purchase' , 'Purchase'),
        ('stock' , 'Stock'),
    ], related='owner')
    value = fields.Float(string='Value',compute="_value_compute")
    date = fields.Date(string='Date' ,default=datetime.today())
    line_ids = fields.One2many(comodel_name='evaluation.details', inverse_name='evaluation_id', string='Details')
    res_id = fields.Integer(string='')
    vendor_type_id = fields.Many2one(comodel_name='vendor.type', string='Vendor Type')
    
    @api.onchange('vendor_type_id')
    def _onchange_vendor_type(self):
        if self.vendor_type_id:
            self.line_ids = False
            criteria = []
            criteria_ids = self.env['evaluation.criteria'].search([('owner' , '=' , self.owner),('vendor_type' , '=' , self.vendor_type_id.id)]).ids
            if len(criteria_ids) == 0:
                raise exceptions.ValidationError(_("Sorry There is No Criteria related to purchase Department to Evaluate This Vendor"))
            for criteria_id in criteria_ids:
                criteria.append((0,0,{'criteria_id' : criteria_id}))
            self.line_ids = criteria
    @api.model
    def create(self, vals):
        vendor_id = vals['inv_vendor_id']
        owner = vals['inv_owner']
        vendor_type_id = vals['vendor_type_id']
        cumulative_evaluation = self.env['cumulative.vendor.evaluation'].search([('owner' , '=' , owner) , ('vendor_id' , '=' , vendor_id)])
        if not cumulative_evaluation:
            cumulative_evaluation = self.env['cumulative.vendor.evaluation'].create({
                'owner' : owner,
                'vendor_id' : vendor_id,
                'line_ids' : False

            })
        vals['evaluation_id'] = cumulative_evaluation.id
        return super(VendoeEvaluation, self).create(vals)

    

    @api.depends('line_ids.value')
    def _value_compute(self):
        sum = 0
        for rec in self:
            for line in rec.line_ids:
                sum += line.value
            if len(rec.line_ids) > 0:
                rec.value = sum /len(rec.line_ids)
            else:
                rec.value = 0
            sum = 0

class EvaluatioinDetails(models.Model):
    _name = 'evaluation.details'
    _description = 'evaluation.details'

    evaluation_id = fields.Many2one(comodel_name='vendor.evaluation', string='Evaluatioin')
    criteria_id = fields.Many2one(comodel_name='evaluation.criteria', string='Criteria')
    value = fields.Float(string='Value',default=0.0)
    vendor_id = fields.Integer(related="evaluation_id.vendor_id.id",store=True)

    @api.constrains('value')
    def _constrains_value(self):
        for rec in self:
            if rec.value < 0 or rec.value > 10:
                raise ValidationError(_("Sorry Evaluation must be between 1 and 10"))
    

    

    
    
    

    
    
    
    
    

    


    

    