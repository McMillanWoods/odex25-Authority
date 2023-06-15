# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError

class TransportMethodAbstract(models.AbstractModel):
	_name = 'report.contract.detials_contract_report_template'
	_description = 'report.contract.detials_contract_report_template'
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
			lines = self.env['contract.line'].search([('contract_id','=',con.id)])
			state=""
			if data['state']:
				state = status[data['state']]
			state = self.checkLength(state)
			result.append(
				{
					'contract':con,
					'lines':lines,
            		'state':state,
            		'contracts':contracts,
					

				}
			)
		
		docargs={
            'doc_ids':[],
            'doc_model':['line.contract.installment'],
            'docs':result,
        }
		return docargs
         
	def checkLength(self,string):
		if len(string)==0:
			return _("All")
		else:
			return string
        
		
		

	