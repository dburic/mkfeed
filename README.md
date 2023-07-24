mkfeed: a program for making RSS feeds
======================================================================

mkfeed is a Python module and command line script for creating RSS 2.0
feeds from HTML, XML, and similar text documents. The feed is created by
parsing the text with user-specified patterns. mkfeed can be used to
quickly provide a feed where none is available.

mkfeed was inspired by [Feed43](http://feed43.com/), a user-friendly
service for converting web pages to RSS feeds.

This file explains how to use mkfeed from the command line on a Linux
system. The system specific details should be easily adaptable to other
systems. 


License
------------------------------

This software is distributed under the MIT license. See LICENSE for
details.


Installation
------------------------------

Copy mkfeed.py to a directory in the path and make it executable.
For example:

    cp mkfeed.py $HOME/bin/mkfeed
    chmod +x $HOME/bin/mkfeed

mkfeed has been tested with Python 2.6 and 2.7, but should work on other
versions too. 

The argparse library, which is part of Python since versions 2.7 and 3.2, is
used for parsing command line arguments. For older versions of Python,
argparse is provided as a separate package. In Debian, argparse is
available in the python-argparse package.

Test the installation:

    mkfeed --help


Usage
------------------------------

mkfeed takes input from stdin, and prints its output to stdout. If the
input is a web page, some other program (for example, wget or curl) has to
be used to actually download the page, which can then be piped through
mkfeed.

### Parsing input

News items are extracted from the input using user-specified patterns.
There are two patterns, the main pattern, and the item pattern. The main
pattern is applied only once, to extract the part of the input which
contains all desired news items. The main pattern is optional, and if left
unspecified, all input is used. The item pattern is applied repeatedly, to
extract properties of individual news items, which are then used to form
items of the generated feed.

A parsing pattern (main or item) is a string of normal characters and
special macros. Two types of macros are available in mkfeed, the parameter
macro `{%}` and the skip macro `{*}`. Both macros match any sequence of
zero or more characters, but `{%}` keeps the matched sequence for later
retrieval, while `{*}` does not. Thus, `{%}` should be used for storing,
and `{*}` for skipping parts of the input.

The main pattern should have only one parameter macro (there could be more,
but only the first one will be used). If the main pattern is not specified,
`{%}` is assumed, which grabs all input and works just fine most of the
time. As an example, one could set the main pattern to
`<body{*}>{%}</body>`, which means that only the body of the HTML document
will be parsed for news items.

Input snippets grabbed by parameter macros in the item pattern are later
available (in item templates, see below) as `{%1}`, `{%2}`, `{%3}`, and so
on, where `{%1}` is the snippet stored by the first parameter macro, `{%2}`
is the snippet stored by the second parameter macro, and so on. 

For example, the pattern 

    <h3 class="news-title"{*}>{%}</h3>{*}<div class="news-text">{%}</div>

will match a `h3` element of the class `news-title`, with possibly other
attributes, followed by arbitrary characters, followed by a `div` element
of the class `news-text`, and will store (only) the content of those
elements into `{%1}` and `{%2}` respectively.

### Creating output

For creating the output feed, the user has to specify the title, link, and
description of the feed. HTML code can be used in the description, but the
title should be plain text.

The user has also to specify the title, link, and description of each news
item. For this, item templates are used. An item template is a string of
normal characters and special macros `{%1}`, `{%2}`, `{%3}`, and so on,
explained above. Usually, one of these macros will be the title, another
will be the link (or part of it), while yet another will be the
description. As before, HTML code can be used in the description, but not
in the title.

Continuing the previous example, one could use `{%1}` as the title, `{%2}`
as the description, and, lacking something better, a constant address for
the link.


Example
------------------------------

Below is a more elaborate example that creates a feed of a YouTube search
for "Learn Python". Use redirection to store the resulting feed in a file.

    URL="https://www.youtube.com/results?search_query=Learn+Python"
    wget -q -O - "$URL" | mkfeed \
        --pattern-main '<ol{*}class={*}item-section{*}>{%}' \
        --pattern-item '<h3{*}class={*}yt-lockup-title{*}>{*}<a{*}href="{%}"{*}>{%}</a>{*}<div{*}class={*}yt-lockup-description{*}>{%}</div>' \
        --feed-title 'YouTube' \
        --feed-link "$URL" \
        --feed-desc 'Search results for "Learn Python"' \
        --item-title '{%2}' \
        --item-link 'https://youtube.com/{%1}' \
        --item-desc '{%3}'

The development of such a long code snippet is best done in a text editor.
The code can then either be copied to a terminal, or saved and executed as
a shell script.


Resources
------------------------------

 - [RSS 2.0 Specification](http://cyber.law.harvard.edu/rss/rss.html)

