# -*- coding: utf-8 -*-
import requests
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ResCompanySMS(models.Model):
    _inherit = "res.company"
    _description = "Res Company SMS Configuration"

    # Company Level SMS Configuration Fields
    sms_active = fields.Boolean()
    user_name = fields.Char("User Name")
    password = fields.Char("Password")
    user_send = fields.Char("Sender")
    api_sms = fields.Char("API")
    api_unicode = fields.Char("Unicode")

    @api.model
    def send_sms(self, number, message):
        """
            This method is used to send odex_sms
        """
        if self.user_name and self.password and number:
            url = self.api_sms + "?user=" + self.user_name + "&pass=" + self.password + "&to=" + number + "&message=" + message + "&sender=" + self.user_send + "&unicode=" + self.api_unicode
            headers = {'Accept-Encoding': 'identity'}
            try:
                response = requests.get(url, headers=headers)
            except:
                print("Oops! Something wrong")
            request = response.text[:100].split("-")
            print("*****", request[1])
            error = self.get_error_response(str(request[1]))
            print(error)
            print(response)
            print("SMS Successfully Sent")

            return response

    def get_error_response(self, result):
        print(result)
        if result == "100":
            raise ValidationError(_("SMS : Missing parameters (not exist or empty) Username And password"))
        if result == "110":
            raise ValidationError(_("SMS :Account not exist (wrong username or password)"))
        if result == "111":
            raise ValidationError(_("SMS : The account not activated."))
        if result == "112":
            raise ValidationError(_("SMS : Blocked account."))
        if result == "113":
            raise ValidationError(_("SMS : Not enough balance."))
        if result == "114":
            raise ValidationError(_("SMS : The service not available for now"))
        if result == "115":
            raise ValidationError(_("SMS : The sender not available (if user have no opened sender)"))
        if result == "116":
            raise ValidationError(_("SMS : The sender not available (if user have no opened sender)"))
        if result == "120":
            raise ValidationError(_("SMS : No destination addresses, or all destinations are not correct)"))
