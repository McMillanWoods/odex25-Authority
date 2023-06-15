# -*- coding: utf-8 -*-

# import sys
#
# # reload(sys)
# # sys.setdefaultencoding("utf-8")
import base64
import os
from odoo.exceptions import ValidationError

# import barcode as barcode
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from pathlib import Path
from odoo.modules.module import get_module_resource


from lxml import etree

import arabic_reshaper
from bidi.algorithm import get_display
from odoo import models, api, fields
from odoo.tools.translate import _


# from odoo.osv.orm import setup_modifiers


class Transaction(models.Model):
    _inherit = 'transaction.transaction'

    binary_barcode = fields.Binary(string='Barcode', attachment=True)

    @api.constrains('ean13', 'name', 'transaction_date', 'type')
    def binary_compute_constraint(self):
        fonts = [os.path.dirname(__file__) + '/img/KacstOffice.ttf',
                 os.path.dirname(__file__) + '/img/amiri-regular.ttf']
        img = Image.new("RGBA", (500, 420), "white")
        draw = ImageDraw.Draw(img)
        number_word = "الرقم : "
        number_word_reshaped = arabic_reshaper.reshape(
            u'' + number_word)
        number_word_artext = get_display(number_word_reshaped)
        draw.text((220, 20),
                  number_word_artext, "black",
                  font=ImageFont.truetype(fonts[1], 18))

        number_value = self.name
        number_value_reshaped = arabic_reshaper.reshape(
            u'' + number_value if number_value else '')
        number_value_artext = get_display(number_value_reshaped)
        draw.text((80, 20),
                  number_value_artext, "black",
                  font=ImageFont.truetype(fonts[1], 18))
        #
        date_hijri = "التاريخ : "
        date_hijri_reshaped = arabic_reshaper.reshape(
            u'' + date_hijri)
        date_hijri_artext = get_display(date_hijri_reshaped)
        draw.text((211, 40),
                  date_hijri_artext, "black",
                  font=ImageFont.truetype(fonts[1], 18))

        date_hijri_value = self.transaction_date_hijri
        date_hijri_value_reshaped = arabic_reshaper.reshape(
            u'' + date_hijri_value if date_hijri_value else '')
        date_hijri_artext = get_display(date_hijri_value_reshaped)
        draw.text((120, 40),
                  date_hijri_artext.replace('-', '/'), "black",
                  font=ImageFont.truetype(fonts[1], 18))

        date_m = "الموافق : "
        date_m_reshaped = arabic_reshaper.reshape(
            u'' + date_m)
        date_m_artext = get_display(date_m_reshaped)
        draw.text((210, 65),
                  date_m_artext, "black",
                  font=ImageFont.truetype(fonts[1], 18))

        date_m_value = self.transaction_date
        date_m_value_reshaped = arabic_reshaper.reshape(
            u'' + str(date_m_value) if date_m_value else '')
        date_m_value_artext = get_display(date_m_value_reshaped)
        draw.text((120, 65),
                  date_m_value_artext.replace('-', '/'), "black",
                  font=ImageFont.truetype(fonts[1], 18))

        attach_m = "المرفقات : "
        attach_m_reshaped = arabic_reshaper.reshape(
            u'' + attach_m)
        date_m_artext = get_display(attach_m_reshaped)
        draw.text((200, 85),
                  date_m_artext, "black",
                  font=ImageFont.truetype(fonts[1], 18))

        attach_m_value = str(self.attachment_num) if self.attachment_num else '0'
        attach_m_value_reshaped = arabic_reshaper.reshape(
            u'' + attach_m_value)
        attach_mvalue_artext = get_display(attach_m_value_reshaped)
        draw.text((180, 85),
                  attach_mvalue_artext, "black",
                  font=ImageFont.truetype(fonts[1], 18))
        # barcode_symbology = options.get('symbology', 'Code128')
        barcode = self.env['ir.actions.report'].barcode('Code11', self.name, width=250, height=100,
                                                        humanreadable=0)

     

        barcode_buffer = BytesIO(barcode)
        barcode_image_file = Image.open(barcode_buffer)
        ImageDraw.Draw(img)
        buffered = BytesIO()
        img.paste(barcode_image_file, (20, 110))
        img.save(buffered, format="png")
        img_str = base64.b64encode(buffered.getvalue())
        self.binary_barcode = img_str


class AttachmentInherit(models.Model):
    _inherit = 'ir.attachment'

    @api.constrains('vals_list')
    def create(self, vals_list):
        print("***********")
        res = super(AttachmentInherit, self).create(vals_list)
        print(res.mimetype)
        if res.mimetype == 'text/html':
            raise ValidationError(_('You cannot inset a html File'))

        return res
