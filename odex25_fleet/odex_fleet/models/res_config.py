from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'


    license = fields.Float(string="License")
    car_license = fields.Float( string="Notify Before Car Licence")
    delegation = fields.Float(string="Delegation")
    form = fields.Float(string="Notify Before Form")
    check = fields.Float(string="Notify Before Check")
    insurance = fields.Float(string="Insurance Notify Before")
    operation = fields.Float(string="Operation Notify Before")
    installment = fields.Float(string="Installment Notify Before")
    service = fields.Float( string="Service Notify Before")



class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    license = fields.Float(related="company_id.license", string="License")
    car_license = fields.Float(related="company_id.car_license", string="Car Licence")
    delegation = fields.Float(related="company_id.delegation", string="Delegation")
    form = fields.Float(related="company_id.form", string=" Form")
    check = fields.Float(related="company_id.check", string="Check")
    insurance = fields.Float(related="company_id.insurance", string="Insurance")
    operation = fields.Float(related="company_id.operation", string="Operation Card")
    installment = fields.Float(related="company_id.installment", string="Installment ")
    service = fields.Float(related="company_id.service", string="Service")
