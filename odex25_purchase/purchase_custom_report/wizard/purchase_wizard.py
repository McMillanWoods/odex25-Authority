# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError

# purchase requisition wizard
class TransportMethodWizard(models.TransientModel):
	_name = 'purchase.requisition.wizard'
	
	date_from = fields.Date(string='From')
	date_to = fields.Date(string='To')
	department_id = fields.Many2many('hr.department')
	state = fields.Selection([
        ('draft','Draft'),
        ('in_progress','Confirmed'),
        ('accept','Accepted'),
        ('open','Bid Selection'),
        ('waiting','Waiting For Budget Confirmation'),
        ('checked','Budget Checked'),
        ('done','Done'),
        ('approve','Approved'),
        ('cancel','cancelled'),
    ])
	type = fields.Selection([
        ('project','Project'),
        ('operational','Operational')
    ])
	category_id = fields.Many2many('product.category')
	
	
	def print_report(self):
		[form_values] = self.read()
		if self.date_to <= self.date_from :
			raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))
		data = []
		data.append(('ordering_date','>=',form_values['date_from']))
		data.append(('ordering_date','<=',form_values['date_to']))
		if len(form_values['department_id']) != 0:
			departments = []
			for rec in form_values['department_id']:
				departments.append(rec)
			data.append(('department_id','in',departments))
		if len(form_values['category_id']) != 0:
			categories = []
			for rec in form_values['category_id']:
				categories.append(rec)
			data.append(('category_ids','in',categories))
		if form_values['state'] != False:
			data.append(('state','=',form_values['state']))
		if form_values['type'] != False:
			data.append(('type','=',form_values['type']))
		datas = {
			'ids': [],
			'model': 'purchase.requisition',
			'department':form_values['department_id'],
			'category':form_values['category_id'],
			'state':form_values['state'],
			'type':form_values['type'],
			'form_values':data
			}
		return self.env.ref('purchase_custom_report.action_report_purchase_requisition').report_action(self, data=datas)
		
class TransportMethodAbstract(models.AbstractModel):
	_name="report.purchase_custom_report.purchase_requisition_template"
	
	@api.model
	def _get_report_values(self,docids, data):
		search = []
		status = {
				'draft':_('Draft'),
				'in_progress':_('Confirmed'),
				'accept':_('Accepted'),
				'open':_('Bid Selection'),
				'purchase_manager':_('Purchase manager'),
				'waiting':_('Waiting For Budget Confirmation'),
				'checked':_('Budget Checked'),
				'done':_('Done'),
				'approve':_('Approved'),
				'cancel':_('cancelled'),
    		}
		types = {
			'project':_('Project'),
        	'operational':_('Operational')
		}
		for rec in data['form_values']:
			search.append(tuple(rec))
		dataa = []
		purchase_requisitions = self.env['purchase.requisition'].search(search)
		for rec in purchase_requisitions:
			dataa.append({'order':rec,'type':types[rec.type],'state':status[rec.state]})
		if len(purchase_requisitions) == 0:
			raise ValidationError(_("There is no data"))
		categories=""
		if len(data['category']) != 0:
			partners = self.env['product.category'].search([('id','in',data['category'])])
			for rec in partners:
				categories = categories + rec.name +" "
		categories = self.checkLength(categories)
		departments=""
		if len(data['department']) != 0:
			partners = self.env['hr.department'].search([('id','in',data['department'])])
			for rec in partners:
				departments = departments + rec.name +" "
		departments = self.checkLength(departments)
		state = ""
		if data['state']:
			state = status[data['state']]
		state = self.checkLength(state)
		type = ""
		if data['type']:
			type = types[data['type']]
		type = self.checkLength(type)
		docargs={
			'doc_ids':[],
			'doc_model':['purchase.requisition'],
			'docs':dataa,	
			'date_from':data['form_values'][0][2],
			'date_to':data['form_values'][1][2],
			'categories':categories,
			'departments':departments,
			'state':state,
			'type':type,
			'company':self.env.user.company_id,
				}
		return docargs 
	
	def checkLength(self,string):
		if len(string)==0:
			return _("All")
		else:
			return string

# vendors wizard
class TransportMethodWizard(models.TransientModel):
	_name = 'vendor.report.wizard'
	
	date_from =fields.Date(string='From')
	date_to=fields.Date(string='To')
	supplier_id = fields.Many2many('res.partner')
	department_id = fields.Many2many('hr.department')
	category_id = fields.Many2many('product.category')
	state = fields.Selection([
        ('wait','Waiting To Be Signed'),
        ('unsign','UnSign'),
        ('sign','Sign'),
        ('waiting','Waiting For Budget Confirmation'),
        ('draft','RFQ'),
        ('sent','RFQ Sent'),
        ('to approve','To Approve'),
        ('purchase','Purchase Order'),
        ('done','Locked'),
        ('cancel','Cancelled'),
    ])
	
	
	def print_report(self):
		[form_values] = self.read()
		if self.date_to <= self.date_from :
			raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))
		data = []
		if len(form_values['department_id']) != 0:
			departments = []
			for rec in form_values['department_id']:
				departments.append(rec)
			data.append(('department_id','in',departments))
		if len(form_values['category_id']) != 0:
			categories = []
			for rec in form_values['category_id']:
				categories.append(rec)
			data.append(('category_id','in',categories))
		if form_values['state'] != False:
			data.append(('state','=',form_values['state']))
		data.append(('date_order','>=',form_values['date_from']))
		data.append(('date_order','<=',form_values['date_to']))
		datas = {
			'ids': [],
			'model': 'purchase.requisition',
			'form_values':data,
			'suppliers':form_values['supplier_id'],
			'supplier':form_values['supplier_id'],
			'category':form_values['category_id'],
			'department':form_values['department_id'],
			'state':form_values['state']			
			}
		return self.env.ref('purchase_custom_report.action_report_vendor').report_action(self, data=datas)
		
class TransportMethodAbstract(models.AbstractModel):
	_name="report.purchase_custom_report.vendors_report_template"
	
	@api.model
	def _get_report_values(self,docids, data):
		search = []
		status = {
			'wait':_('Waiting To Be Signed'),
			'unsign':_('UnSign'),
			'sign':_('Sign'),
			'waiting':_('Waiting For Budget Confirmation'),
			'draft':_('RFQ'),
			'sent':_('RFQ Sent'),
			'to approve':_('To Approve'),
			'purchase':_('Purchase Order'),
			'done':_('Locked'),
			'cancel':_('Cancelled'),
		}
		for rec in data['form_values']:
			search.append(tuple(rec))
		purchase_orders = []
		suppliersss = None
		if len(data['suppliers']) ==0 :
			suppliersss = idss = self.env['res.partner'].search([('supplier_rank','>',0)]).ids
		else:
			suppliersss= data['suppliers']
		for rec in suppliersss:												
			sss = search
			sss.append(('partner_id','=',rec))
			po = self.env['purchase.order'].search(sss)
			if len(po) != 0:
				supplier = po[0].partner_id.name
			if len(po) == 0:
				supplier = self.env['res.partner'].search([('id','=',rec)]).name
			purchase_orders.append(
				{
					'len':len(po),
					'total_amount': sum(rec.amount_total for rec in po),
					'supplier':supplier,
				})
			sss.pop(len(sss)-1)
		if len(purchase_orders) == 0:
			raise ValidationError(_("There is no data"))
		total_amount = sum(rec['total_amount'] for rec in purchase_orders)
		lenn = sum(rec['len'] for rec in purchase_orders)
		suppliers=""
		if len(data['supplier']) != 0:
			partners = self.env['res.partner'].search([('id','in',data['supplier'])])
			for rec in partners:
				suppliers = suppliers + rec.name +" "
		departments=""
		if len(data['department']) != 0:
			partners = self.env['hr.department'].search([('id','in',data['department'])])
			for rec in partners:
				departments = departments + rec.name +" "
		departments = self.checkLength(departments)
		suppliers = self.checkLength(suppliers)
		state=""
		if data['state']:
			state = status[data['state']]
		state = self.checkLength(state)
		docargs={
			'doc_ids':[],
			'doc_model':['purchase.order'],
			'date_from':data['form_values'][0][2],
			'date_to':data['form_values'][1][2],
			'suppliers':suppliers,
			'state':state,
			'departments':departments,
			'docs':purchase_orders,
			'total_amount':total_amount,
			'lenn':lenn
				}
		return docargs 

	def checkLength(self,string):
		if len(string)==0:
			return _("All")
		else:
			return string

# purchase orders
class TransportMethodWizard(models.TransientModel):
	_name = 'purchase.order.report.wizard'
	
	date_from =fields.Date(string='From')
	date_to=fields.Date(string='To')
	supplier_id = fields.Many2many('res.partner')
	category_id = fields.Many2many('product.category')
	department_id = fields.Many2many('hr.department')
	state = fields.Selection([
        ('wait','Waiting To Be Signed'),
        ('unsign','UnSign'),
        ('sign','Sign'),
        ('waiting','Waiting For Budget Confirmation'),
        ('draft','RFQ'),
        ('sent','RFQ Sent'),
        ('to approve','To Approve'),
        ('purchase','Purchase Order'),
        ('done','Locked'),
        ('cancel','Cancelled'),
    ])

	
	def print_report(self):
		[form_values] = self.read()
		data = []
		if self.date_to <= self.date_from :
			raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))
		if len(form_values['department_id']) != 0:
			departments = []
			for rec in form_values['department_id']:
				departments.append(rec)
			data.append(('department_id','in',departments))
		if len(form_values['category_id']) != 0:
			categories = []
			for rec in form_values['category_id']:
				categories.append(rec)
			data.append(('category_id','in',categories))
		if len(form_values['supplier_id']) != 0:
			supplier = []
			for rec in form_values['supplier_id']:
				supplier.append(rec)
			data.append(('partner_id','in',supplier))
		if form_values['state'] != False:
			data.append(('state','=',form_values['state']))
		data.append(('date_order','>=',form_values['date_from']))
		data.append(('date_order','<=',form_values['date_to']))
		datas = {
			'ids': [],
			'model': 'purchase.requisition',
			'form_values':data,
			'supplier':form_values['supplier_id'],
			'category':form_values['category_id'],
			'department':form_values['department_id'],
			'state':form_values['state']
			}
		return self.env.ref('purchase_custom_report.action_report_purchase_order').report_action(self, data=datas)
		
class TransportMethodAbstract(models.AbstractModel):
	_name="report.purchase_custom_report.purchase_order_report_template"
	
	@api.model
	def _get_report_values(self,docids, data):
		search = []
		status = {
        'wait':_('Waiting To Be Signed'),
        'unsign':_('UnSign'),
        'sign':_('Sign'),
        'waiting':_('Waiting For Budget Confirmation'),
        'draft':_('RFQ'),
        'sent':_('RFQ Sent'),
        'to approve':_('To Approve'),
        'purchase':_('Purchase Order'),
        'done':_('Locked'),
        'cancel':_('Cancelled'),
		'budget_rejected': _('Rejected By Budget'),
		'wait_for_send':_('Waiting For Send to Budget'),
		'budget_rejected': _('Rejected By Budget'),
    		}


		for rec in data['form_values']:
			search.append(tuple(rec))
		purchase_orders = self.env['purchase.order'].search(search)
		po = []
		if len(purchase_orders) == 0:
			raise ValidationError(_("There is no data"))
		total_amount = sum(rec.amount_total for rec in purchase_orders)
		for rec in purchase_orders:
			po.append({'order':rec,'date':rec.date_order,'state':status[rec.state]})
		suppliers=""
		if len(data['supplier']) != 0:
			partners = self.env['res.partner'].search([('id','in',data['supplier'])])
			for rec in partners:
				suppliers = suppliers + rec.name +" "
		suppliers = self.checkLength(suppliers)
		state = ""
		if data['state']:
			state = status[data['state']]
		state = self.checkLength(state)
		categories=""
		if len(data['category']) != 0:
			partners = self.env['product.category'].search([('id','in',data['category'])])
			for rec in partners:
				categories = categories + rec.name +" "
		categories = self.checkLength(categories)
		departments=""
		if len(data['department']) != 0:
			partners = self.env['hr.department'].search([('id','in',data['department'])])
			for rec in partners:
				departments = departments + rec.name +" "
		departments = self.checkLength(departments)
		docargs={
			'doc_ids':[],
			'doc_model':['purchase.order'],
			'date_from':data['form_values'][0][2],
			'date_to':data['form_values'][1][2],
			'suppliers':suppliers,
			'categories':categories,
			'state':state,
			'departments':departments,
			'docs':po,
			'total_amount':total_amount,
				}
		return docargs 
		
	def checkLength(self,string):
		if len(string)==0:
			return _("All")
		else:
			return string