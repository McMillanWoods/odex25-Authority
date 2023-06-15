# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    folder_id = fields.Many2one('dms.directory',
                                       string="Floder Workspace",
                                       ondelete="cascade",
                                       help="A workspace Folder to store all project documents.")

    @api.model_create_multi
    def create(self, vals_list):
        """
        Add folder_id from model to ir.attachment if exist in model
        """
        for values in vals_list:
            
            if values.get('res_model'):
                model = self.env[values['res_model']]
                if model._fields.get('folder_id'):
                    folder_id = self.env[values['res_model']].browse(values['res_id']).folder_id
                    values['folder_id'] = folder_id.id
        return super(IrAttachment, self).create(vals_list)
