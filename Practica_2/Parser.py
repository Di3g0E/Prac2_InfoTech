

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
        ('left', 'ISVOID', '*', '/', '+', '-'),
        ('nonassoc', 'LE', '<', '=', 'NOT'),
        ('right', 'ASSIGN')
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

    @_('OBJECTID "(" formales_opt ")" ":" TYPEID "{" expresiones "}"')
    def metodo(self, p):
        nombre = p.OBJECTID
        formales = p.formales_opt if p.formales_opt else []
        tipo = p.TYPEID
        cuerpo = p.expresiones
        return Metodo(linea=p.lineno, nombre=nombre, formales=formales, tipo=tipo, cuerpo=cuerpo)

    @_('formal "," formales_opt',
       'formal')
    def formales_opt(self, p):
        return [p.formal] if len(p) == 1 else [p.formal] + p.formales_opt

    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(linea=p.lineno, nombre_variable=p.OBJECTID, tipo=p.TYPEID)

    @_('expresion')
    def expresiones(self, p):
        return [p.expresion]

    @_('expresion "," expresiones',
       'expresion ";"')
    def expresiones(self, p):
        return [p.expresion] if len(p) == 2 else [p.expresion] + p.expresiones

    @_('expresion "+" expresion',
       'expresion "-" expresion',
       'expresion "*" expresion',
       'expresion "/" expresion',
       '"~" expresion',
       'expresion LE expresion',
       'expresion "<" expresion',
       'expresion "=" expresion',
       '"(" expresion ")"')
    def expresion(self, p):
        if p[1] == '+':
            return Suma(p.expresion, p.expresion)
        elif p[1] == '-':
            return Resta(p.expresion, p.expresion)
        elif p[1] == '*':
            return Multiplicacion(p.expresion, p.expresion)
        elif p[1] == '/':
            return Division(p.expresion, p.expresion)
        elif p[1] == '~':
            return Neg(p.expresion)
        elif p[1] == 'LE':
            return LeIgual(p.expresion, p.expresion)
        elif p[1] == '<':
            return Menor(p.expresion, p.expresion)
        elif p[1] == '=':
            return Igual(p.expresion, p.expresion)
        elif p[1] == '(':
            return p.expresion

    @_('expresion "@" TYPEID "." OBJECTID "(" ")"',
       'expresion "@" TYPEID "." OBJECTID "(" expresiones ")"')
    def expresion(self, p):
        if len(p) == 7:
            return LlamadaMetodoEstatico(
                cuerpo=p.expresion, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[]
            )
        else:
            return LlamadaMetodoEstatico(
                cuerpo=p.expresion, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=p.expresiones
            )

    @_('expresion "."', ' ')
    def expr_opc1(self, p):
        if len(p) == 2:
            return p.expreion
        else:
            return []

    @_('expr_opc1 OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expr_opc1, clase=p.OBJECTID, nombre_metodo=p.OBJECTID, argumentos=[])

    @_('expr_opc1 OBJECTID "(" expresiones ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expr_opc1, clase=p.OBJECTID, nombre_metodo=p.OBJECTID, argumentos=p.expresiones)

    @_('IF expresion THEN expresion ELSE expresion FI')
    def expresion(self, p):
        return Condicional(condicion=p.expresion0, verdadero=p.expresion1, falso=p.expresion2)

    @_('WHILE expresion LOOP expresion POOL')
    def expresion(self, p):
        return Bucle(condicion=p.expresion0, cuerpo=p.expresion1)


    @_('ASSIGN expresion', ' ')
    def expr_opc2(self, p):
        if p == ' ':
            return []
        else:
            return p.expreion

    @_('expr_rep "," OBJECTID ":" TYPEID expr_opc2', 'OBJECTID ":" TYPEID expr_opc2', ' ')
    def expr_rep(self, p):
        if len(p) == 1:
            return Expresion(cast=p.TYPEID, nombre=p.OBJECTID, cuerpo=p.expr_opc2)
        elif len(p) == 2:
            return p.expr_rep + [Expresion(cast=p.TYPEID, nombre=p.OBJECTID, cuerpo=p.expr_opc2)]
        else:
            return NoExpr(cast='_no_type')

    @_('LET OBJECTID ":" TYPEID expr_opc2 expr_rep IN expresion')
    def expresion(self, p):
        return Let(nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=p.expr_opc2, cuerpo=p.expresion)

    @_('OBJECTID ":" TYPEID DARROW expresion', 'OBJECTID ":" TYPEID DARROW expresion expr_rep2')
    def expr_rep2(self, p):
        if len(p) == 5:
            return Asignacion(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)
        else:
            return Asignacion(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion, expr_rep2=p.expr_rep2)

    @_('CASE expresion OF "(" expr_rep2 ")" ";" ESAC')
    def expresion(self, p):
        return Swicht(expr=p.expresion, casos=p.expr_rep2)

    @_('expresion ";"', 'expresion ";" expr_rep3')
    def expr_rep3(self, p):
        if len(p) == 2:
            return p.expresion
        else:
            return [p.expresion] + p.expr_rep3

    @_('"{" expr_rep3 "}"')
    def expresion(self, p):
        return Bloque(expresiones=p.expr_rep3)

    @_('OBJECTID',
       'INT_CONST',
       'BOOL_CONST',
       'STR_CONST',
       'NEW TYPEID',
       'ISVOID expresion',
       'NOT expresion')
    def expresion(self, p):
        if p[0] == 'OBJECTID':
            pass
        elif p[0] == 'INT_CONST':
            return Entero(p[0])
        elif p[0] == 'BOOL_CONST':
            return Booleano(p[0])
        elif p[0] == 'STR_CONST':
            return String(p[0])
        elif p[0] == 'NEW':
            return Nueva(p.TYPEID)
        elif p[0] == 'ISVOID':
            return EsNulo(p.expresion)
        elif p[0] == 'NOT':
            return Not(p.expresion)