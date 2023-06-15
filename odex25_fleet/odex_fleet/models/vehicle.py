from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import math

class FleetBranch(models.Model):
    _inherit = 'res.branch'

    state_id = fields.Many2one('res.country.state', string="State", )
    
class Partner(models.Model):
    _inherit = 'res.partner'

    car_owner = fields.Boolean( string="Car Owner", )

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    owner_id = fields.Many2one('res.partner',string="Owner")
    insurance_companies_id = fields.Many2one('insurance.companies',string="Insurance Companies")
    employee_id = fields.Many2one('hr.employee',string="Driver")
    driver_id = fields.Many2one(related='employee_id.user_id.partner_id',store=True,string="Driver")
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id )
    states = fields.Many2one('res.country.state', string="State", )
    old_branch_id = fields.Many2one('res.branch', string="Old Branch", )
    license_end = fields.Date(string="License End")
    check_end = fields.Date(string="Check End Date")
    form_end = fields.Date(string="Form End Date")
    serial_number = fields.Char(string="Serial Number")
    computer_number = fields.Char(string="Computer Number")
    operation_card_number = fields.Char(string="Operation Card Number")
    operation_card_end = fields.Date(string="Operation Card End")
    car_weight = fields.Float(string="Car Weight")
    insurance_number = fields.Char(string="Insurance Number")
    insurance_start_date = fields.Date(string="Insurance Start Date")
    insurance_end_date = fields.Date(string="Insurance End Date")
    insurance_attachment = fields.Binary(string="Insurance Docs")
    installment_number = fields.Char(string="Installment Number")
    fuel_consumption = fields.Float(string="Fuel consumption")
    installment_ids = fields.One2many('insurance.installment','fleet_id',string="Installment")
    service_ids = fields.One2many('fleet.service.line.config','fleet_id',string="Services")
    next_request_date = fields.Date(string="Next Maintenance Date")
    fuel_type = fields.Many2one('fuel.price','Fuel Type', help='Fuel Used by the vehicle')
    model_id = fields.Many2one('fleet.vehicle.model', string="Model Type", required=True, help='Model of the vehicle')
    location = fields.Char(string="Work Location" ,help='Location of the vehicle (garage, ...)')
    car_category = fields.Many2one('car.category', 'Car Category')
    # man_company = fields.Many2one('manufacture.company', 'Manufacture Company')
    man_company = fields.Many2one(related='model_id.man_company_id')
    fleet_type_id = fields.Many2one(related='model_id.fleet_type_id', string="Fleet Type", )
    form_renew_cost = fields.Float(related='model_id.fleet_type_id.amount',string="Form Renew Cost")
    transmission_id = fields.Many2one('transmission.setting',string="Transmission")
    insurance_cost = fields.Float(string="Insurance Cost" ,compute ="get_insurance_cost",store = True,readonly = False)
    department_id = fields.Many2one('hr.department',string="Department",compute = "get_department_id" , store = True)
    project_id = fields.Many2one('project.project', string='Project')

    @api.depends('employee_id')
    def get_department_id(self):
        for rec in self :
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id

    @api.depends('installment_ids')
    def get_insurance_cost(self):
        total = 0
        for rec in self.installment_ids:
            total += rec.amount
        self.insurance_cost = total

    @api.model
    def fleet_expired_cron(self):
        date = datetime.now().date()
        operation = self.company_id.operation
        insurance = self.company_id.insurance
        car_license = self.env.user.company_id.car_license
        # delegation = self.company_id.delegation
        form = self.company_id.form
        check = self.company_id.check
        installment = self.company_id.installment
        if car_license >0:
            date = date + relativedelta(days=car_license)
            fleet = self.env['fleet.vehicle'].sudo().search([('license_end','<=',str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.car_expiration_email_template', False)
                template.send_mail(f.id)
        if insurance>0:
            date = date + relativedelta(days=+int(insurance))
            fleet = self.env['fleet.vehicle'].sudo().search([('insurance_end_date', '>=', str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.insurance_expiration_email_template', False)
                template.send_mail(f.id)

        if form>0:
            date = date + relativedelta(days=+int(form))
            fleet = self.env['fleet.vehicle'].sudo().search([('form_end', '>=', str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.form_expiration_email_template', False)
                template.send_mail(f.id)
        if check>0:
            date = date + relativedelta(days=+int(check))
            fleet = self.env['fleet.vehicle'].sudo().search([('check_end', '>=', str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.check_expiration_email_template', False)
                template.send_mail(f.id)
        if operation>0:
            date = date + relativedelta(days=+int(operation))
            fleet = self.env['fleet.vehicle'].sudo().search([('operation_card_end', '>=', str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.operation_expiration_email_template', False)
                template.send_mail(f.id)
        if installment >0:
            date = date + relativedelta(days=car_license)
            fleet = self.env['insurance.installment'].sudo().search([('date','<=',str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.installment_expiration_email_template', False)
                template.send_mail(f.id)

    @api.onchange('insurance_start_date','insurance_end_date')
    @api.constrains('insurance_start_date','insurance_end_date')
    def check_data(self):
        if self.insurance_start_date and self.insurance_end_date and self.insurance_start_date > self.insurance_end_date:
            raise UserError(_('Insurance Start Date must be less than or equal Insurance End Date '))

class FleetType(models.Model):
    _name = 'fleet.type'
    _description = 'Fleet Type'
    

    name = fields.Char(string="Name")
    amount = fields.Float(string="Renew Amount")

class FuelPrice(models.Model):
    _name = 'fuel.price'
    _description = 'Fuel Price'
    _rec_name = 'fuel_type'

    fuel_type = fields.Many2one('product.product', string='Fuel Type',help='Fuel Used by the vehicle')
    price = fields.Float(string="Price")
    uom_id = fields.Many2one(related='fuel_type.uom_id',string='Unit of Measure', readonly=True)

class CarCtegory(models.Model):
    _name = 'car.category'
    _description = 'Car Category'
    _rec_name = 'car_category'

    car_category = fields.Char('Car Category')

class FleetVehicleModelBrand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'
    man_company_id = fields.Many2one('manufacture.company')

class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    man_company_id = fields.Many2one(related='brand_id.man_company_id')
    fleet_type_id = fields.Many2one('fleet.type', string="Fleet Type")


class ManufactureCompany(models.Model):
    _name = 'manufacture.company'
    _description = 'Manufacture Company'
    _rec_name = 'man_company'

    man_company = fields.Char('Manufacture Company')
    brand_ids = fields.Many2many('fleet.vehicle.model.brand')

class TransmissionType(models.Model):
    _name = 'transmission.setting'
    _description = 'Trnsmission Setting'
    _rec_name = 'transmission'

    transmission = fields.Char('Transmission')

class InsuranceInstallment(models.Model):
    _name = 'insurance.installment'
    _description = 'Insurance Installment'

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    amount = fields.Float(string="Amount")
    paid = fields.Date(string="Paid")
    fleet_id = fields.Many2one('fleet.vehicle',string="Fleet")
    
# class FleetVehicleCost(models.Model):
#     _inherit = 'fleet.vehicle.cost'




#     branch_id = fields.Many2one('res.branch', string="Branch",  default=lambda self: self.env.user.branch_id)
#     number = fields.Float(string="Number")
#     total = fields.Float(string="Total", compute='_compute_total',readonly=True)

#     @api.onchange('number','amount')
#     def _compute_total(self):
#         for r in self:
#             r.total = r.number * r.amount



#     @api.onchange('vehicle_id')
#     def get_branch(self):
#         if self.vehicle_id:
#             self.branch_id = self.vehicle_id.branch_id.id if  self.vehicle_id.branch_id else False

class FleetVehicleCost(models.Model):
    _name = 'fleet.vehicle.cost'
    _description = 'Cost related to a vehicle'
    _order = 'date desc, vehicle_id asc'

    name = fields.Char(related='vehicle_id.name', string='Name', store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', help='Vehicle concerned by this log')
    cost_subtype_id = fields.Many2one('fleet.service.type', 'Type', help='Cost type purchased with this cost')
    amount = fields.Float('Total Price')
    cost_type = fields.Selection([
        ('contract', 'Contract'),
        ('services', 'Services'),
        ('fuel', 'Fuel'),
        ('other', 'Other')
        ], 'Category of the cost', default="other", help='For internal purpose only', required=True)
    parent_id = fields.Many2one('fleet.vehicle.cost', 'Parent', help='Parent cost to this current cost')
    service_id = fields.Many2one('fleet.vehicle.log.services', 'Service', help='Service cost to this current cost')
    cost_ids = fields.One2many('fleet.vehicle.cost', 'parent_id', 'Included Services', copy=True)
    odometer_id = fields.Many2one('fleet.vehicle.odometer', 'Odometer', help='Odometer measure of the vehicle at the moment of this log')
    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer', string='Odometer Value',
        help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed')
    contract_id = fields.Many2one('fleet.vehicle.log.contract', 'Contract', help='Contract attached to this cost')
    auto_generated = fields.Boolean('Automatically Generated', readonly=True)
    description = fields.Char("Cost Description")
    branch_id = fields.Many2one('res.branch', string="Branch",  default=lambda self: self.env.user.branch_id)
    number = fields.Float(string="Number")
    total = fields.Float(string="Total", compute='_compute_total',readonly=True)

    @api.onchange('number','amount')
    def _compute_total(self):
        for r in self:
            r.total = r.number * r.amount



    @api.onchange('vehicle_id')
    def get_branch(self):
        if self.vehicle_id:
            self.branch_id = self.vehicle_id.branch_id.id if  self.vehicle_id.branch_id else False



    def _get_odometer(self):
        for record in self:
            if record.odometer_id:
                record.odometer = record.odometer_id.value

    def _set_odometer(self):
        for record in self:
            if not record.odometer:
                raise UserError(_('Emptying the odometer value of a vehicle is not allowed.'))
            odometer = self.env['fleet.vehicle.odometer'].create({
                'value': record.odometer,
                'date': record.date or fields.Date.context_today(record),
                'vehicle_id': record.vehicle_id.id
            })
            self.odometer_id = odometer

    @api.model
    def create(self, data):
        # make sure that the data are consistent with values of parent and contract records given
        if 'parent_id' in data and data['parent_id']:
            parent = self.browse(data['parent_id'])
            data['vehicle_id'] = parent.vehicle_id.id
            data['date'] = parent.date
            data['cost_type'] = parent.cost_type
        if 'contract_id' in data and data['contract_id']:
            contract = self.env['fleet.vehicle.log.contract'].browse(data['contract_id'])
            data['vehicle_id'] = contract.vehicle_id.id
            data['cost_subtype_id'] = contract.cost_subtype_id.id
            data['cost_type'] = contract.cost_type
        if 'odometer' in data and not data['odometer']:
            # if received value for odometer is 0, then remove it from the
            # data as it would result to the creation of a
            # odometer log with 0, which is to be avoided
            del data['odometer']
        return super(FleetVehicleCost, self).create(data)



class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    @api.model
    def default_get(self, default_fields):
        res = super(FleetVehicleLogServices, self).default_get(default_fields)
        rec = self.env['fleet.account.config'].sudo().search([('type', '=', 'service'), ('state', '=', 'confirm')],
                                                             limit=1)
        if rec:
            res['account_id'] = rec.account_id.id
            res['tax_id'] = rec.tax_id.id
        else:
            raise ValidationError(_("You Need To Configurate Account Details"))
        return res

    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id )
    account_id = fields.Many2one('account.account', string="Account")
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False)
    partner_id = fields.Many2one('res.partner', string="Service Provider")
    request_id = fields.Many2one('fleet.maintenance', string="Maintenance Request")
    state = fields.Selection([
        ('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('approve', 'Approved'),
                                        ('invoiced', 'Invoiced'),
                                        ('refused', 'Refused'),
                                        ('cancel', 'Cancel'),
        
    ], default='draft',related="status")
    
    status = fields.Selection([('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('approve', 'Approved'),
                                        ('invoiced', 'Invoiced'),
                                        ('refused', 'Refused'),
                                        ('cancel', 'Cancel'),
                                         ], default='draft')
    edit_access = fields.Boolean(compute="get_access",)
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    cost_subtype_id = fields.Many2one('fleet.service.type', 'Type', help='Cost type purchased with this cost')
    cost_ids = fields.One2many('fleet.vehicle.cost', 'service_id', 'Included Services', copy=True)
    employee_id = fields.Many2one('hr.employee',string="Driver")
    service_type_id = fields.Many2one(
        'fleet.service.type', 'Service Type', required=False,
        default=lambda self: self.env.ref('fleet.type_service_service_8', raise_if_not_found=False),
    )
    @api.onchange('odometer')
    def onchange_odometer(self):
        for rec in self :
            if rec.odometer < rec.vehicle_id.odometer :
                if rec.env.user.lang == 'en_US':
                    raise ValidationError(_("odometer should be more than current odometer"))
                elif rec.env.user.lang == 'ar_SY' or rec.env.user.lang == 'ar_001':
                    raise ValidationError(_("عداد المسافات يجب أن يكون أكبر من عدادت المسافات الحالي"))

    def get_access(self):
        for rec in self:
            rec.edit_access = False
            if rec.status == 'approve' and  self.env.user.has_group('odex_fleet.fleet_group_account'):
                rec.edit_access = True

    def action_confirm(self):
        self.sudo().status = 'confirm'

    def action_approve(self):
        self.status = 'approve'
        self.vehicle_id.odometer = self.odometer

    def action_cancel(self):
        self.status = 'cancel'

    def action_refuse(self):
        self.status = 'refused'

    @api.onchange('vehicle_id')
    def get_branch(self):
        if self.vehicle_id:
            self.branch_id = self.vehicle_id.branch_id.id if  self.vehicle_id.branch_id else False
            self.odometer = self.vehicle_id.odometer
            self.employee_id = self.vehicle_id.employee_id

    def create_invoice(self):
        invoice = self.env['account.move'].sudo().create({
            'partner_id': self.partner_id.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'name': 'Fleet Service Cost Invoice ',
            # 'account_id': self.partner_id.property_account_payable_id.id,
            'branch_id': self.vehicle_id.branch_id.id,
            'move_type': 'in_invoice',
            'invoice_date': datetime.now().today(),
        })

        self.env['account.move.line'].with_context(check_move_validity=False).sudo().create({
            'quantity': 1,
            'price_unit': self.amount,
            'move_id': invoice.id,
            'name': 'Fleet Service Cost',
            'account_id': self.account_id.id,
            'tax_ids': [(6, 0, [self.tax_id.id])],

        })
        self.sudo().invoice_id = invoice.id
        # invoice.sudo().action_invoice_open()
        self.sudo().status = 'invoiced'


    @api.onchange('cost_ids')
    def get_amount_total(self):
        for rec in self:
            rec.amount = sum(rec.cost_ids.mapped('total'))

class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id )

    @api.onchange('vehicle_id')
    def get_branch(self):
        if self.vehicle_id:
            self.branch_id = self.vehicle_id.branch_id.id if  self.vehicle_id.branch_id else False

class FleetVehicleLogFuel(models.Model):
    _name = 'fleet.vehicle.log.fuel'
    _description = 'Fuel log for vehicles'
    _inherits = {'fleet.vehicle.cost': 'cost_id'}

    @api.model
    def default_get(self, default_fields):
        res = super(FleetVehicleLogFuel, self).default_get(default_fields)
        service = self.env.ref('fleet.type_service_refueling', raise_if_not_found=False)
        res.update({
            'date': fields.Date.context_today(self),
            'cost_subtype_id': service and service.id or False,
            'cost_type': 'fuel'
        })
        rec = self.env['fleet.account.config'].sudo().search([('type','=','fuel'),('state','=','confirm')],limit=1)                                              
        if rec:
            res['account_id'] = rec.account_id.id
            res['tax_id'] = rec.tax_id.id
        else:
            raise ValidationError(_("You Need To Configurate Account Details"))
        return res


    liter = fields.Float()
    price_per_liter = fields.Float()
    purchaser_id = fields.Many2one('res.partner', 'Purchaser', domain="['|',('customer_rank','>',0),('employee','=',True)]")
    inv_ref = fields.Char('Invoice Reference', size=64)
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier_rank','=',True)]")
    notes = fields.Text()
    cost_id = fields.Many2one('fleet.vehicle.cost', 'Cost', required=True, ondelete='cascade')
    branch_id = fields.Many2one('res.branch', string="Branch",  default=lambda self: self.env.user.branch_id)
    account_id = fields.Many2one('account.account', string="Account")
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    invoice_id = fields.Many2one('account.move', string="Invoice",copy=False)
    partner_id = fields.Many2one('res.partner', string="Service Provider")
    fuel_type = fields.Many2one(related='vehicle_id.fuel_type')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('approve', 'Approved'),
                                        ('invoiced', 'Invoiced'),
                                        ('refused', 'Refused'),
                                        ('cancel', 'Cancel'),
                                         ], default='draft')
    amount = fields.Float('Total Untax')
    liter = fields.Float()
    price_tax = fields.Float(string='Tax')
    total_price_tax = fields.Float(string='Total', )
    price_per_liter = fields.Float()
    cal_type = fields.Selection(selection=[('total', 'Total'),('liter','Liter')],string="Calculation Type",default='liter')
    edit_access = fields.Boolean(compute="get_access",)
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee',string="Driver")

    # we need to keep this field as a related with store=True because the graph view doesn't support
    # (1) to address fields from inherited table
    # (2) fields that aren't stored in database
    cost_amount = fields.Float(related='cost_id.amount', string='Amount', store=True)

    @api.onchange('odometer')
    def onchange_odometer(self):
        for rec in self:
            if rec.odometer < rec.vehicle_id.odometer:
                if rec.env.user.lang == 'en_US':
                    raise ValidationError(_("odometer should be more than current odometer"))
                elif rec.env.user.lang == 'ar_SY' or rec.env.user.lang == 'ar_001':
                    raise ValidationError(_("عداد المسافات يجب أن يكون أكبر من عدادت المسافات الحالي"))

    @api.onchange('liter', 'price_per_liter', 'amount')
    def _onchange_liter_price_amount(self):
        # need to cast in float because the value receveid from web client maybe an integer (Javascript and JSON do not
        # make any difference between 3.0 and 3). This cause a problem if you encode, for example, 2 liters at 1.5 per
        # liter => total is computed as 3.0, then trigger an onchange that recomputes price_per_liter as 3/2=1 (instead
        # of 3.0/2=1.5)
        # If there is no change in the result, we return an empty dict to prevent an infinite loop due to the 3 intertwine
        # onchange. And in order to verify that there is no change in the result, we have to limit the precision of the
        # computation to 2 decimal
        liter = float(self.liter)
        price_per_liter = float(self.price_per_liter)
        amount = float(self.amount)
        if liter > 0 and price_per_liter > 0 and round(liter * price_per_liter, 2) != amount:
            self.amount = round(liter * price_per_liter, 2)
        elif amount > 0 and liter > 0 and round(amount / liter, 2) != price_per_liter:
            self.price_per_liter = round(amount / liter, 2)
        elif amount > 0 and price_per_liter > 0 and round(amount / price_per_liter, 2) != liter:
            self.liter = round(amount / price_per_liter, 2)


   
    def get_access(self):
        for rec in self:
            rec.edit_access = False
            if rec.state == 'approve' and  self.env.user.has_group('odex_fleet.fleet_group_account'):
                rec.edit_access = True

    @api.onchange('cal_type','price_per_liter','liter','total_price_tax')
    def _get_total(self):
        for rec in self:
            
            if rec.cal_type == 'total':
                taxes = rec.tax_id.compute_all(rec.price_per_liter, None,  1, product=None,
                                                partner=None)
                val = round(sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),2)
                pice_tax = rec.price_per_liter + val
                liter = rec.total_price_tax / pice_tax if val and rec.price_per_liter > 0 else 0
                new_taxes = rec.tax_id.compute_all(rec.price_per_liter, None, liter, product=None,
                                               partner=None)
                tax = sum(t.get('amount', 0.0) for t in new_taxes.get('taxes', []))
                rec.price_tax = tax
                amount = rec.total_price_tax - rec.price_tax
                rec.liter = liter if liter>0 else 0
                rec.amount = amount if amount>0 else 0
            else:
                taxes = rec.tax_id.compute_all(rec.price_per_liter, None,rec.liter, product=None,
                                               partner=None)
                tax = round(sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),2)
                rec.price_tax = tax if tax>0 else 0
                rec.amount = rec.liter * rec.price_per_liter
                rec.total_price_tax = round(rec.amount+ rec.price_tax,2)

   

    # def get_account_data(self):
    #     print("in herere============")
    #     rec = self.env['fleet.account.config'].sudo().search([('type','=','fuel'),('state','=','confirm')],limit=1)
    #     if rec:
    #         self.account_id = rec.account_id.id
    #         self.tax_id = rec.tax_id.id
    #     else:
    #         raise ValidationError(_("You Need To Configurate Account Details"))

    @api.constrains('odometer','price_per_liter')
    def odometer_check(self):
        for rec in self:
            if rec.odometer <= 0:
                raise ValidationError(_("Odometer Should Be Greater Than 0"))

    @api.constrains('liter')
    def liter_check(self):
        for rec in self:
            if rec.liter <= 0:
                raise ValidationError(_("liter Should Be Greater Than 0"))

    def action_confirm(self):
        self.odometer_check()
        self.sudo().state = 'confirm'

    def action_approve(self):
        self.state = 'approve'
        self.vehicle_id.odometer = self.odometer

    def action_cancel(self):
        self.state = 'cancel'

    def action_refuse(self):
        self.state = 'refused'

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.purchaser_id = self.vehicle_id.driver_id.id

            self.price_per_liter = self.vehicle_id.fuel_type.price or 0
            self.branch_id = self.vehicle_id.branch_id.id if  self.vehicle_id.branch_id else False
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.employee_id = self.vehicle_id.employee_id
            self.odometer = self.vehicle_id.odometer


  

    def create_invoice(self):
        invoice = self.env['account.move'].sudo().create({
            'partner_id': self.partner_id.id,
            'currency_id':self.env.user.company_id.currency_id.id,
            'name': 'Fuel Cost Invoice ',
            'journal_id':2,
            # 'account_id': self.partner_id.property_account_payable_id.id,
            'branch_id': self.vehicle_id.branch_id.id,
            'move_type': 'in_invoice',
            'invoice_date':datetime.now().today(),
        })

        self.env['account.move.line'].with_context(check_move_validity=False).sudo().create({
            'quantity': self.liter  if self.cal_type== 'liter' else 1,
            'price_unit': self.price_per_liter if self.cal_type== 'liter' else self.amount,
            'move_id': invoice.id,
            'name': 'Fuel Cost',
            'account_id': self.account_id.id,
            'tax_ids':   [(6, 0, [self.tax_id.id])],
            'product_id': self.fuel_type.fuel_type.id,
            # 'uom_id': self.fuel_type.uom_id.id,
        })
        self.sudo().invoice_id = invoice.id
        invoice.sudo()._compute_amount()
#         invoice.sudo().action_invoice_open()
        self.sudo().state = 'invoiced'
        date = fields.Date.context_today(self)
        data = {'value': self.odometer, 'date': date, 'vehicle_id': self.vehicle_id.id}
        self.env['fleet.vehicle.odometer'].sudo().create(data)


class FleetServiceConfig(models.Model):
    _name = 'fleet.service.line.config'
    _description = 'Fleet Serive Line'

    fleet_id = fields.Many2one('fleet.vehicle')
    service_ids = fields.Many2many('fleet.service.type',string="Service")
    date = fields.Date(string="Next Request Date")
    next_odometer = fields.Float(string="Next Odometer")
    odometer = fields.Float(string="Next Odometer")
    type = fields.Selection(selection=[('date', 'Date'), ('odometer', 'Odometer')],
                                    string="Type")

    @api.onchange('type','odometer')
    def get_vals(self):
        for rec in self:
            if rec.type == 'odometer':
                rec.get_next_odometer()
                
    def get_next_odometer(self):
        for rec in self:
            rec.next_odometer = rec.fleet_id.odometer + rec.odometer

    @api.model
    def fleet_maintenance_cron(self):
        date = self.env['fleet.service.line.config'].sudo().search([('type','=','date'),('date','=',str(datetime.now().date()))])
        odo = self.env['fleet.service.line.config'].sudo().search([('type', '=', 'odometer'),
                                                                     ])
        odo = odo.filtered(lambda r:r.fleet_id.odometer >= r.next_odometer)
        print("FDDDDDDDDDDDDDDDDDDDDd",str(datetime.now().date()),date,odo.mapped('fleet_id.odometer'))
        self.create_request(date)
        self.create_request(odo)

    def create_request(self,data):
        for d in data:
            self.env['fleet.maintenance'].sudo().create({
                'name':"Preventive Maintenance",
                'type':'preventive',
                'vehicle_id':d.fleet_id.id,
                'branch_id':d.fleet_id.branch_id.id,
                'odometer':d.fleet_id.odometer,
                'license_plate':d.fleet_id.license_plate,
                'line_id':d.id,
                'employee_id':d.fleet_id.employee_id.id if d.fleet_id.employee_id else False,
                'service_ids':[(0,0,{'service_id':l.id}) for l in d.service_ids]
            })
            if d.type == 'odometer':
                d.get_next_odometer()

