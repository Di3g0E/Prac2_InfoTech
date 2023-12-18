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
        ('right', 'ASSIGN'),
        ('nonassoc', 'NOT'),
        ('nonassoc', 'LE', '<', '='),
        ('left', '+', "-"),
        ('left', '~', '*', '/', 'ISVOID'),
        ('left', '@'),
        ('left', '.')
    )

    # PROGRAMA

    @_('clases')
    def Programa(self, p):
        return Programa(secuencia=p.clases)

    # CLASE

    @_('clase', 'clases clase')  # clase+
    def clases(self,p):
        if len(p)==2:
            return p.clases+[p.clase]
        else:
            return [p.clase]

    @_('CLASS TYPEID "{" caracteristicas "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre='Object', nombre_fichero=self.nombre_fichero,
                     caracteristicas=p.caracteristicas)

    @_('CLASS TYPEID inhert_opt "{" caracteristicas "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre=p.inhert_opt, nombre_fichero=self.nombre_fichero,
                     caracteristicas=p.caracteristicas)
    @_('')
    def inhert_opt(self, p):
        return 'Object'

    @_('INHERITS TYPEID')
    def inhert_opt(self, p):
        return p.TYPEID

    @_('caracteristicas caracteristica')
    def caracteristicas(self, p):
        return p[0] + [p[1]]

    @_(' ')
    def caracteristicas(self, p):
        return []

    @_('atributo')
    def caracteristica(self, p):
        return p[0]

    @_('metodo')
    def caracteristica(self, p):
        return p[0]


    # ATRIBUTOS


    @_('OBJECTID ":" TYPEID ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())

    @_('OBJECTID ":" TYPEID ";" ASSIGN expresion ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)

    # METODO

    @_('OBJECTID "(" ")" ":" TYPEID "{" expresion "}" ";"')
    def metodo(self, p):
        return Metodo(nombre=str(p.OBJECTID), tipo=str(p.TYPEID), formales=[], cuerpo=p.expresion)

    @_('OBJECTID "(" formales ")" ":" TYPEID "{" expresion "}" ";"')
    def metodo(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, formales=p.formales, cuerpo=p.expresion)

    # FORMAL
    @_('formal', 'formales "," formal')
    def formales(self, p):
        return p.formales + [p.formal] if len(p) == 3 else [p.formal]
    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID)

    # EXPRESION

    @_('OBJECTID ASSIGN expresion')
    def expresion(self, p):
        return Asignacion(nombre=p.OBJECTID, cuerpo=p.expresion)

    @_("expresion '+' expresion")
    def expresion(self, p):
        return Suma(izquierda=p.expresion0, derecha=p.expresion1)

    @_("expresion '-' expresion")
    def expresion(self, p):
        return Resta(izquierda=p.expresion0, derecha=p.expresion1)

    @_("expresion '*' expresion")
    def expresion(self, p):
        return Multiplicacion(izquierda=p.expresion0, derecha=p.expresion1)

    @_("expresion '/' expresion")
    def expresion(self, p):
        return Division(izquierda=p.expresion0, derecha=p.expresion1)

    @_("expresion '<' expresion")
    def expresion(self, p):
        return Menor(izquierda=p.expresion0, derecha=p.expresion1)

    @_("expresion LE expresion")
    def expresion(self, p):
        return LeIgual(izquierda=p.expresion0, derecha=p.expresion1)

    @_("expresion '=' expresion")
    def expresion(self, p):
        return Igual(izquierda=p.expresion0, derecha=p.expresion1)

    @_('"(" expresion ")"')
    def expresion(self, p):
        return p.expresion

    @_("NOT expresion")
    def expresion(self, p):
        return Not(expr=p.expresion)

    @_("ISVOID expresion")
    def expresion(self, p):
        return EsNulo(expr=p.expresion)

    @_("'~' expresion")
    def expresion(self, p):
        return Neg(expr=p.expresion)

    @_('expresion "@" TYPEID "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[])

    @_('expresion "@" TYPEID "." OBJECTID "(" argumentos ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion, clase=p.TYPEID, nombre_metodo=p.OBJECTID,
                                     argumentos=p.argumentos)

    @_('OBJECTID "(" argumentos ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=p.argumentos, cuerpo=Objeto(nombre='self'))

    @_('expresion "." OBJECTID "(" argumentos ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=p.argumentos, cuerpo=p.expresion)

    @_('OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=[], cuerpo=Objeto(nombre='self'))

    @_('expresion "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=[], cuerpo=p.expresion)

    @_('IF expresion THEN expresion ELSE expresion FI')
    def expresion(self, p):
        return Condicional(condicion=p[1], verdadero=p[3], falso=p[5])

    @_('WHILE expresion LOOP expresion POOL')
    def expresion(self, p):
        return Bucle(condicion=p[1], cuerpo=p[3])

    # LET
    @_('OBJECTID ":" TYPEID opt_assign')
    def let_declaration(self, p):
        return (p.OBJECTID, p.TYPEID, p.opt_assign)

    @_('let_declaration')
    def let_declarations(self, p):
        return [p.let_declaration]

    @_('let_declarations "," let_declaration')
    def let_declarations(self, p):
        return p.let_declarations + [p.let_declaration]

    @_('LET let_declarations IN expresion')
    def expresion(self, p):
        cuerpo = p.expresion
        for nombre, tipo, inicializacion in reversed(p.let_declarations):
            cuerpo = Let(nombre=nombre, tipo=tipo, inicializacion=inicializacion, cuerpo=cuerpo)
        return cuerpo

    @_('CASE expresion OF rama_case ESAC')
    def expresion(self, p):
        return Swicht(expr=p.expresion, casos=p.rama_case)

    @_('OBJECTID ":" TYPEID DARROW expresion ";"')
    def rama_case(self, p):
        return [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]

    @_('rama_case OBJECTID ":" TYPEID DARROW expresion ";"')
    def rama_case(self, p):
        return p.rama_case + [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]

    @_('NEW TYPEID')
    def expresion(self, p):
        return Nueva(tipo=p.TYPEID)

    @_('"{" expresiones_puntoComa  "}"')
    def expresion(self, p):
        return p.expresiones_puntoComa

    @_('expresion ";"', 'expresiones_puntoComa expresion ";"')
    def expresiones_puntoComa(self, p):
        if len(p) == 2:
            return Bloque(expresiones=[p.expresion])
        else:
            lista = p.expresiones_puntoComa.expresiones
            lista += [p.expresion]
            return Bloque(expresiones=lista)

    @_('OBJECTID')
    def expresion(self, p):
        return Objeto(nombre=p.OBJECTID)

    @_('INT_CONST')
    def expresion(self, p):
        return Entero(valor=p.INT_CONST)
    @_('STR_CONST')
    def expresion(self, p):
        return String(valor=p.STR_CONST)

    @_('BOOL_CONST')
    def expresion(self, p):
        return Booleano(valor=p.BOOL_CONST)

    # Asignacion Opcional

    @_('ASSIGN expresion')
    def opt_assign(self, p):
        return p.expresion

    @_('')
    def opt_assign(self, p):
        return NoExpr()

    # Argumentos

    @_('expresion', 'argumentos "," expresion')
    def argumentos(self, p):
        return p.argumentos + [p.expresion] if len(p) == 3 else [p.expresion]

    # Error

    def error(self, p):
        if p:
            err_location = f'"{self.nombre_fichero}", line {p.lineno}'
            err_msg = f'syntax error at or near {p.type} = {p.value}'
            self.errores.append(f'{err_location}:{err_msg}')