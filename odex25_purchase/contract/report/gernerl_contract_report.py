# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError

class TransportMethodAbstract(models.AbstractModel):
	_name = 'report.contract.general_contract_report_template'
	_description = 'report.contract.general_contract_report_template'
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
			
			total_amount = sum(rec['with_tax_amount'] for rec in contracts)
			
			state=""
			if data['state']:
				state = status[data['state']]
			state = self.checkLength(state)
			
		
		docargs={
            'doc_ids':[],
            'doc_model':['contract.contract'],
            'docs':contracts,
            'state':state,
            'total_amount':total_amount,
			'date_from':data['date_from'],
            'date_to':data['date_to'],
            'report_type':data['report_type'],
        }
		return docargs
         
	def checkLength(self,string):
		if len(string)==0:
			return _("All")
		else:
			return string
        
		

	