# coding: utf-8

from sly import Lexer
import os
import re
import sys


class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, STR_CONST, LE, DARROW, ASSIGN}
    # ignore = '\t '
    literals = {'(', '*', ')', ';', '{', '}', '=', ':', '.', ',', '~', '-', '/', '<', '@', '+'}
    # Ejemplo
    ELSE = r'\b[eE][lL][sS][eE]\b'

    CARACTERES_CONTROL = [bytes.fromhex(i + hex(j)[-1]).decode('ascii')
                          for i in ['0', '1']
                          for j in range(16)] + [bytes.fromhex(hex(127)[-2:]).decode("ascii")]

    #@_(r'\(')
    #def LPAREN(self, t):
    #    return t

    #@_(r'\)')
    #def RPAREN(self, t):
    #    return t

    @_(r'(<-|->)')
    def ASSIGN(self, t):
        return t

    @_(r'=>')
    def DARROW(self, t):
        return t

    @_(r'<=')
    def LE(self, t):
        return t

    @_(r'(t[rR][uU][eE]\b)|(f[aA][lL][sS][eE]\b)')
    def BOOL_CONST(self, t):
        if t.value.lower() == "true":
            t.value = True
        else:
            t.value = False
        return t


    @_(r'"([^"]*)"')
    def STR_CONST(self, t):
        t.value = t.value.replace('\t', '\\t')
        return t

    @_(r'\d+')
    def INT_CONST(self, t):
        return t

    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECTID(self, t):  # También tiene que leer palabras conectadas por barra baja
        keys = {'NOT', 'IN', 'CASE', 'CLASS', 'ESAC', 'FI', 'IF', 'INHERITS', 'ISVOID', 'LET', 'LOOP', 'NEW', 'OF',
                'POOL', 'THEN', 'WHILE'}
        if t.value.upper() in keys:
            t.type = t.value.upper()
        return t

    @_(r'[A-Z][a-zA-Z0-9_]*')
    def TYPEID(self, t):
        keys = {'NOT', 'IN', 'CASE', 'CLASS', 'ESAC', 'FI', 'IF', 'INHERITS', 'ISVOID', 'LET', 'LOOP', 'NEW', 'OF',
                'POOL', 'THEN', 'WHILE'}
        if t.value.upper() in keys:
            t.type = t.value.upper()
        return t

    @_(r'\(\*((.|\n)*?)\*\)|--(.*)')
    def multilinecomment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\t| |\v|\r|\f')
    def spaces(self, t):
        pass

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        self.index += 1
    @_('_|\*\)|\!|\#|\$|\%|\^|\&|\>|\?|\`|\[|\[|\]|\||\\\\|EOF')
    def ERROR(self, t):
        if t.value == '_':
            t.value = '"_"'
        if t.value == '!':
            t.value = '"!"'
        if t.value == '#':
            t.value = '"#"'
        if t.value == '$':
            t.value = '"$"'
        if t.value == '%':
            t.value = '"%"'
        if t.value == '^':
            t.value = '"^"'
        if t.value == '&':
            t.value = '"&"'
        if t.value == '>':
            t.value = '">"'
        if t.value == '?':
            t.value = '"?"'
        if t.value == '`':
            t.value = '"`"'
        if t.value == '[':
            t.value = '"["'
        if t.value == ']':
            t.value = '"]"'
        if t.value == '|':
            t.value = '"|"'
        if t.value == '\\':
            t.value = '"\\\\"'
        elif t.value == '*)':
            t.value = '"Unmatched *)"'
        return t

    def salida(self, texto):
        lexer = CoolLexer()
        list_strings = []
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\' '
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} {token.value}'
            else:
                result = f'#{token.lineno} {token.type}'
            list_strings.append(result)
        return list_strings
