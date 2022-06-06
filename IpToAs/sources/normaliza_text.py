#!/usr/bin/env python
# -*- coding: utf8 -*-

from unicodedata import normalize

def normalizar_string(unicode_string):
    u"""Retorna unicode_string normalizado para efectuar una búsqueda.

    >>> normalizar_string(u'Mónica Viñao')
    'monica vinao'
    
    """
    return normalize('NFKD', unicode_string).encode('ASCII', 'ignore').lower()

if __name__ == "__main__":
    texto = 'ñandú'.decode('utf8')
    
   # textunicode = text.decode('utf8')
    print type(texto), texto
    print normalizar_string(texto)
