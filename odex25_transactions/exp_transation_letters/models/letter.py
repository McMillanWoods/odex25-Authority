# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models


class Letters(models.Model):
    _name = "letters.letters"

    name = fields.Char(string="Name")
    unite = fields.Many2one('cm.entity', string="Unite")
    letter_template = fields.Many2one('letters.template', string='Template')
    date = fields.Date(string="Date")
    hijir_date = fields.Char(string="Hijir Date", compute='compute_hijri')
    content = fields.Html(string="Content")
    signature = fields.Binary("Signature image")
    transaction_type = fields.Selection([('internal', 'Internal'), ('outgoing', 'Outgoing'),
                                         ('incoming', 'Incoming')], default='internal', string='Transaction Type')
    incoming_transaction_id = fields.Many2one(comodel_name='incoming.transaction', string='Incoming Transaction')
    internal_transaction_id = fields.Many2one(comodel_name='internal.transaction', string='Internal Transaction')
    outgoing_transaction_id = fields.Many2one(comodel_name='outgoing.transaction', string='Outgoing Transaction')

    @api.onchange('transaction_type')
    def set_value_false(self):
        if self.transaction_type == 'internal':
            self.incoming_transaction_id = ''
            self.outgoing_transaction_id = ''
        elif self.transaction_type == 'outgoing':
            self.incoming_transaction_id = ''
            self.internal_transaction_id = ''
        elif self.transaction_type == 'incoming':
            self.internal_transaction_id = ''
            self.outgoing_transaction_id = ''
        elif not self.transaction_type:
            self.incoming_transaction_id = ''
            self.internal_transaction_id = ''
            self.outgoing_transaction_id = ''

    @api.depends('date')
    def compute_hijri(self):
        '''
        method for compute hijir date depend on date using odex hijri
        '''
        H = self.env['odex.hijri']
        for r in self:
            r.hijir_date = r.date and H.convert(r.date) or ''

    @api.onchange('letter_template')
    def get_content(self):
        for rec in self:
            final_content = rec.letter_template.introduction+rec.letter_template.content+rec.letter_template.conclusion
            if final_content:
                final_content = final_content.replace('line-height', '')
                rec.content = final_content

    
    def action_generate_attachment(self):
        """ this method called from button action in view xml """
        # generate pdf from report, use report's id as reference
        REPORT_ID = 'exp_transation_letters.report_letter_action_report'
        pdf = self.env.ref(REPORT_ID)._render_qweb_pdf(self.ids)
        # pdf result is a list
        b64_pdf = base64.b64encode(pdf[0])
        res_model = ''
        res_id = ''
        if self.transaction_type == 'internal':
            transaction = self.env['internal.transaction']
            res_model = transaction._name
            res_id = self.internal_transaction_id.id
        elif self.transaction_type == "outgoing":
            transaction = self.env['outgoing.transaction']
            res_model = transaction._name
            res_id = self.outgoing_transaction_id.id
        elif self.transaction_type == "incoming":
            transaction = self.env['incoming.transaction']
            res_model = transaction._name
            res_id = self.incoming_transaction_id.id
        # save pdf as attachment
        ATTACHMENT_NAME = "Letter"
        return self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME + '.pdf',
            'type': 'binary',
            'datas': b64_pdf,
            # 'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': res_model,
            'res_id': res_id,
            'mimetype': 'application/x-pdf'
        })

    
    def write(self, values):
        if values.get('content'):
            final_content = values.get('content')
            values['content'] = final_content.replace('line-height', '')
        return super(Letters, self).write(values)


class LettersTemp(models.Model):
    _name = "letters.template"

    name = fields.Char(string="Name")
    unite = fields.Many2one('cm.entity', string="Unite")
    introduction = fields.Html(string='Introduction')
    conclusion = fields.Html(string="Conclusion")
    content = fields.Html(string="Content")
    is_favorite = fields.Selection([
        ('0', 'not'),
        ('1', 'Favorite'),
    ], size=1, string="Favorite")


