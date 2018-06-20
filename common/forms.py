# coding=utf-8
from django.forms.utils import ErrorDict, ErrorList
import json


def form_errors_to_list(errors):
    assert isinstance(errors, ErrorDict)
    return [item[0]['message'] for item in list(json.loads(errors.as_json()).values())]


class DivErrorList(ErrorList):

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''

        return ('<div class="%s">%s</div>' %
                (self.error_class,
                 ''.join(['<div class="alert alert-danger">%s</div>'
                          % e for e in self])))

    def as_list(self):
        output = []
        for field, errors in self.items():
            output.append('%s' % e for e in errors)
        return output