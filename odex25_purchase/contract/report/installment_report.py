# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError

class TransportMethodAbstract(models.AbstractModel):
	_name = 'report.contract.installments_report_template'
	_description = 'report.contract.installments_report_template'
	@api.model
	def _get_report_values(self,docids, data):
		search = []
	
		status = {
			'new':_('New'),
			'to_confirm':_('To Confirm'),
			'confirmed':_('Confirmed'),
			'in_progress':_('in_progress'),	
			'suspended':_('Suspended'),
			'closed':_('Closed'),
			'cancel':_('Cancel'),
        }
		
		for rec in data['form_values']:
			search.append(tuple(rec))
		contracts = self.env['contract.contract'].search(search)
		
		
		if len(contracts) == 0:
			raise ValidationError(_("There is no data"))
		result = []
		for con in contracts:
			installments = self.env['line.contract.installment'].search([('contract_id','=',con.id)])
			
			total_amount = sum(rec['amount'] for rec in installments)
			total_amount_tax = sum(rec['total_amount'] for rec in installments)
			tax_amount = sum(rec['tax_amount'] for rec in installments)
			suppliers = con.partner_id.name +" "
			contracts =con.name +" "
			contracts = self.checkLength(contracts)
			suppliers = self.checkLength(suppliers)
			state=""
			if data['state']:
				state = status[data['state']]
			state = self.checkLength(state)
			result.append(
				{
					'contract':con,
					'installments':installments,
					'suppliers':suppliers,
            		'state':state,
            		'contracts':contracts,
            		'total_amount':total_amount,
					'total_amount_tax':total_amount_tax,
					'tax_amount':tax_amount,
					'date_from':data['date_from'],
            		'date_to':data['date_to'],

				}
			)
		docargs={
            'doc_ids':[],
            'doc_model':['line.contract.installment'],
            'docs':docids,
			'result':result,
        }
		return docargs
         
	def checkLength(self,string):
		if len(string)==0:
			return _("All")
		else:
			return string
        
		
		

	