import sublime, sublime_plugin
import re

class SuperCalculatorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
            regex = '(?=[0-9]+)[0-9+\-*/.\(\)]+'
            selected_regions = self.view.sel()
            for region in selected_regions:
                expr = self.view.substr(region)
                if re.match(regex, expr):
                    # calculate expression and replace it with the result
                    result = str(eval(expr))
                    self.view.replace(edit, region, result)
                    # move cursor after the result
                    result_region = self.view.sel()[-1]
                    result_region_end = sublime.Region(result_region.end(), result_region.end())
                    self.view.sel().clear()
                    self.view.sel().add(result_region_end)
                    sublime.status_message("Calculated result: " + expr + "=" + result)
                else:
                    line_region = self.view.line(region)
                    # do reverse find
                    new_regions = (r for r in reversed(self.view.find_all(regex))
                        if r.begin() < region.end())
                    try:
                        match_region = new_regions.next()
                    except StopIteration:
                        continue
                    if match_region:
                        match = self.view.substr(match_region)
                        # validate result and check if it is in the current line
                        if re.match(regex, match) and line_region.begin() <= match_region.begin():
                            self.view.sel().clear()
                            self.view.sel().add(match_region)
                            print match_region
                            sublime.status_message("Calculate: " + match + "?")
