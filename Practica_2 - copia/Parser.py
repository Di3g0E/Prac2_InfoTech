# coding: utf-8

from Lexer import CoolLexer
from sly import Parser
import sys
import os
from Clases import *


class CoolParser(Parser):
    nombre_fichero = ''
    tokens = CoolLexer.tokens
    debugfile = "salida.out"
    errores = []

    #@_("CLASS OBJECTID")
    #def Programa(self, p):
    #    pass


    @_('clases')
    def Programa(self, p):
        return Programa(secuencia=p.clases)

    @_('clase', 'clases clase')
    def clases(self, p):
        if len(p) == 2:
            return p.clases+[p.clase]
        else:
            return [p.clase]

    @_('CLASS TYPEID "{" atributos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre="OBJECT", nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)

    #@_('expresion"()" ":" expresion')
    #def method(self, p):
    #    return Metodo(formales=p.expresion)

    #@_('atributo ":" tipo object ";"')
    #def let(self, p):
    #    return Let(nombre=p.atributo, tipo=p.tipo, inicializacion=':', cuerpo=p.object)

    @_("atributos atributo") # Esta función y la siguiente es lo mismo que un 'or' aunque también se pueden separar por ','
    def atributos(self, p):
        return p.atributos+[p.atributo]

    @_(" ")
    def atributos(self, p):
        return []

    @_("OBJECTID ':' TYPEID ';'")
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())

    #@_('in objeto "}"";"')
    #def objeto(self, p):
    #    return Objeto(nombre=p.objeto)