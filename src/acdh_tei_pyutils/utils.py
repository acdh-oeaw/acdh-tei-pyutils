import re
from itertools import chain, islice, tee
from typing import Union

import lxml.etree as ET

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
    """removese any superfluos whitespace from a given string"""
    return " ".join(" ".join(string.split()).split())


def make_entity_label(
    name_node: ET.Element, default_msg="no label provided", default_lang="en"
) -> tuple[str, str]:
    """Extracts a label and a lang tag from the past in name-node

    Args:
        name_node (ET.Element): A tei:persName|placeName|orgName element
        default_msg (str, optional): some default vaule for the label.
        default_lang (str, optional): some default lang tag if the node does not provide and xml:lang attribute".

    Returns:
        tuple[str, str]: returns the extracted label and a lang tag
    """

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


def make_bibl_label(
    node: ET.Element,
    no_author="o.A.",
    no_title="o.T.",
    year="o.J.",
    editor_abbr="(Hg.)",
    max_title_length=75,
) -> str:
    """creates a nice, bibliograhpically useful label from the passed in tei:biblStruct element

    Args:
        node (ET.Element): a tei:biblStruct element
        no_author (str, optional): Used if no author name can be extracted. Defaults to "o.A".
        no_title (str, optional): Used if no title can be extracted. Defaults to "o.T".
        year (str, optional): Used if no year can be extracted. Defaults to "o.J".
        editor_abbr(str, optional): how to mark the 'author' beeing an editor. Defaults to "(Hg.)".
        max_title_length(int, optional): max lenght for the title before it gets truncated. Defaults to

    Returns:
        str: _description_
    """
    try:
        author = node.xpath(".//tei:author[1]/tei:surname[1]", namespaces=nsmap)[0].text
    except IndexError:
        try:
            author = node.xpath(".//tei:author[1]/tei:name[1]", namespaces=nsmap)[
                0
            ].text
        except IndexError:
            try:
                author = node.xpath(
                    ".//tei:editor[1]/tei:surname[1]", namespaces=nsmap
                )[0].text
                author = f"{author} {editor_abbr}"
            except IndexError:
                try:
                    author = node.xpath(
                        ".//tei:editor[1]/tei:name[1]", namespaces=nsmap
                    )[0].text
                    author = f"{author} {editor_abbr}"
                except IndexError:
                    author = no_author
    try:
        year = node.xpath(".//tei:date[1]", namespaces=nsmap)[0].text
    except IndexError:
        year = year
    title = node.xpath(".//tei:title[1]", namespaces=nsmap)[0].text
    if title:
        if len(title) > max_title_length:
            title = f"{title[:max_title_length]}..."
    else:
        title = no_title
    return f"{author}, {title}, {year}"


def extract_fulltext_with_spacing(
    root_node,
    tag_blacklist=None,
    block_elements=[
        "p",
        "salute",
        "dateline",
        "closer",
        "seg",
        "opener",
        "div",
        "head",
    ],
):
    """
    Extract full text content from an XML element tree with proper spacing.
    This function recursively traverses an XML element tree and extracts all text
    content while preserving logical spacing around block-level elements. It handles
    XML namespaces and respects a blacklist of elements to exclude from extraction.
    Taken from https://github.com/arthur-schnitzler/schnitzler-briefe-static/blob/main/python/make_typesense_index.py
    Args:
        root_node: The root XML element from which to extract text.
        tag_blacklist (list, optional): A list of element tag names to exclude from
            text extraction. Elements with tags in this list will be skipped entirely.
            Defaults to None (empty list).
        block_elements (tuple, optional): A tuple of tag names that should have spaces
            added around them. Defaults to ('p', 'salute', 'dateline', 'closer', 'seg',
            'opener', 'div', 'head').
    Returns:
        str: The extracted text with normalized spacing. Multiple consecutive
            whitespace characters are collapsed into a single space, and the
            result is stripped of leading/trailing whitespace.
    Notes:
        - Handles XML namespaced tags by extracting the local name (part after '}').
        - Special handling for 'space' elements with unit='chars' attribute.
        - Preserves tail text from child elements.
        - Automatically collapses multiple spaces into single spaces using regex.
    """

    if tag_blacklist is None:
        tag_blacklist = []

    def extract_text_recursive(element):
        try:
            if hasattr(element.tag, "split"):
                element_tag_name = element.tag.split("}")[-1]
            else:
                element_tag_name = str(element.tag).split("}")[-1]
        except (AttributeError, TypeError):
            element_tag_name = ""

        if element_tag_name in tag_blacklist:
            return ""

        text_parts = []

        if element.text:
            text_parts.append(element.text)

        # Process children
        for child in element:
            try:
                if hasattr(child.tag, "split"):
                    tag_name = child.tag.split("}")[-1]  # Remove namespace
                else:
                    tag_name = str(child.tag).split("}")[-1]
            except (AttributeError, TypeError):
                # Skip if we can't determine the tag name
                if hasattr(child, "tail") and child.tail:
                    text_parts.append(child.tail)
                continue

            # Handle space elements
            if tag_name == "space":
                unit = child.get("unit", "")
                if unit == "chars":
                    # Add space for char-based spacing elements
                    text_parts.append(" ")
                # Add tail text before continuing
                if child.tail:
                    text_parts.append(child.tail)
                continue

            # Add space before block elements
            if tag_name in block_elements:
                text_parts.append(" ")

            # Process child recursively
            child_text = extract_text_recursive(child)
            if child_text:
                text_parts.append(child_text)

            # Add space after block elements
            if tag_name in block_elements:
                text_parts.append(" ")

            # Add tail text
            if child.tail:
                text_parts.append(child.tail)

        return "".join(text_parts)

    result = extract_text_recursive(root_node)
    result = re.sub(r"\s+", " ", result).strip()
    return result
