=====
Usage
=====

Batch process a collection of XML/Documents by adding xml:id, xml:base next and prev attributes to the documents root element run::

    add-attributes -g "/path/to/your/xmls/*.xml" -b "https://value/of-your/base.com"


Write mentions as listEvents into index-files::

    mentions-to-indices -t "erwähnt in " -i "/path/to/your/xmls/indices/*.xml" -f "/path/to/your/xmls/editions/*.xml"


Write mentions as listEvents ot index-files and copy enriched index entries into files::

    denormalize-indices -f "../../xml/schnitzler/schnitzler-tagebuch-data-public/editions/*.xml" -i "../../xml/schnitzler/schnitzler-tagebuch-data-public/indices/*.xml"