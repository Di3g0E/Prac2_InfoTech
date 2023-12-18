

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

    @_('formales_opt "," formal',
       'formal', ' ')
    def formales_opt(self, p):
        if len(p) == 3:
            return p.formales_opt + p.formal
        elif len(p) == 1:
            return p.formal
        else:
            return None

    @_('OBJECTID "(" formales_opt ")" ":" TYPEID "{" expresiones "}" ";"')
    def metodo(self, p):
        formales = p.formales_opt if p.formales_opt else []
        return Metodo(linea=p.lineno, nombre=p.OBJECTID, formales=formales, tipo=p.TYPEID, cuerpo=p.expresiones)

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
    def assign_expr(self, p):
        if len(p) == 2:
            return [p.expresion]
        else:
            return []

    @_('OBJECTID ":" TYPEID assign_expr', 'OBJECTID ":" TYPEID assign_expr "," rep_let', ' ')
    def rep_let(self, p):
        if len(p) == 4:
            return Let(nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=p.assign_expr)
        elif len(p) > 4:
            return Let(nombre=p.OBJETID, tipo=p.TYPEID, inicializacion=p.assign_expr, cuerpo=p.rep_let)
        else:
            return []

    @_('LET OBJECTID ":" TYPEID assign_expr rep_let IN expresion')
    def expresion(self, p):
        return Let(nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=p.rep_let, cuerpo=p.expresion)

    @_('OBJECTID ":" TYPEID DARROW expresion',
       'OBJECTID ":" TYPEID DARROW expresion expr_rep2')
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
            return Objeto(nombre=p.OBJECTID)
        elif p[0] == 'INT_CONST':
            return Entero(valor=p[0])
        elif p[0] == 'BOOL_CONST':
            return Booleano(valor=p[0])
        elif p[0] == 'STR_CONST':
            return String(valor=p[0])
        elif p[0] == 'NEW':
            return Nueva(tipo=p.TYPEID)
        elif p[0] == 'ISVOID':
            return EsNulo(expr=p.expresion)
        elif p[0] == 'NOT':
            return Not(expr=p.expresion)