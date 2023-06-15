from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)


class SupersetUser(models.Model):
    _name = 'superset.users'
    _description = "SupersetUser"

    password = fields.Char()


class ResUser(models.Model):
    _inherit = 'res.users'

    superset_uid = fields.Many2one('superset.users')


class ChangePasswordUser(models.TransientModel):
    """ Change superset password when odoo users change their password. """
    _inherit = 'change.password.user'

    def change_password_button(self):
        params = self.env['ir.config_parameter'].sudo()
        url = params.get_param('superset.bi_url', default=False)
        super_usr = params.get_param('superset.username', default=False)
        super_pwd = params.get_param('superset.password', default=False)

        for line in self:
            s = requests.Session()
            vals = {'password': line.new_passwd}
            if line.user_id.superset_uid:
                r=s.post(url + "login/",
                       data={'username': line.user_id.login, 'password': line.user_id.superset_uid.password})
                _logger.warning("Superuser cann't login to Odex BI '%s' - '%s'",r.url , url)
                # if r.url == url + "login/":
                #     raise ValidationError(_('''User cann't login to Odex BI'''))

                resss=s.post(url + "resetmypassword/form",
                       data={'password': line.new_passwd, 'conf_password': line.new_passwd})
                line.user_id.superset_uid.write({'password': line.new_passwd})
            else:
                r=s.post(url + "login/", data={'username': super_usr, 'password': super_pwd})
                _logger.warning("Superuser cann't login to Odex BI '%s' - '%s'",r.url , url)
                # if r.url == url + "login/":
                #     raise ValidationError(_('''Superuser cann't login to Odex BI 
                #                             Kindly check superuser credential in General Setting'''))

                s.post(url + "users/add", data={'first_name': line.user_id.name, 'last_name': line.user_id.name,
                                                'username': line.user_id.login, 'email': line.user_id.login ,
                                                'active': True, 'password': line.new_passwd, 'conf_password': line.new_passwd})
                superset_uid = self.env['superset.users'].create({'password': line.new_passwd})
                vals.update({'superset_uid':superset_uid.id})
            line.user_id.write(vals)
        # don't keep temporary passwords in the database longer than necessary
        self.write({'new_passwd': False})
