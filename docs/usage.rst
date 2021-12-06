=====
Usage
=====

Batch process a collection of XML/Documents by adding xml:id, xml:base next and prev attributes to the documents root element run::

    add-attributes -g "/path/to/your/xmls/*.xml" -b "https://value/of-your/base.com"
    add-attributes -g "../../xml/grundbuecher/gb-data/data/editions/*.xml" -b "https://id.acdh.oeaw.ac.at/grundbuecher"


Write mentions as listEvents into index-files::

    mentions-to-indices -t "erwähnt in " -i "/path/to/your/xmls/indices/*.xml" -f "/path/to/your/xmls/editions/*.xml"


Write mentions as listEvents ot index-files and copy enriched index entries into files::

    denormalize-indices -f "../../xml/schnitzler/schnitzler-tagebuch-data-public/editions/*.xml" -i "../../xml/schnitzler/schnitzler-tagebuch-data-public/indices/*.xml"
    denormalize-indices -f "./data/*/*.xml" -i "./data/indices/*.xml" -m ".//*[@key]/@key" -x ".//tei:title[@level='a']/text()"
    denormalize-indices -f "./data/*/*.xml" -i "./data/indices/*.xml" -m ".//*[@key]/@key" -x ".//tei:title[@level='a']/text()" -b pmb2121 -b pmb10815 -b pmb50


Register handle-ids and add them as tei:idno elements::

    add-handles -g "../../xml/grundbuecher/gb-data/data/editions/*.xml" -user "user12.3456-01" -pw "verysecret" -hixpath ".//tei:publicationStmt"