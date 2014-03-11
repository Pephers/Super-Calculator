from __future__ import division

import sys
import re
import math
import random
from decimal import *

import sublime
import sublime_plugin


class SuperCalculatorCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view
        self.settings = sublime.load_settings("Super Calculator.sublime-settings")
        self.callables = {}
        self.constants = {}
        for lib in (random, math):
            for key in dir(lib):
                attr = getattr(lib, key)
                if key[0] != '_':
                    if callable(attr):
                        self.callables[key] = attr
                    else:
                        self.constants[key] = attr
                        self.constants[key.upper()] = attr

        def average(nums):
            return sum(nums) / len(nums)

        self.callables['avg'] = average
        self.callables['average'] = average

        class Constant(object):
            def __init__(self, func):
                self._func = func

            def __call__(self, *args, **kwargs):
                return self._func(*args, **kwargs)

            def __repr__(self):
                return self._func()

        def password(length=10):
            pwdchrs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            return ''.join(random.choice(pwdchrs) for _ in range(length))

        password = Constant(password)
        self.callables['pwd'] = password
        self.callables['password'] = password
        self.constants['pwd'] = password
        self.constants['password'] = password
        self.constants['PWD'] = password
        self.constants['PASSWORD'] = password

        allowed = '|'.join(
            [r'[-+*/%%()]'] +
            [r'\b[-+]?(\d*\.)?\d+\b'] +
            [r'\b%s\b' % c for c in self.constants.keys()] +
            [r'\b%s\s*\(' % c for c in self.callables.keys()]
        )
        self.regex = r'(%s)((%s|[ ])*(%s))?' % (allowed, allowed, allowed)
        self.dict = self.callables.copy()
        self.dict.update(self.constants)

    def run(self, edit):
        result_regions = []
        exprs = []
        for region in reversed(self.view.sel()):
            # Do the replacement in reverse order, so the character offsets
            # don't get invalidated
            exprs.append((region, self.view.substr(region)))
        for region, expr in exprs:
            if expr:
                # calculate expression and replace it with the result
                try:
                    result = str(eval(expr, self.dict, {}))
                except Exception as e:
                    sublime.status_message("Error: %s" % e)
                    continue
                else:
                    # round result if decimals are found
                    if '.' in result:
                        result = round(Decimal(result), self.settings.get("round_decimals"))
                    result = str(result)
                    if self.settings.get("trim_zeros") and '.' in result:
                        result =  result.strip('0').rstrip('.')
                        if result == '':
                            result = '0'
                    if result != expr:
                        self.view.replace(edit, region, result)
                        sublime.status_message("Calculated result: " + expr + "=" + result)
                    continue
            line_region = self.view.line(region)
            match_region = self.find_reverse(self.regex, region)
            if match_region:
                match = self.view.substr(match_region)
                # validate result and check if it is in the current line
                if re.match(self.regex, match) and line_region.begin() <= match_region.begin():
                    result_regions.append(match_region)
                    sublime.status_message("Calculate: " + match + "?")
        if result_regions:
            self.view.sel().clear()
            for region in result_regions:
                self.view.sel().add(region)

    def find_reverse(self, string, region):
        new_regions = (r for r in reversed(self.view.find_all(string))
            if r.begin() < region.end())
        try:
            if sys.version_info < (3,0,0) :
                new_region = new_regions.next()
            else :
                new_region = next(new_regions)
        except StopIteration:
            return None
        else:
            return new_region
