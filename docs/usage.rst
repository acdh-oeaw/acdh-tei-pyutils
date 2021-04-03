=====
Usage
=====

Batch process a collection of XML/Documents by adding xml:id, xml:base next and prev attributes to the documents root element run::

    add-attributes -g "/path/to/your/xmls/*.xml" -b "https://value/of-your/base.com"


Write mentiones as listEvents into index-files::

    mentions-to-indices -t "erwähnt in " -i "/path/to/your/xmls/indices/*.xml" -f "/path/to/your/xmls/editions/*.xml"