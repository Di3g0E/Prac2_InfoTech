

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
        ('right', 'ASSIGN'),
        ('nonassoc', 'LE', '<', '=', 'NOT'),
        ('left', 'ISVOID', '*', '/', '+', '-'),
        ('nonassoc', '@'),
        ('nonassoc', '.')
    )



    @_('clases')
    def Programa(self, p):
        return Programa(secuencia=p.clases)

    @_('clase', 'clases clase')
    def clases(self, p):
        if len(p) == 2:
            return p.clases + [p.clase]
        else:
            return [p.clase]

    @_('CLASS TYPEID "{" atributos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre="OBJECT", nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)

    @_('CLASS TYPEID "{" metodos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre="OBJECT", nombre_fichero=self.nombre_fichero, caracteristicas=p.metodos)

    @_('CLASS TYPEID INHERITS TYPEID "{" atributos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID0, padre=p.TYPEID1, nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)

    @_('CLASS TYPEID INHERITS TYPEID "{" metodos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID0, padre=p.TYPEID1, nombre_fichero=self.nombre_fichero, caracteristicas=p.metodos)

    @_("atributos atributo")  # Esta función y la siguiente es lo mismo que un 'or' aunque también se pueden separar por ','
    def atributos(self, p):
        return p.atributos + [p.atributo]

    @_(" ")
    def atributos(self, p):
        return []

    @_('OBJECTID ":" TYPEID ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())

    @_('OBJECTID ":" TYPEID ASSIGN expresion ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)

    @_('metodos metodo', ' ')
    def metodos(self, p):
        if len(p) == 2:
            return p.metodos + [p.metodo]
        else:
            return []

    @_('OBJECTID "(" ")" ":" TYPEID "{" expresion "}" ";"')
    def metodo(self, p):
        return Metodo(nombre=p.OBJECTID, formales=[], tipo=p.TYPEID, cuerpo=p.expresion)

    @_('OBJECTID "(" formales formal ")" ":" TYPEID "{" expresion "}" ";"')
    def metodo(self, p):
        return Metodo(nombre=p.OBJECTID, formales=p.formales+[p.formal], tipo=p.TYPEID, cuerpo=p.expresion)

    @_('formales formal ","')
    def formales(self, p):
        return p.formales + [p.formal]

    @_(' ')
    def formales(self, p):
        return []

    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID)

    @_('expresion "+" expresion',
       'expresion "-" expresion',
       'expresion "*" expresion',
       'expresion "/" expresion',
       'expresion "<" expresion',
       'expresion LE expresion',
       'expresion "=" expresion',
       '"(" expresion ")"',
       '"~" expresion')
    def expresion(self, p):
        if p[1] == '+':
            return Suma(izquierda=p.expresion0, derecha=p.expresion1, operando='+')
        elif p[1] == '-':
            return Resta(izquierda=p.expresion0, derecha=p.expresion1, operando='-')
        elif p[1] == '*':
            return Multiplicacion(izquierda=p.expresion0, derecha=p.expresion1, operando='*')
        elif p[1] == '/':
            return Division(izquierda=p.expresion0, derecha=p.expresion1, operando='/')
        elif p[1] == '<':
            return Menor(izquierda=p.expresion0, derecha=p.expresion1, operando='<')
        elif p[1] == 'LE':
            return LeIgual(izquierda=p.expresion0, derecha=p.expresion1, operando='<=')
        elif p[1] == '=':
            return Igual(izquierda=p.expresion0, derecha=p.expresion1, operando='=')
        elif p[0] == '(' and p[2] == ')':
            pass
        elif p[0] == '~':
            return Neg(expr=p.expresion, operador='~')

    @_('expresion "@" TYPEID "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[])

    @_('expresiones expresion ","')
    def expresiones(self, p):
        return p.expresiones + [p.expresion]

    @_(' ')
    def expresiones(self, p):
        return []

    @_('expresion "@" TYPEID "." OBJECTID "(" expresiones expresion ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion0, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=p.expresiones+[p.expresion1])

    @_('OBJECTID "(" expresiones expresion ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=NoExpr(), nombre_metodo=p.OBJECTID, argumentos=p.expresiones+[p.expresion])

    @_('expresion "." OBJECTID "(" expresiones expresion ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=p.expresion0, nombre_metodo=p.OBJECTID, argumentos=p.expresiones+[p.expresion1])

    @_('OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=NoExpr(), nombre_metodo=p.OBJECTID, argumentos=NoExpr())

    @_('expresion "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=p.expresion, nombre_metodo=p.OBJECTID, argumentos=NoExpr())

    @_('IF expresion THEN expresion ELSE expresion FI')
    def expresion(self, p):
        return Condicional(condicion=p.expresion0, verdadero=p.expresion1, falso=p.expresion2)

    @_('WHILE expresion LOOP expresion POOL')
    def expresion(self, p):
        return Bucle(condicion=p.expresion0, cuerpo=p.expresion1)

    @_(' ')
    def let_rep(self, p):
        pass

    @_('OBJECTID ":" TYPEID')
    def let_rep(self, p):
        pass

    @_('OBJECTID ":" TYPEID ASSIGN expresion')
    def let_rep(self, p):
        pass

    @_('let_rep OBJECTID ":" TYPEID ","')
    def let_rep(self, p):
        pass

    @_('let_rep OBJECTID ":" TYPEID ASSIGN expresion ","')
    def let_rep(self, p):
        pass

    @_('LET OBJECTID ":" TYPEID let_rep IN expresion')
    def expresion(self, p):
        pass #return Let(nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=p.rep_let, cuerpo=p.expresion)

    @_('LET OBJECTID ":" TYPEID ASSIGN expresion let_rep IN expresion')
    def expresion(self, p):
        pass #return Let(nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=p.rep_let, cuerpo=p.expresion)

    @_('OBJECTID ":" TYPEID DARROW expresion')
    def case_rep(self, p):
        return RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)

    @_('case_rep OBJECTID ":" TYPEID DARROW expresion')
    def case_rep(self, p):
        return p.case_rep + [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]

    @_('CASE expresion OF case_rep ";" ESAC')
    def expresion(self, p):
        return Swicht(expr=p.expresion, casos=p.case_rep)

    @_(' ')
    def llaves_rep(self, p):
        return []

    @_('llaves_rep expresion ";"')
    def llaves_rep(self, p):
        return Bloque(expresiones=p.llaves_rep+[p.expresion])

    @_('"{" llaves_rep expresion ";" "}"')
    def expresion(self, p):
        return Bloque(expresiones=p.llaves_rep+[p.expresion])

    @_('NOT expresion',
       'ISVOID expresion',
       'NEW TYPEID',
       'OBJECTID',
       'INT_CONST',
       'STR_CONST',
       'BOOL_CONST')
    def expresion(self, p):
        if p[0] == 'NOT':
            return Not(expr=p.expresion, operador='NOT')
        elif p[0] == 'ISVOID':
            return EsNulo(expr=p.expresion)
        elif p[0] == 'NEW':
            return Nueva(tipo=p.TYPEID)
        elif p[0] == 'OBJECTID':
            return Objeto(nombre=p.OBJECTID)
        elif p[0] == 'INT_CONST':
            return Entero(valor=p.INT_CONST)
        elif p[0] == 'STR_CONST':
            return String(valor=p.STR_CONST)
        elif p[0] == 'BOOL_CONST':
            return Booleano(valor=p.BOOL_CONST)
