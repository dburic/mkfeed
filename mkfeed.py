#!/usr/bin/env python

"""
Python module and command line script for making RSS 2.0 feeds. 
"""

__version__ = "1.0"

import re
import sys
import argparse

class FeedTemplate:
    """A simple class for storing feed templates."""
    def __init__(self, main, item):
        self.main = main
        self.item = item

RSS_TEMPLATE = FeedTemplate("""\
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
 <channel>
  <title>%(title)s</title>
  <link>%(link)s</link>
  <description><![CDATA[%(desc)s]]></description>
%(items)s
 </channel>
</rss>""",
"""\
  <item>
   <title>%(title)s</title>
   <link>%(link)s</link>
   <description><![CDATA[%(desc)s]]></description>
  </item>"""
)

class Container(dict):
    """A dictionary that can be easily initalized from another dictionary,
    especially the one returned by locals()."""
    def __init__(self, d={}, exclude=["self"]):
        dict.__init__(self)
        for k in d.keys():
            if not k in exclude:
                self[k] = d[k]

class FeedMaker:
    """Main class for making feeds. Contains methods for setting
    parameters, input parsing, and feed generation."""
    def __init__(self):
        self.items = []
        self.template = RSS_TEMPLATE

    def set_patterns(self, main, item):
        self.patterns = Container(locals())

    def set_feed_prop(self, title, link, desc):
        self.feed_prop = Container(locals())

    def set_item_prop(self, title, link, desc):
        self.item_prop = Container(locals())

    def _parse(self, string, pattern, maxitems=-1):
        """Parse string according to pattern and return a list of items.
        Parsing stops when maxitems > 0 are found."""
        items = []
        pieces = [p for p in re.split(r"(\{[*%]\})", pattern) if p]
        begin = 0
        while begin < len(string) and len(items) != maxitems:
            keep = False
            item = []
            for p in pieces:
                if p == "{*}":
                    keep = False
                elif p == "{%}":
                    keep = True
                else:
                    end = string.find(p, begin)
                    if end == -1: break
                    if keep: item.append(string[begin:end])
                    begin = end + len(p)
            else:
                if p == "{%}":
                    item.append(string[begin:])
                    begin = len(string)
            if not item: break
            items.append(item)
        return items
    
    def find_items(self, source):
        """Parse source, first with main pattern, then with item pattern."""
        items = self._parse(source, self.patterns["main"], 1)
        if items and items[0]:
            self.items.extend(self._parse(items[0][0], self.patterns["item"]))

    def _expand(self, template, item):
        """Expand a template into a string."""
        result = []
        for p in re.split(r"(\{%\d+\})", template):
            m = re.match(r"\{%(\d+)\}", p)
            if m:
                k = int(m.group(1))
                if k <= len(item): result.append(item[k - 1])
            else:
                result.append(p)
        return "".join(result)

    def _make_item(self, item):
        d = {}
        for k in self.item_prop.keys():
            d[k] = self._expand(self.item_prop[k], item)
        return self.template.item % d

    def make_feed(self):
        """Generate feed."""
        d = {"items": "\n".join([self._make_item(i) for i in self.items])}
        d.update(self.feed_prop)
        return self.template.main % d

def main():
    """Process command line arguments, parse stdin, and print the feed to
    stdout."""
    p = argparse.ArgumentParser(description="""Make an RSS 2.0 feed from
            a HTML, XML or similar document. Input is taken from stdin, and
            output goes to stdout.""")
    p.add_argument("--pattern-main", metavar="PATTERN", default="{%}")
    p.add_argument("--pattern-item", metavar="PATTERN", required=True)
    p.add_argument("--feed-title", metavar="TEXT", required=True)
    p.add_argument("--feed-link", metavar="URL", required=True)
    p.add_argument("--feed-desc", metavar="TEXT", required=True)
    p.add_argument("--item-title", metavar="TEMPLATE", required=True)
    p.add_argument("--item-link", metavar="TEMPLATE", required=True)
    p.add_argument("--item-desc", metavar="TEMPLATE", required=True)
    a = p.parse_args()
    f = FeedMaker()
    f.set_patterns(a.pattern_main, a.pattern_item)
    f.set_feed_prop(a.feed_title, a.feed_link, a.feed_desc)
    f.set_item_prop(a.item_title, a.item_link, a.item_desc)
    f.find_items(sys.stdin.read())
    print f.make_feed()

if __name__ == "__main__":
    main()

