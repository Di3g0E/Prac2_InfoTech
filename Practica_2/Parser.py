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
    precedence = (
        ('nonassoc', '.'),
        ('nonassoc', '@'),
        ('left', ISVOID, '*', '/', '+', '-'),
        ('nonassoc', LE, '<', '=', NOT),
        ('right', ASSIGN)
    )



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

    @_('CLASS TYPEID INHERITS TYPEID "{" atributos "}" ";"', 'CLASS TYPEID "{" metodos "}" ";"')
    def clase(self, p):
        pass #return Clase(nombre=p.TYPEID, padre="OBJECT", nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)



    @_("atributos atributo") # Esta función y la siguiente es lo mismo que un 'or' aunque también se pueden separar por ','
    def atributos(self, p):
        return p.atributos+[p.atributo]


    @_(" ")
    def atributos(self, p):
        return []


    #@_("OBJECTID ':' TYPEID ';'")
    #def atributo(self, p):
    #    return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())


    @_('metodos metodo')
    def metodos(self, p):
        return p.metodos+[p.metodo]

    @_(' ')
    def metodos(self, p):
        return []


    @_('OBJECTID "(" ")" ":" TYPEID "{" expresion "}" ";"', 'OBJECTID "(" formales "," formales ")" ":" TYPEID "{" expresiones "}" ')
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







    @_('expresiones expresion')
    def expresiones(self, p):
        return p.expresiones+[p.expresion]

    @_(' ')
    def expresiones(self, p):
        return []





    @_('ASSIGN expresion', ' ')
    def assign_exp(self, p):
        if len(p) == 1:
            return "ASSIGN expresion"
        else:
            return ' '

    @_(' ', 'OBJECTID ":" TYPEID', 'OBJECTID ":" TYPEID assign_exp', 'let_rep "," let_rep')
    def let_rep(self, p):
        pass





    @_('expresiones expresion')
    def expresionas(self, p):
        return p.expresiones + p.expresion

    @_(' ')
    def expresionas(self, p):
        return p.expresion





    @_('OBJECTID ASSIGN expresion')
    def expresion(self, p):
        pass

    @_('expresion "+" expresion')
    def expresion(self, p):
        pass

    @_('expresion "-" expresion')
    def expresion(self, p):
        pass

    @_('expresion "*" expresion')
    def expresion(self, p):
        pass

    @_('expresion "/" expresion')
    def expresion(self, p):
        pass

    @_('expresion "<" expresion')
    def expresion(self, p):
        pass

    @_('expresion LE expresion')
    def expresion(self, p):
        pass

    @_('expresion "=" expresion')
    def expresion(self, p):
        pass

    @_('"(" expresion ")"')
    def expresion(self, p):
        pass

    @_('NOT expresion')
    def expresion(self, p):
        pass

    @_('ISVOID expresion')
    def expresion(self, p):
        pass

    @_('"~" expresion')
    def expresion(self, p):
        pass

    @_('expresion "@" TYPEID "." OBJECTID "(" ")"')
    def expresion(self, p):
        pass

    @_('expresion "@" TYPEID "." OBJECTID "(" expresiones "," expresion ")"')
    def expresion(self, p):
        pass

    @_('IF expresion THEN expresion ELSE expresion FI')
    def expresion(self, p):
        pass

    @_('WHILE expresion LOOP expresion POOL')
    def expresion(self, p):
        pass

    @_('LET OBJECTID ":" TYPEID assign_exp let_rep IN expresion', )
    def expresion(self, p):
        pass #return Let(nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion='let', cuerpo=':')

    @_('CASE expresion OF "(" OBJECTID ":" TYPEID DARROW expresionas ")" ";" ESAC')
    def expresion(self, p):
        pass

    @_('NEW TYPEID')
    def expresion(self, p):
        pass

    @_('"{" "(" expresionas ";" ")" "}"')
    def expresion(self, p):
        pass

    @_('OBJECTID')
    def expresion(self, p):
        pass

    @_('INT_CONST')
    def expresion(self, p):
        pass

    @_('STR_CONST')
    def expresion(self, p):
        pass

    @_('BOOL_CONST')
    def expresion(self, p):
        pass