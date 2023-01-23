import lxml.etree as ET
from itertools import tee, islice, chain

nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}


def previous_and_next(some_iterable):
    """taken from https://stackoverflow.com/a/1012089"""
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


def normalize_string(string: str) -> str:
    return " ".join(" ".join(string.split()).split())


def make_entity_label(
    name_node: ET.Element, default_msg="no label provided", default_lang="en"
) -> tuple[str, str]:
    """extracts labels from tei:persName|placeName|orgName"""

    lang_tag = name_node.get("{http://www.w3.org/XML/1998/namespace}lang", default_lang)
    fornames = [
        normalize_string(x)
        for x in name_node.xpath(".//tei:forename//text()", namespaces=nsmap)
    ]
    surnames = [
        normalize_string(x)
        for x in name_node.xpath(".//tei:surname//text()", namespaces=nsmap)
    ]
    if len(surnames) > 0 and len(fornames) > 0:
        label = f"{surnames[0]}, {' '.join(fornames)}"
    elif len(surnames) == 0 and len(fornames) > 0:
        label = f"{' '.join(fornames)}"
    elif len(surnames) > 0 and len(fornames) == 0:
        label = f"{surnames[0]}"
    else:
        name_node_text = " ".join(name_node.xpath(".//text()", namespaces=nsmap))
        label = normalize_string(name_node_text)
    if label is None or label == "":
        label = default_msg
    return label, lang_tag
