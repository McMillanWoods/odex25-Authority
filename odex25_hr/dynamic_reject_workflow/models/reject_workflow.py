# -*- coding: utf-8 -*-

from lxml import etree
import json
from odoo import models, fields, api, _


class RejectWorkflow(models.Model):
    _name = 'reject.workflow'
    _description = 'Reject Workflow'

    name = fields.Char(string='Name')
    model_id = fields.Many2one('ir.model', string='Model Ref.', domain="[('is_mail_thread','=',True)]")
    button_ids = fields.Many2many('reject.button', string="Reject Button")

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.env['reject.button'].search([]).unlink()

    def reject_workflow_buttons(self):
        for rec in self:
            if rec.model_id:
                self.env['reject.button'].search([]).unlink()
                view = self.env[rec.model_id.model].fields_view_get()
                arch = etree.XML(view['arch'])
                for btn in arch.xpath("//form/header/button"):
                    attr = btn.attrib
                    modifiers = json.loads(attr['modifiers'])
                    btn_dict = {
                        'name': attr.get('string'),
                        'button_name': attr.get('name'),
                        'model_id': rec.model_id.id,
                        'invisible': 'invisible' in modifiers and
                                     modifiers['invisible'] or False,
                        'states': 'states' in attr and attr['states'] or False
                    }
                    self.env['reject.button'].create(btn_dict)
        return {
            'name': _('Buttons'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reject.button.wizard',
            'target': 'new',
        }

    def check_reject_workflow(self, model=None):
        button_ids = []
        if model:
            reject_button = self.search([('model_id.model', '=', model)])
            button_ids = [{'name': item.button_name, 'string': item.name,
                           'invisible': item.invisible, 'states': item.states}
                          for item in reject_button.button_ids]
        return button_ids


class RejectButtonWizard(models.TransientModel):
    _name = 'reject.button.wizard'
    _description = 'Reject Button Wizard'

    button_ids = fields.Many2many('reject.button', string="Reject Button")

    def confirm(self):
        active_id = self.env['reject.workflow'].browse(self.env.context.get('active_id'))
        active_id.write({
            "button_ids": [(6, 0, self.button_ids.ids)]
        })


class RejectButton(models.Model):
    _name = 'reject.button'
    _description = 'Reject Button'

    name = fields.Char(string='Button String')
    button_name = fields.Char(string='Button Name')
    invisible = fields.Char(string='Invisible')
    states = fields.Char(string='States')
    model_id = fields.Many2one('ir.model', string='Model Ref.')


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    reason = fields.Text(string='Reason/Justification')

    def action_reject_workflow(self):
        return {
            'name': _('Reject'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reject.wizard',
            'target': 'new',
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, body='', subject=None, message_type='notification',
                     parent_id=False, subtype_xmlid=None, attachments=None, **kwargs):
        context = self.env.context
        if 'merge_reason' in context:
            tracking_value_ids = kwargs['tracking_value_ids']
            tracking_value_ids.append([0, 0, {
                'field': 'reason',
                'field_desc': _(self.env['mail.thread'].fields_get('reason')['reason']['string']),
                'field_type': 'Text',
                'old_value_char': '',
                'new_value_char': self.reason
            }])
        res = super(MailThread, self).message_post(body=body, subject=subject, message_type=message_type,
                                                   subtype_xmlid=subtype_xmlid,
                                                   parent_id=parent_id, attachments=attachments, **kwargs)
        return res
