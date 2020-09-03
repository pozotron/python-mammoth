from __future__ import unicode_literals

import re
from xml.sax.saxutils import escape

from .abc import Writer


class HtmlWriter(Writer):
    def __init__(self):
        self._fragments = []

    def text(self, text):
        text = _escape_html(text)
        try:
            # Following block should guarantee that <span> tags with pagenumbers info will be interpreted 'as they are'
            # Without changing '<' to '&lt' and so on
            # So in html they will be interpreted as tags and not as simple text

            pagenum = re.search(r"&lt;span data-page=&quot;(.*?)&quot;&gt;", text).group(1)
            text = re.sub(r"&lt;span data-page=&quot;\d+&quot;&gt;", f'<span data-page="{pagenum}">', text)
            text = re.sub(r"&lt;/span&gt;", "</span>", text)
            self._fragments.append(text)
        except AttributeError:
            self._fragments.append(text)
    
    def start(self, name, attributes=None):
        attribute_string = _generate_attribute_string(attributes)
        self._fragments.append("<{0}{1}>".format(name, attribute_string))

    def end(self, name):
        self._fragments.append("</{0}>".format(name))
    
    def self_closing(self, name, attributes=None):
        attribute_string = _generate_attribute_string(attributes)
        self._fragments.append("<{0}{1} />".format(name, attribute_string))
    
    def append(self, html):
        self._fragments.append(html)
    
    def as_string(self):
        return "".join(self._fragments)


def _escape_html(text):
    return escape(text, {'"': "&quot;"})


def _generate_attribute_string(attributes):
    if attributes is None:
        return ""
    else:
        return "".join(
            ' {0}="{1}"'.format(key, _escape_html(attributes[key]))
            for key in sorted(attributes)
        )
