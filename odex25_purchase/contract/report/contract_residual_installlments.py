from odoo import models, fields, api,_
class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.contract.contract_residual_installlments'
    _description = 'report.contract.contract_residual_installlments'

    @api.model
    def _get_report_values(self, docids, data=None):
        installment_data = []
        payment = 0.0
        docs = self.env['contract.contract'].browse(docids)
        instalments = self.env['line.contract.installment'].search([('contract_id','in',docs.ids)], order='due_date asc')
        for instalment in instalments:
            if instalment.invoice_id:
                invoices = self.env['account.move'].search([('id','=',instalment.invoice_id.id)])
                contract_id = instalment.contract_id
                for inv in invoices:
                    if inv.state != 'paid':
                        payment = inv.amount_total - contract_id.remaining_amount
                    else:
                        inv_payment = contract_id._get_related_payment()
                        for p in inv_payment:
                            payment += p.amount
            else:
                payments = self.env['account.payment'].search([('id','=',instalment.payment_id.id)])
                for p in payments:
                    payment += p.amount

            installment_data.append({
                    'contract':instalment.contract_id.id,
                    'name':instalment.name,
                    'due_date':instalment.due_date,
                    'total_amount':instalment.total_amount,
                    'residual':instalment.total_amount - payment,   
                })
            
       
        return {
            'doc_ids': self.ids,
            'docs': docs,
            'installment_data':installment_data
           
        }