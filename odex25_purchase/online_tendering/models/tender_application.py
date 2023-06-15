from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from datetime import datetime


class TederApplication(models.Model):
    _name = 'tender.application'
    _order = "id desc"

    date = fields.Date(string='Date')
    user_id = fields.Many2one('res.users' , 'Applicant Name')
    name = fields.Char('Name' , default=lambda self: self.env['ir.sequence'].next_by_code(self._name))
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    tender_id = fields.Many2one('purchase.requisition')
    tender_date = fields.Datetime('Tender Date' , related="tender_id.date_end")
    total = fields.Float(string='Total', digits=dp.get_precision('Product Price'),compute="_totol_compute")
    line_ids = fields.One2many("tender.application.line" , "application_id" , "Details")
    state = fields.Selection([('draft' , 'Draft') , ('tender' , 'Tender') , ('contract' , 'Contract'),('reject' , 'Rejected')],string="State" ,default="draft")
    reject_reason = fields.Text(string='Reject Reson')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    vendor_note = fields.Text('Vendor Note', default="/")

    @api.model
    def create(self,vals):
        application = super(TederApplication , self).create(vals)
        if application.tender_id.email_notify:
            template = self.env.ref('online_tendering.email_template_tender_application')
            template.send_mail(application.id,force_send=True,)
        return application
            

    @api.depends('line_ids')
    def _totol_compute(self):
        for rec in self:
            sum = 0
            for line in rec.line_ids:
                sum += line.total
            rec.total = sum

    
    def action_tender(self):
        user = self.user_id
        order_lines = []
        for line in self.line_ids:
            order_lines += [(0,6,{
                'name' : line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom' : line.product_uom_id.id,
                'product_qty' : line.product_qty,
                'price_unit' : line.price_unit,
                'date_planned' : (line.schedule_date and line.schedule_date) or line.application_id.tender_id.ordering_date,
            })]
        po = self.env['purchase.order'].create({
            'application_id' : self.id,  
            'partner_id' : user.partner_id.id,
            'date_order' : datetime.today(),
            'origin' : self.tender_id.name,
            'requisition_id' : self.tender_id.id,
            'order_line' : order_lines
        })
        Attachments = self.env['ir.attachment']
        attachment = self.attachment_id
        if attachment:
            Attachments.sudo().create({
                'name':self.attachment_id.name,
                #'datas_fname': self.attachment_id.name,
                'res_name': self.attachment_id.name,
                'type': 'binary',   
                'res_model': 'purchase.order',
                'res_id': po.id,
                'datas': attachment.datas,
            })
        template = self.env.ref('online_tendering.email_template_application_shortlist')
        email = template.send_mail(self.id,force_send=True,)
        self.write({
            'state'  : 'tender'
        })
        if po:
            return po


    
    def action_reject(self):
        return {     
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',   
            'res_model': 'application.reject.wizard',   
            'view_mode': 'form',   
            'target': 'new', 
            'context' : {'default_application_id' : self.id}
        }
        

    
class TederApplicationLine(models.Model):
    _name = "tender.application.line"
    
    name = fields.Char("Product" , related="product_id.name")
    vendor_id = fields.Many2one('res.partner')
    application_id = fields.Many2one('tender.application', string='Application', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    schedule_date = fields.Date(string='Scheduled Date')
    tax_id = fields.Many2one(comodel_name='account.tax', string='Tax')
    tax = fields.Float(string='Tax Amount', digits=dp.get_precision('Product Price'))
    tender_id = fields.Many2one('purchase.requisition' , related="application_id.tender_id")
    state = fields.Selection(related="application_id.state")
    #TODO add vat field
    total = fields.Float(string='Total', digits=dp.get_precision('Product Price'),compute="_totol_compute")
    
    @api.model
    def create(self,vals):
        line = super(TederApplicationLine,self).create(vals)
        return line
        # line.write({
        #     'tender_id' : line.application_id.tender_id.id,
        #     'vendor_id' : line.application_id.user_id.partner_id.id,
        # })
    @api.depends('product_qty','price_unit','tax_id')
    def _totol_compute(self):
        for rec in self:
            total = rec.product_qty * rec.price_unit
            tax = 0
            if rec.tax_id:
                print('tax_id OOOOOOOOOOOOO', rec.tax_id.amount)
                tax = ((total * rec.tax_id.amount) / 100)
                rec.total = total + tax
            else:
                rec.total = total

            rec.tax =  tax


class RejectWizard(models.TransientModel):
    _name = 'application.reject.wizard'

    application_id = fields.Many2one('tender.application')
    reject_reason = fields.Text(string='Reject Reson')

    
    def action_reject(self):
        self.application_id.reject_reason = self.reject_reason
        self.application_id.state = "reject"



    

