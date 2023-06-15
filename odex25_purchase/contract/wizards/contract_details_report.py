# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError

class contractDetailsReport(models.TransientModel):
	_name = 'details.report.wizard'
	_description = 'details.report.wizard'
	date_from =fields.Date(string='From')
	date_to=fields.Date(string='To')
	supplier_id = fields.Many2one('res.partner')
	user_id = fields.Many2one('res.users')
	contract_ids = fields.Many2many('contract.contract')
	
	state = fields.Selection(
	selection=[('new', 'New'),
	('to_confirm' ,'To Confirm'),
	('confirmed', 'Confirmed'),
	('in_progress', 'In progress'),
	('suspended', 'Suspended'),
	('closed', 'Closed'),
	('cancel', 'Cancel')],

	)



	@api.onchange('supplier_id','state','user_id')
	def _onchange_supplier_id(self):
		domain = []
		if self.supplier_id:
			domain.append(('partner_id', '=', self.supplier_id.id))
		
		if self.state :
			domain.append(('state', '=', self.state))
		
		if self.user_id:
			domain.append(('user_id', '=', self.user_id.id))
	
		return {

			'domain': {
			'contract_ids': domain

			}
		}

	@api.onchange('contract_ids')
	def _onchange_contract_id(self):
		if self.contract_ids:
			partner = self.env['contract.contract'].search([('id','in',self.contract_ids.ids)]).mapped('partner_id')
			return {
			'value':{'partner_id':False},
			'domain': {
			'partner_id': [('id', 'in', partner.ids)]
			}
			}
		return {}
			

	def print_report(self):
		[form_values] = self.read()
		if self.date_to <= self.date_from :
			raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))
		data = []
		if len(form_values['contract_ids']) != 0:
			contracts = []
			for rec in form_values['contract_ids']:
				contracts.append(rec)
			data.append(('id','in',contracts))
		if self.supplier_id:
			data.append(('partner_id','=',self.supplier_id.id))
		if form_values['state'] != False:
			data.append(('state','=',form_values['state']))
		if form_values['user_id'] != False:
			data.append(('state','=',form_values['user_id']))

		data.append(('create_date','>=',form_values['date_from']))
		data.append(('create_date','<=',form_values['date_to']))
		datas = {
			'ids': [],
			'model': 'line.contract.installment',
			'form_values':data,
			'supplier':form_values['supplier_id'],
			'contract':form_values['contract_ids'],
			'state':form_values['state'],
			'date_from':self.date_from,
			'date_to':self.date_to,			
		}
		return self.env.ref('contract.action_report_details_contract').report_action(self, data=datas)
