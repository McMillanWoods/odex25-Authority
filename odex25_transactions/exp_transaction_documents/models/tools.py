#-*- coding: utf-8 -*-

from ..tools import generator, generator128
from random import shuffle
import re
from odoo import models

SHUFFLE = [str(y) for y in ([x for x in range(10)] + [1,2,3])]


class Barcode(models.TransientModel):
    '''
    Generate EAN13 Barcode
    '''
    _name = 'odex.barcode'

    def generate(self, code):
        '''
            Generate Ean13 code
        '''
        return generator128(code)


    def ean13(self):
        shuffle(SHUFFLE)
        return ''.join(SHUFFLE)

    def code128(self, starter, code, ender):
        x = re.sub(r'[^\d]', '', code)
        if len(x) < 9:
            shuffle(SHUFFLE)
            y = SHUFFLE[:9-len(x)]
            x = u'{}{}'.format(x, y)
        if len(x) > 9:
            x = x[:9]
        return u'{}{}{}'.format(starter, x, ender)

    def to_arabic_indic(self, txt):
        txt = unicode(txt)
        TXTAR = u''.join([str(x) for x in range(10)]+['-'])
        TXT = u'٠١٢٣٤٥٦٧٨٩/'
        K = {x: y for x, y in zip(TXTAR, TXT)}
        for k, v in K.items():
            txt = txt.replace(k, v)
        return txt
