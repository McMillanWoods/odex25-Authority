# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64
import io
import os

from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo import models, api
from PyPDF2 import PdfFileWriter, PdfFileReader


# class IrAttachment(models.Model):
#     _inherit = "ir.attachment"
#
#     @api.model
#     def _pdf_split(self, new_files=None, open_files=None):
#         """Creates and returns new pdf attachments based on existing data.
#
#         :param new_files: the array that represents the new pdf structure:
#             [{
#                 'name': 'New File Name',
#                 'new_pages': [{
#                     'old_file_index': 7,
#                     'old_page_number': 5,
#                 }],
#             }]
#         :param open_files: array of open file objects.
#         :returns: the new PDF attachments
#         """
#         vals_list = []
#         pdf_from_files = [PdfFileReader(open_file, strict=False) for open_file in open_files]
#         for new_file in new_files:
#             output = PdfFileWriter()
#             for page in new_file['new_pages']:
#                 input_pdf = pdf_from_files[int(page['old_file_index'])]
#                 page_index = page['old_page_number'] - 1
#                 output.addPage(input_pdf.getPage(page_index))
#             with io.BytesIO() as stream:
#                 output.write(stream)
#                 vals_list.append({
#                     'name': new_file['name'] + ".pdf",
#                     'datas': base64.b64encode(stream.getvalue()),
#                 })
#         return self.create(vals_list)
#
#     def _create_document(self, vals):
#         """
#         Implemented by bridge modules that create new documents if attachments are linked to
#         their business models.
#
#         :param vals: the create/write dictionary of ir attachment
#         :return True if new documents are created
#         """
#         # Special case for documents
#         if vals.get('res_model') == 'documents.document' and vals.get('res_id'):
#             document = self.env['documents.document'].browse(vals['res_id'])
#             if document.exists() and not document.attachment_id:
#                 document.attachment_id = self[0].id
#             return False
#
#         # Generic case for all other models
#         res_model = vals.get('res_model')
#         res_id = vals.get('res_id')
#         model = self.env.get(res_model)
#         if model is not None and res_id and issubclass(type(model), self.pool['documents.mixin']):
#             vals_list = [
#                 model.browse(res_id)._get_document_vals(attachment)
#                 for attachment in self
#                 if not attachment.res_field
#             ]
#             vals_list = [vals for vals in vals_list if vals]  # Remove empty values
#             self.env['documents.document'].create(vals_list)
#             return True
#         return False
#
#     def _get_dms_directories(self, res_model, res_id):
#         domain = [
#             ("res_model", "=", res_model),
#             ("res_id", "=", res_id),
#             ("storage_id.save_type", "=", "attachment"),
#         ]
#         if self.env.context.get("attaching_to_record"):
#             domain += [("storage_id.include_message_attachments", "=", True)]
#         return self.env["dms.directory"].search(domain)
#
#     def _dms_directories_create(self):
#         items = self.sudo()._get_dms_directories(self.res_model, False)
#         for item in items:
#             model_item = self.env[self.res_model].browse(self.res_id)
#             ir_model_item = self.env["ir.model"].search(
#                 [("model", "=", self.res_model)]
#             )
#             self.env["dms.directory"].sudo().with_context(check_name=False).create(
#                 {
#                     "name": model_item.display_name,
#                     "model_id": ir_model_item.id,
#                     "res_model": self.res_model,
#                     "res_id": self.res_id,
#                     "parent_id": item.id,
#                     "storage_id": item.storage_id.id,
#                 }
#             )
#
#     def _dms_operations(self):
#         for attachment in self:
#             print(attachment,"__________________________")
#             if not attachment.res_model or not attachment.res_id:
#                 continue
#             directories = attachment._get_dms_directories(
#                 attachment.res_model, attachment.res_id
#             )
#             if not directories:
#                 attachment._dms_directories_create()
#                 # Get dms_directories again (with items previously created)
#                 directories = attachment._get_dms_directories(
#                     attachment.res_model, attachment.res_id
#                 )
#             # Auto-create_files (if not exists)
#             for directory in directories:
#                 dms_file_model = self.env["documents.document"].sudo()
#                 dms_file = dms_file_model.search(
#                     [
#                         ("attachment_id", "=", attachment.id),
#                         ("directory_id", "=", directory.id),
#                     ]
#                 )
#                 if not dms_file:
#                     dms_file_model.create(
#                         {
#                             "name": attachment.name,
#                             "directory_id": directory.id,
#                             "attachment_id": attachment.id,
#                             "res_model": attachment.res_model,
#                             "res_id": attachment.res_id,
#                         }
#                     )
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         records = super().create(vals_list)
#         if not self.env.context.get("dms_file"):
#             records._dms_operations()
#         return records
#
#     def write(self, vals):
#         res = super().write(vals)
#         if not self.env.context.get("dms_file") and self.env.context.get(
#                 "attaching_to_record"
#         ):
#             self._dms_operations()
#         return res


class IrAttachment2(models.Model):
    _inherit = ['ir.attachment']

    @api.model
    def _pdf_split(self, new_files=None, open_files=None):
        """Creates and returns new pdf attachments based on existing data.

        :param new_files: the array that represents the new pdf structure:
            [{
                'name': 'New File Name',
                'new_pages': [{
                    'old_file_index': 7,
                    'old_page_number': 5,
                }],
            }]
        :param open_files: array of open file objects.
        :returns: the new PDF attachments
        """
        vals_list = []
        pdf_from_files = [PdfFileReader(open_file, strict=False) for open_file in open_files]
        for new_file in new_files:
            output = PdfFileWriter()
            for page in new_file['new_pages']:
                input_pdf = pdf_from_files[int(page['old_file_index'])]
                page_index = page['old_page_number'] - 1
                output.addPage(input_pdf.getPage(page_index))
            with io.BytesIO() as stream:
                output.write(stream)
                vals_list.append({
                    'name': new_file['name'] + ".pdf",
                    'datas': base64.b64encode(stream.getvalue()),
                })
        return self.create(vals_list)

    def _create_document(self, vals):
        """
        Implemented by bridge modules that create new documents if attachments are linked to
        their business models.

        :param vals: the create/write dictionary of ir attachment
        :return True if new documents are created
        """
        # Special case for documents
        if vals.get('res_model') == 'documents.document' and vals.get('res_id'):
            document = self.env['documents.document'].browse(vals['res_id'])
            if document.exists() and not document.attachment_id:
                document.attachment_id = self[0].id
            return False

        # Generic case for all other models
        res_model = vals.get('res_model')
        res_id = vals.get('res_id')
        model = self.env.get(res_model)
        if model is not None and res_id and issubclass(type(model), self.pool['documents.mixin']):
            vals_list = [
                model.browse(res_id)._get_document_vals(attachment)
                for attachment in self
                if not attachment.res_field
            ]
            vals_list = [vals for vals in vals_list if vals]  # Remove empty values
            self.env['documents.document'].create(vals_list)
            return True
        return False

    @api.model
    # def create(self, vals):
    #     attachment = super(IrAttachment2, self).create(vals)
    #     print("😀😀😀😀😀😀😀😀😀😀😀")
    #     extension = os.path.splitext(attachment['name'])[1]
    #     # print(extension)
    #     # if vals['mimetype'] == 'image/png':
    #     #     raise ValidationError(
    #     #         _("😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀"))
    #
    #     # print(vals)
    #     # the context can indicate that this new attachment is created from documents, and therefore
    #     # doesn't need a new document to contain it.
    #     if not self._context.get('no_document') and not attachment.res_field:
    #         attachment.sudo()._create_document(dict(vals, res_model=attachment.res_model, res_id=attachment.res_id))
    #     return attachment

    def write(self, vals):
        if not self._context.get('no_document'):
            self.filtered(lambda a: not (vals.get('res_field') or a.res_field)).sudo()._create_document(vals)
        return super(IrAttachment2, self).write(vals)
