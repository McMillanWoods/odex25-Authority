from odoo import models, fields, api, _, exceptions
class AccountAssetOperation(models.Model):
    _inherit = 'account.asset.operation'

    emp_asset_custody_id = fields.Many2one(comodel_name='custom.employee.custody')

    def act_confirm(self):
        module = self.env['ir.module.module'].sudo()
        exp_petty_cash_module = module.search(
            [('state', '=', 'installed'), ('name', '=', 'exp_employee_custody')])
        if not self.asset_id:
            raise exceptions.Warning(_('Asset is required to confirm this operation.'))
        if self.type in ('assignment', 'release', 'transfer'):
            self.custody_confirm()
        self.state = 'done'
        if self.type == 'assignment':
            self.asset_id.status = 'assigned'
            if exp_petty_cash_module:
                custody = self.env['custom.employee.custody'].search([('id', '=', self.emp_asset_custody_id.id)])
                print("===============================================================", custody)
                for cus in custody:
                    operation = self.env['account.asset.operation'].search(
                        [('emp_asset_custody_id', '=', cus.id), ('type', '=', 'assignment')])
                    print("----------", operation)
                    print("----------", operation.state)
                    if all(ope.state in 'done' for ope in operation):
                        print("----------", operation.state)
                        cus.write({'state': 'assign'})
        elif self.type == 'release':
            self.asset_id.status = self.asset_status == 'good' and 'available' or 'scrap'
            if exp_petty_cash_module:
                custody = self.env['custom.employee.custody'].search([('id', '=', self.emp_asset_custody_id.id)])
                for cus in custody:
                    operation = self.env['account.asset.operation'].search(
                        [('emp_asset_custody_id', '=', cus.id), ('type', '=', 'release')])
                    if all(ope.state in 'done' for ope in operation):
                        cus.write({'state': 'done'})


    # def custody_confirm(self):
    #
    #     self.asset_id.employee_id = self.new_employee_id.id
    #     self.asset_id.department_id = self.new_department_id.id
    #     self.asset_id.location_id = self.new_location_id.id
    #     self.asset_id.custody_type = self.custody_type
    #     self.asset_id.custody_period = self.custody_period
    #     self.asset_id.return_date = self.return_date
    #     self.asset_id.purpose = self.note
