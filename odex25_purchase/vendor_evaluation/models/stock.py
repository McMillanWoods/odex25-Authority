from odoo import models, fields, api,_,exceptions

class CustomPurchaseOrder(models.Model):
    _inherit = 'stock.picking'

    
    def action_vendor_eval(self):
        criteria = []
        criteria_ids = self.env['evaluation.criteria'].search([('owner' , '=' , 'stock')]).ids
        if len(criteria_ids) == 0:
            raise exceptions.ValidationError(_("Sorry There is No Criteria related to stock Department order to Evaluate This Vendor"))

        for criteria_id in criteria_ids:
            criteria.append((0,0,{'criteria_id' : criteria_id}))
        evaluation = self.env['vendor.evaluation'].search([('res_id' , '=', self.id)])
        if not evaluation:
            return  {     
                'type': 'ir.actions.act_window',
                'name': 'Vendor Evaluation',   
                'res_model': 'vendor.evaluation',   
                    
                'view_mode': 'form',   
                'target': 'new', 
                'context' : {'default_res_id' : self.id,'default_line_ids' : criteria , 'default_owner' : 'stock' , 'default_vendor_id' : self.partner_id.id }
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

    