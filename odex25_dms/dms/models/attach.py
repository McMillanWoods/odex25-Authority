from odoo import _, api, fields, models, tools


class FileAttach(models.Model):
    _name = "dms.file.attach"
    _description = "File"

    file_project_ids = fields.One2many(
        comodel_name='documents.document',
        inverse_name='project_id',
        compute="_compute_project_field",
        string='',
        required=False)

    file_transaction_ids = fields.One2many(
        comodel_name='documents.document',
        inverse_name='attach_id',
        string='',
        required=False)

    def _compute_project_field(self):
        print("******************")
        related_recordset = self.env["documents.document"].search([])
        self.file_project_ids = ()
        s_list = []
        value = {}
        for val in self:
            User_input = related_recordset.search([])
            for rec in User_input:
                data = {
                    'file_code': rec.file_code,
                    'write_date': rec.write_date,
                    'create_uid': rec.create_uid,
                }
                print(data)
                s_list.append((0, 0, data))
            self.file_project_ids = s_list
            print(self.file_project_ids)
