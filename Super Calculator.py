from __future__ import division
from decimal import *
import sublime
import sublime_plugin
import re


class SuperCalculatorCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view
        self.settings = sublime.load_settings("Super Calculator.sublime-settings")

    def run(self, edit):
        regex = '(?=[0-9.]+)[0-9+\-*/.\(\)]+'
        selected_regions = self.view.sel()
        for region in selected_regions:
            expr = self.view.substr(region)
            if re.match(regex, expr):
                # calculate expression and replace it with the result
                result = str(eval(expr))
                # round result if decimals are found
                if '.' in result:
                    result = round(Decimal(result), self.settings.get("round_decimals"))
                result = str(result)
                if result.endswith('.0'):
                    dot_pos = result.find('.')
                    result = result[0:dot_pos]
                self.view.replace(edit, region, result)
                # move cursor after the result
                result_region = self.view.sel()[-1]
                result_region_end = sublime.Region(result_region.end(), result_region.end())
                self.view.sel().clear()
                self.view.sel().add(result_region_end)
                sublime.status_message("Calculated result: " + expr + "=" + result)
            else:
                line_region = self.view.line(region)
                match_region = self.find_reverse(regex, region)
                if match_region:
                    match = self.view.substr(match_region)
                    # validate result and check if it is in the current line
                    if re.match(regex, match) and line_region.begin() <= match_region.begin():
                        self.view.sel().clear()
                        self.view.sel().add(match_region)
                        sublime.status_message("Calculate: " + match + "?")

    def find_reverse(self, string, region):
        new_regions = (r for r in reversed(self.view.find_all(string))
            if r.begin() < region.end())
        try:
            new_region = new_regions.next()
        except StopIteration:
            return None
        else:
            return new_region
