# acdh-tei-pyutils

[![Github Workflow Tests Status](https://github.com/acdh-oeaw/acdh-tei-pyutils/workflows/Test/badge.svg)](https://github.com/acdh-oeaw/acdh-tei-pyutils/workflows/Test/badge.svg)
[![PyPI version](https://badge.fury.io/py/acdh-tei-pyutils.svg)](https://badge.fury.io/py/acdh-tei-pyutils)
[![codecov](https://codecov.io/gh/acdh-oeaw/acdh-tei-pyutils/branch/main/graph/badge.svg?token=y6HUg72XnH)](https://codecov.io/gh/acdh-oeaw/acdh-tei-pyutils)

Utilty functions to work with TEI Documents

## install

run `pip install acdh-tei-pyutils`

## usage

some examples on how to use this package

### parse an XML/TEI Document from and URL, string or file:

```python
from acdh_tei_pyutils.tei import TeiReader

doc = TeiReader("https://raw.githubusercontent.com/acdh-oeaw/acdh-tei-pyutils/main/acdh_tei_pyutils/files/tei.xml")
print(doc.tree)
>>> <Element {http://www.tei-c.org/ns/1.0}TEI at 0x7ffb926f9c40>

doc = TeiReader("./acdh_tei_pyutils/files/tei.xml")
doc.tree
>>> <Element {http://www.tei-c.org/ns/1.0}TEI at 0x7ffb926f9c40>
```

### write the current XML/TEI tree object to file
```python
doc.tree_to_file("out.xml")
>>> 'out.xml'
```

see [acdh_tei_pyutils/cli.py](https://github.com/acdh-oeaw/acdh-tei-pyutils/blob/main/acdh_tei_pyutils/cli.py) for further examples

### command line scripts

Batch process a collection of XML/Documents by adding xml:id, xml:base next and prev attributes to the documents root element run:

```bash
add-attributes -g "/path/to/your/xmls/*.xml" -b "https://value/of-your/base.com"
add-attributes -g "../../xml/grundbuecher/gb-data/data/editions/*.xml" -b "https://id.acdh.oeaw.ac.at/grundbuecher"
```

Write mentions as listEvents into index-files:

```bash
mentions-to-indices -t "erwähnt in " -i "/path/to/your/xmls/indices/*.xml" -f "/path/to/your/xmls/editions/*.xml"
```

Write mentions as listEvents of index-files and copy enriched index entries into files

```bash
# docs
uv run denormalize-indices --help 

# examples
uv run denormalize-indices -f "../../xml/schnitzler/schnitzler-tagebuch-data-public/editions/*.xml" -i "../../xml/schnitzler/schnitzler-tagebuch-data-public/indices/*.xml"
uv run denormalize-indices -f "./data/*/*.xml" -i "./data/indices/*.xml" -m ".//*[@key]/@key" -x ".//tei:title[@level='a']/text()"
uv run denormalize-indices -f "./data/*/*.xml" -i "./data/indices/*.xml" -m ".//*[@key]/@key" -x ".//tei:title[@level='a']/text()" -b pmb2121 -b pmb10815 -b pmb50
uv run denormalize-indices -f "./data/*/*.xml" -i "./data/indices/*.xml" --standoff # writes entity-lists into a tei:standOff element and not in a back element. 
```
## develop

* project uses [uv](https://docs.astral.sh/uv/)
* linting/formatting `uv run ruff check .` `uv run ruff format .`
* before commiting run `flake8` to check linting and `uv run coverage run -m pytest -v` to run the tests

### bump version
```shell
uv version --bump minor
```