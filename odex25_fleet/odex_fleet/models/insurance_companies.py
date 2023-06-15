from odoo import models, fields, api, _


class InsuranceCompanies(models.Model):
    _name = 'insurance.companies'

    name = fields.Char(string='Company Name', required=True)