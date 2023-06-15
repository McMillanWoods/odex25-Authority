import logging

from odoo import _
from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class Settings(models.Model):
    _name = 'dms.settings'
    _description = "MuK Documents Settings"
    # _inherit = 'dms.model'

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    name = fields.Char(
        string="Name",
        required=True)

    save_type = fields.Selection(
        selection=[("database", _('Database'))],
        string="Save Type",
        default="database",
        required=True,
        help="The save type is used to determine how a file is saved to the system.")

    system_locks = fields.Boolean(
        string="System Locks",
        default=True,
        help="Indicates if files and directories should be automatically locked while system operations take place.")

    show_tree = fields.Boolean(
        string="Show Structure",
        default=True,
        help="Indicates if directories inside of this settings object are visible on document views.")

    settings_directories = fields.One2many(
        comodel_name='dms.directory',
        inverse_name='settings',
        string="Directories",
        copy=False,
        readonly=True)

    settings_files = fields.One2many(
        comodel_name='dms.file',
        inverse_name='settings',
        string="Files",
        copy=False,
        readonly=True)

    count_settings_directories = fields.Integer(
        # compute='_compute_count_settings_directories',
        string="Directories")

    count_settings_files = fields.Integer(
        compute='_compute_count_settings_files',
        string="Files")

    root_directories = fields.One2many(
        comodel_name='dms.directory',
        inverse_name='settings',
        string="Root Directories",
        domain=[['is_root_directory', '=', True]])

    top_directories = fields.One2many(
        comodel_name='dms.directory',
        inverse_name='settings',
        # compute='_compute_top_directories',
        search='_search_top_directories',
        string="Top Directories",
        help="Directories which have no parent or the user has no access right to those parents.")

    top_files = fields.One2many(
        comodel_name='dms.file',
        string="Top Files",
        compute='_compute_top_files',
        search='_search_top_files',
        help="Files which parent aren't readable by the user.")

    # ----------------------------------------------------------
    # Functions
    # ----------------------------------------------------------

    def notify_change(self, values, *largs, **kwargs):
        super(Settings, self).notify_change(values, *largs, **kwargs)
        for record in self:
            directories = record.root_directories
            operation = directories.generate_operation_key()
            if record.system_locks:
                directories.lock_tree(operation=operation, refresh=True)
            for directory in directories:
                directory.with_context(operation=operation).notify_change(values)
            if record.system_locks:
                directories.unlock_operation(operation=operation, refresh=True)

    # ----------------------------------------------------------
    # Search
    # ----------------------------------------------------------

    @api.model
    def _search_top_directories(self, operator, operand):
        directories = self.env['dms.directory'].search([('name', operator, operand)])
        directories = directories.filtered(
            lambda d: d.is_root_directory or
                      not d.parent_directory.check_access('read'))
        return [('id', 'in', directories.mapped('settings.id'))]

    @api.model
    def _search_top_files(self, operator, operand):
        files = self.env['dms.file'].search([('name', operator, operand)])
        files = files.filtered(lambda f: not f.directory.check_access('read'))
        return [('id', 'in', files.mapped('settings.id'))]

    # ----------------------------------------------------------
    # Read, View 
    # ----------------------------------------------------------

    # @api.depends('settings_directories')
    # def _compute_count_settings_directories(self):
    #     for record in self:
    #         record.count_settings_directories = len(record.settings_directories)
    #
    @api.depends('settings_files')
    def _compute_count_settings_files(self):
        for record in self:
            record.count_settings_files = len(record.settings_files)

    # @api.depends('settings_directories')
    # def _compute_top_directories(self):
    #     for record in self:
    #         # access_ids = self.env['dms.directory']._get_complete_access_ids("read")
    #         access_ids = self.env['dms.directory']
    #         record.top_directories = record.settings_directories.filtered(
    #             lambda d: d.is_root_directory or not d.parent_directory.id in access_ids)

    @api.depends('settings_files')
    def _compute_top_files(self):
        for record in self:
            # access_ids = self.env['dms.directory']._get_complete_access_ids("read")
            access_ids = self.env['dms.directory']
            record.top_files = record.settings_files.filtered(lambda f: not f.directory.id in access_ids)

    # ----------------------------------------------------------
    # Create, Update, Delete
    # ----------------------------------------------------------

    @api.onchange('save_type')
    def _onchange_save_type(self):
        if self._origin.id:
            warning = {
                'title': (_('Information')),
                'message': (_('Changing the save settings can cause a heavy migration process.'))
            }
            return {'warning': warning}

    def _check_notification(self, vals, *largs, **kwargs):
        if 'save_type' in vals:
            self.suspend_security().notify_change({'save_type': vals['save_type']})
