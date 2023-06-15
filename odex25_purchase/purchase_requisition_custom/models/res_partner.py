from odoo import api, fields, models, _
from datetime import datetime
from datetime import timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    documents_ids = fields.One2many("partner.document","partner_id",string="Partner Documents")
    # attachment_ids = fields.Many2many("ir.attachment",string="Attachment")

    # New Feature
    def send_notification_message(self, subject, body, author_id=None, group=None):
        """Send notification"""
        if group:
            partner_ids = self.env.ref(group).users.mapped('partner_id').ids
            # print('group', partner_ids)
            # partner_ids = self.env['res.partner'].search([('id', 'in', users)]).mapped('id')
        else:
            partner_ids = [self.id]

        if partner_ids:
            try:
                self.message_post(type="notification", subject=subject, body=body, author_id=author_id,
                     partner_ids=partner_ids,
                     subtype_xmlid="mail.mt_comment")
            except Exception as e:
                pass


class PartnerDocuments(models.Model):
    _name = 'partner.document'
    _description = 'Partner Document'

    partner_id = fields.Many2one('res.partner','Partner')
    
    name = fields.Char(string='Name')
    attachment = fields.Binary(string='Attachment')
    
    type_id = fields.Many2one(
        string='Type',
        comodel_name='document.type',
    )

    exp_date = fields.Date(string='Expiration Date')

    def cron_document_experation(self):
        date_now = (datetime.now() + timedelta(days=1)).date()
        documents = self.search([])
        for i in documents:
            if i.exp_date:
                exp_date = fields.Date.from_string(i.exp_date) - timedelta(days=30)
                if date_now >= exp_date:
                    # Send Notifications
                    subject = _('Document Expiration') + '- {} / {}'.format(i.name, i.exp_date)
                    message = _('Hello, This is  a notice about the end date of the document.') + '\n' + _('Name of document: ') + '{}'.format(i.name) + '\n' + _('Expiration Date: ') + '{}'.format(i.exp_date) + '\n' + _('Partner Name: ') + '{}'.format(i.partner_id.name)
                    group = 'purchase.group_purchase_manager'
                    author_id = None #i.create_uid.partner_id.id or None
                    i.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id, group=group)


class PartnerDocuments(models.Model):
    _name = 'document.type'
    _description = 'Partner Document Type'
     
    name = fields.Char(
         string='Name',
         translate=True
         
     )
     