# Copyright 2020 RGB Consulting
# Copyright 2017-2019 MuK IT GmbH
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Tag(models.Model):
    _name = "dms.tag"
    _description = "Document Tag"

    name = fields.Char(string="Name", required=True, translate=True)
    active = fields.Boolean(
        default=True,
        help="The active field allows you " "to hide the tag without removing it.",
    )
    folder_id = fields.Many2one('dms.directory', string="Workspace", store=True,
                                readonly=False)
    facet_id = fields.Many2one('documents.facet', string="Category", ondelete='cascade', required=True)
    sequence = fields.Integer('Sequence', default=10)
    category_id = fields.Many2one(
        comodel_name="dms.category",
        context="{'dms_category_show_path': True}",
        string="Category",
        ondelete="set null",
    )
    color = fields.Integer(string="Color Index", default=10)
    folder_id = fields.Many2one(
        'dms.directory',
        string='',
        required=False)
    directory_ids = fields.Many2many(
        comodel_name="dms.directory",
        # relation="dms_directory_tag_rel",
        # column1="tid",
        # column2="did",
        # string="Directories",
        # readonly=True,
    )
    file_ids = fields.Many2many(
        comodel_name="documents.document",
        # relation="dms_file_tag_rel",
        # column1="tid",
        # column2="fid",
        # string="Files",
        # readonly=True,
    )
    count_directories = fields.Integer(
        compute="_compute_count_directories", string="Count Directories"
    )
    count_files = fields.Integer(compute="_compute_count_files", string="Count Files")

    _sql_constraints = [
        ("name_uniq", "unique (name, category_id)", "Tag name already exists!"),
    ]

    @api.depends("directory_ids")
    def _compute_count_directories(self):
        for rec in self:
            rec.count_directories = len(rec.directory_ids)

    @api.depends("file_ids")
    def _compute_count_files(self):
        for rec in self:
            rec.count_files = len(rec.file_ids)

    # @api.model
    # def _get_tags(self, domain, folder_id):
    #     """
    #     fetches the tag and facet ids for the document selector (custom left sidebar of the kanban view)
    #     """
    #     documents = self.env['documents.document'].search(domain)
    #     # folders are searched with sudo() so we fetch the tags and facets from all the folder hierarchy (as tags
    #     # and facets are inherited from ancestor folders).
    #     folders = self.env['dms.directory'].sudo().search([('parent_folder_id', 'parent_of', folder_id)])
    #     self.flush(['sequence', 'name', 'facet_id'])
    #     self.env['documents.facet'].flush(['sequence', 'name', 'tooltip'])
    #     query = """
    #             SELECT  facet.sequence AS group_sequence,
    #                     facet.id AS group_id,
    #                     facet.tooltip AS group_tooltip,
    #                     documents_tag.sequence AS sequence,
    #                     documents_tag.id AS id,
    #                     COUNT(rel.documents_document_id) AS __count
    #             FROM documents_tag
    #                 JOIN documents_facet facet ON dms.tag.facet_id = facet.id
    #                     AND facet.folder_id = ANY(%s)
    #                 LEFT JOIN document_tag_rel rel ON dms_tag.id = rel.documents_tag_id
    #                     AND rel.documents_document_id = ANY(%s)
    #             GROUP BY facet.sequence, facet.name, facet.id, facet.tooltip, dms_tag.sequence, documents_tag.name, documents_tag.id
    #             ORDER BY facet.sequence, facet.name, facet.id, facet.tooltip, dms_tag.sequence, documents_tag.name, documents_tag.id
    #         """
    #     params = [
    #         list(folders.ids),
    #         list(documents.ids),  # using Postgresql's ANY() with a list to prevent empty list of documents
    #     ]
    #     self.env.cr.execute(query, params)
    #     result = self.env.cr.dictfetchall()
    #
    #     # Translating result
    #     groups = self.env['documents.facet'].browse({r['group_id'] for r in result})
    #     group_names = {group['id']: group['name'] for group in groups}
    #
    #     tags = self.env['documents.tag'].browse({r['id'] for r in result})
    #     tags_names = {tag['id']: tag['name'] for tag in tags}
    #
    #     for r in result:
    #         r['group_name'] = group_names.get(r['group_id'])
    #         r['display_name'] = tags_names.get(r['id'])
    #
    #     return result
