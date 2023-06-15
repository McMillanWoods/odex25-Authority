#-*- coding: utf-8 -*-
from . import barcode
from .barcode import writer


def generator(code):
    return barcode.get('ean13', code).render()

def generator128(code):
    ean = barcode.get('code128', code, writer.SVGWriter())
    return ean.render({})
