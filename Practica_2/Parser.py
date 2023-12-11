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


    @_('clases')
    def Programa(self, p):
        return Programa(secuencia=p.clases)


    @_('clase', 'clases clase')
    def clases(self, p):
        if len(p) == 2:
            return p.clases+[p.clase]
        else:
            return [p.clase]


    @_('CLASS TYPEID "{" atributos "}" ";"', 'CLASS TYPEID "{" metodos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre="OBJECT", nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)


    @_("atributos atributo") # Esta función y la siguiente es lo mismo que un 'or' aunque también se pueden separar por ','
    def atributos(self, p):
        return p.atributos+[p.atributo]


    @_(" ")
    def atributos(self, p):
        return []


    @_("OBJECTID ':' TYPEID ';'")
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())


    @_('metodos metodo')
    def metodos(self, p):
        return p.metodos+[p.metodo]

    @_(' ')
    def metodos(self, p):
        return []


    @_('OBJECTID "(" ")" ":" TYPEID "{" expresiones "}" ";"', 'OBJECTID "(" formales "," formales ")" ":" TYPEID "{" expresiones "}" ')
    def metodo(self, p):
        return Metodo(formales=p.formales)


    @_('formales formal')
    def formales(self, p):
        return p.formales+[p.formal]


    @_(' ')
    def formales(self, p):
        return []


    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID)


    @_("expresiones expresion")
    def expresiones(self, p):
        return p.expresiones + [p.expresion]


    @_("expresion")
    def expresiones(self, p):
        return p.expresion


    @_("OBJECTID ASSIGN",
       "expresion '+' expresion",
       "expresion '-' expresion",
       "expresion '*' expresion",
       "expresion '/' expresion",
       "expresion '<' expresion",
       "expresion LE expresion",
       "expresion '=' expresion",
       "'(' expresion ')'",
       "NOT expresion",
       "ISVOID expresion",
       "'~' expresion",
       "expresion '@' TYPEID '.' OBJECTID '(' ')'",
       "expresion '@' TYPEID '.' OBJECTID '(' expresiones ',' expresion ')'",
       "expresion '.' OBJECTID '(' expresiones ',' expresion ')' expresion",
       "OBJECTID '(' expresion ',' expresion ')' expresion",
       "expresion '.' OBJECTID '(' ')'",
       "OBJECTID '(' ')'",
       "IF expresion THEN expresion ELSE expresion FI",
       "WHILE expresion LOOP expresion  POOL",
       "LET OBJECTID ':' TYPEID ASSIGN expresion ',' OBJECTID ':' TYPEID ASSIGN expresiones IN expresion",
       "CASE expresion OF '(' OBJECTID ':' TYPEID DARROW expresiones ')' ';' ESAC",
       "NEW TYPEID",
       "'{' expresiones ';' '}'",
       "INT_CONST",
       "STR_CONST",
       "BOOL_CONST",
       "expresion expresion")
    def expresion(self, p):
        pass #return Expresion(cast=p.ASSING)


    @_("NOT")
    def negacion(self, p):
        return Not(expr=p, operator="NOT")






    #@_('atributo ":" tipo OBK ";"')
    #def let(self, p):
    #    pass #    return Let(nombre=p.atributo, tipo=p.tipo, inicializacion=':', cuerpo=p.object)

    #@_('in objeto "}"";"')
    #def objeto(self, p):
    #    return Objeto(nombre=p.objeto)