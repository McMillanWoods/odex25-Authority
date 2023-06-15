from odoo import models, fields, api,_ , exceptions


class CustomPurchaseOrder(models.Model):
    _inherit = 'account.move'

    
    def action_vendor_eval(self):
        criteria = []
        criteria_ids = self.env['evaluation.criteria'].search([('owner' , '=' , 'account')]).ids
        if len(criteria_ids) == 0:
            raise exceptions.ValidationError(_("Sorry There is No Criteria related to purchase Department to Evaluate This Vendor"))
        for criteria_id in criteria_ids:
            criteria.append((0,0,{'criteria_id' : criteria_id}))
        evaluation = self.env['vendor.evaluation'].search([('res_id' , '=', self.id),('owner' , '=' , 'account' )])
        if not evaluation:
            return  {     
                'type': 'ir.actions.act_window',
                'name': 'Vendor Evaluation',   
                'res_model': 'vendor.evaluation',   
                    
                'view_mode': 'form',   
                'target': 'new', 
                'context' : {'default_res_id' : self.id,'default_line_ids' : criteria , 'default_owner' : 'account' , 'default_vendor_id' : self.partner_id.id }
            }
        else:
            return  {     
                'type': 'ir.actions.act_window',
                'name': 'Vendor Evaluation',   
                'res_model': 'vendor.evaluation',   
                    
                'view_mode': 'form',  
                'res_id' :  evaluation.id,
                'target': 'new', 
            }

    