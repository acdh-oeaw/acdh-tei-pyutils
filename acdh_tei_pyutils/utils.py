import lxml.etree as ET
from itertools import tee, islice, chain
from typing import Union

from acdh_tei_pyutils.tei import TeiReader

nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}


def get_xmlid(element: ET.Element) -> str:
    """returns an @xml:id of the given node"""
    return element.attrib["{http://www.w3.org/XML/1998/namespace}id"]


def crate_tag_whitelist(element: ET.Element, tag_blacklist: list) -> list:
    """lists all unique elements from a given node and returns only those not in the given blacklist"""
    tags = list(
        set([x.tag for x in element.iter(tag=ET.Element) if x.tag not in tag_blacklist])
    )
    return tags


def extract_fulltext(root_node: ET.Element, tag_blacklist: list = []) -> str:
    """extracts all fulltext from given element and its children, except from blacklisted elements"""
    tags = crate_tag_whitelist(root_node, tag_blacklist)
    full_text = " ".join("".join(root_node.itertext(*tags)).split())
    return full_text


def check_for_hash(value: str) -> str:
    """checks if value starts with '#' and if so removes the '#' from the returned value"""
    if value.startswith("#"):
        return value[1:]
    else:
        return value


def add_graphic_url_to_pb(doc: TeiReader) -> TeiReader:
    """writes url attributes into tei:pb elements fetched from matching tei:surface//tei:graphic[1] elements"""
    for x in doc.any_xpath(".//tei:pb[@facs]"):
        facs_id = check_for_hash(x.attrib["facs"])
        xpath_expr = f'.//tei:surface[@xml:id="{facs_id}"]//tei:graphic[1]/@url'
        try:
            facs_url = doc.any_xpath(xpath_expr)[0]
        except IndexError:
            continue
        x.attrib["url"] = facs_url
    return doc


def get_birth_death_year(
    person_node: ET.Element, xpath_part: str = "@when", birth: bool = True
) -> Union[int, bool]:
    """tries to extract birth and death years from person nodes and returns either None or the year as Integer"""
    if birth:
        year_xpath = f"./tei:birth/{xpath_part}"
    else:
        year_xpath = f"./tei:death/{xpath_part}"
    try:
        date_str = person_node.xpath(
            year_xpath, namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
        )[0]
    except IndexError:
        return None
    year_str = date_str[:4]
    try:
        return int(year_str)
    except ValueError:
        return None


def previous_and_next(some_iterable):  # pragma: no cover
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
