from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta



class OnlinePurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    published_in_portal = fields.Boolean('Show',default=False)
    publish_in_portal = fields.Boolean(string="Publish in Portal")
    availability_period = fields.Integer('Availability Period (days)')
    email = fields.Char('Email')
    email_notify = fields.Boolean('Receive Notification')
    po_notification = fields.Boolean('PO Notification')
    num_applications = fields.Integer('Portal Application', compute="_compute_num_applications")
    available_until = fields.Date('Availablity date')


    
    def extend_availability(self):
        return {     
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',   
            'res_model': 'availability.period.extend',   
            'view_mode': 'form',   
            'target': 'new', 
            'context' : {'default_requisition_id' : self.id}
        }

    @api.depends('name')
    def _compute_num_applications(self):
        for rec in self:
            rec.num_applications = self.env['tender.application'].sudo().search_count([('tender_id' , '=' , rec.id)])

    
    def application(self):
        return {     
            'type': 'ir.actions.act_window',
            'name': 'Applications',   
            'res_model': 'tender.application',   
            'view_mode': 'tree,form',   
            'target': 'current', 
            'domain' : [('tender_id' , '=' , self.id)]
        }
    
    def action_show_portal(self):
        self.write({
            'published_in_portal' : True,
            'available_until' : datetime.today() + relativedelta(days=self.availability_period)
        })


    
    def Unpublish(self):
        self.write({
            'published_in_portal' : False,
        })
    
    
    def action_done(self):
        sup = super(OnlinePurchaseRequisition,self).action_done()
        self.Unpublish()
        template = self.env.ref('online_tendering.not_win_email_template')
        for po in self.purchase_ids:
            if po.state != "purchase":
                email = template.send_mail(po.id,force_send=True,)
        return sup



class POCustom(models.Model):
    _inherit = 'purchase.order'

    application_id = fields.Many2one('tender.application' , 'Referance Application')

    
    def button_confirm(self):
        for rec in self:
            super(POCustom,rec).button_confirm()
            if rec.application_id:
                rec.application_id.state = 'contract'


class PeriodExtend(models.TransientModel):
    _name = 'availability.period.extend'

    requisition_id = fields.Many2one('purchase.requisition')
    days = fields.Integer("Days")

    
    def action_extend(self):
        if datetime.strptime(self.requisition_id.available_until,'%Y-%m-%d') >= datetime.today():
            self.requisition_id.available_until = datetime.strptime(self.requisition_id.available_until,'%Y-%m-%d') + relativedelta(days=self.days)
        else:
            self.requisition_id.available_until = datetime.today() + relativedelta(days=self.days)
