from lxml import etree as ET
import re
from acdh_xml_pyutils.xml import XMLReader
from slugify import slugify


class HandleAlreadyExist(Exception):
    pass


NER_TAG_MAP = {
    "persName": "PER",
    "person": "PER",
    "placeName": "LOC",
    "place": "LOC",
    "orgName": "ORG",
    "org": "ORG",
    "work": "WORK",
    "workName": "WORK",
    "bibl": "WORK",
    "name": "NAME",
    "date": "DATE",
    "time": "TIME",
}


class TeiReader(XMLReader):
    """a class to read an process tei-documents"""

    def any_xpath(self, any_xpath="//tei:rs"):
        """Runs any xpath expressions against the parsed document
        :param any_xpath: Any XPath expression.
        :return: The result of the xpath
        """
        return self.tree.xpath(any_xpath, namespaces=self.ns_tei)

    def extract_ne_elements(self, parent_node, ne_xpath="//tei:rs"):
        """extract elements tagged as named entities
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.
        :return: A list of elements
        """

        ne_elements = parent_node.xpath(ne_xpath, namespaces=self.ns_tei)
        return ne_elements

    def extract_ne_dicts(
        self, parent_node, ne_xpath="//tei:rs", NER_TAG_MAP=NER_TAG_MAP
    ):
        """ extract strings tagged as named entities
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.
        :param NER_TAG_MAP: A dictionary providing mapping from TEI tags used to tag NEs to\
        spacy-tags
        :return: A list of NE-dicts containing the 'text' and the 'ne_type'
        """

        ne_elements = self.extract_ne_elements(parent_node, ne_xpath)
        ne_dicts = []
        for x in ne_elements:
            item = {}
            text = "".join(x.xpath(".//text()"))
            item["text"] = re.sub(r"\s+", " ", text).strip()
            try:
                ne_type = NER_TAG_MAP.get("{}".format(x.xpath("./@type")[0]), "MISC")
            except IndexError:
                ne_type = NER_TAG_MAP.get("{}".format(x.xpath("name()")), "MISC")
            item["ne_type"] = ne_type
            ne_dicts.append(item)

        return ne_dicts

    def create_plain_text(self, node):
        """ extracts all text nodes from given element
        :param start_node: An XPath expressione pointing to\
        an element which text nodes should be extracted
        :return: A normalized, cleaned plain text
        """
        result = re.sub(r"\s+", " ", "".join(node.xpath(".//text()"))).strip()

        return result

    def get_text_nes_list(
        self,
        parent_nodes=".//tei:body//tei:p",
        ne_xpath=".//tei:rs",
        NER_TAG_MAP=NER_TAG_MAP,
    ):
        """ extracts all text nodes from given elements and their NE
        :param parent_nodes: An XPath expressione pointing to\
        those elements which text nodes should be extracted
        :param ne_xpath:  An XPath expression pointing to elements used to tagged NEs.\
        Takes the parent node(s) as context
        :param NER_TAG_MAP: A dictionary providing mapping from TEI tags used to tag NEs to\
        spacy-tags
        :return: A list of dicts like [{"text": "Wien ist schön", "ner_dicts": [{"text": "Wien",\
        "ne_type": "LOC"}]}]
        """

        parents = self.tree.xpath(parent_nodes, namespaces=self.ns_tei)
        result = []
        for node in parents:
            text = self.create_plain_text(node)
            ner_dicts = self.extract_ne_dicts(node, ne_xpath, NER_TAG_MAP)
            result.append({"text": text, "ner_dicts": ner_dicts})
        return result

    def extract_ne_offsets(
        self,
        parent_nodes=".//tei:body//tei:p",
        ne_xpath=".//tei:rs",
        NER_TAG_MAP=NER_TAG_MAP,
    ):
        """ extracts offsets of NEs and the NE-type
        :param parent_nodes: An XPath expressione pointing to\
        those element which text nodes should be extracted
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.\
        Takes the parent node(s) as context
        :param NER_TAG_MAP: A dictionary providing mapping from TEI tags used to tag NEs to\
        spacy-tags
        :return: A list of spacy-like NER Tuples [('some text'), {'entities': [(15, 19, 'place')]}]
        """

        text_nes_dict = self.get_text_nes_list(parent_nodes, ne_xpath, NER_TAG_MAP)
        result = []
        for x in text_nes_dict:
            plain_text = x["text"]
            ner_dicts = x["ner_dicts"]
            entities = []
            for x in ner_dicts:
                if x["text"] != "":
                    for m in re.finditer(re.escape(x["text"]), plain_text):
                        entities.append([m.start(), m.end(), x["ne_type"]])
            entities = [item for item in set(tuple(row) for row in entities)]
            entities = sorted(entities, key=lambda x: x[0])
            ents = []
            next_item_index = 1
            # remove entities with the same start offset
            for x in entities:
                cur_start = x[0]
                try:
                    next_start = entities[next_item_index][0]
                except IndexError:
                    next_start = 9999999999999999999999
                if cur_start == next_start:
                    pass
                else:
                    ents.append(x)
                next_item_index = next_item_index + 1

            train_data = (plain_text, {"entities": ents})
            result.append(train_data)
        return result


class TeiEnricher(TeiReader):
    """a class to enrich tei-documents"""

    def add_base_and_id(self, base_value, id_value, prev_value, next_value):
        """adds @xml:base and @xml:id and next and prev to root element

        :param base_value: The value of the @xml:base
        :type base_value: str

        :return: the updated tree
        """

        base = self.any_xpath("//tei:TEI")[0]
        if base_value:
            base.set(f"{{{self.ns_xml['xml']}}}base", base_value)
        if id_value:
            base.set(f"{{{self.ns_xml['xml']}}}id", id_value)
        if prev_value:
            base.set("prev", f"{base_value}/{prev_value}")
        if next_value:
            base.set("next", f"{base_value}/{next_value}")
        return self.tree

    def get_full_id(self):
        """returns the combination of @xml:base and @xml:id

        :return: combination of @xml:base and @xml:id
        :rtype: str

        """
        base = self.any_xpath("//tei:TEI")[0]
        try:
            base_base = base.xpath("./@xml:base", namespaces=self.ns_xml)[0]
        except IndexError:
            return None
        try:
            base_id = base.xpath("./@xml:id", namespaces=self.ns_xml)[0]
        except IndexError:
            return None
        if base_base.endswith("/"):
            return f"{base_base}{base_id}"
        else:
            return f"{base_base}/{base_id}"

    def handle_exist(self, handle_xpath='.//tei:idno[@type="handle"]'):
        """checks if a handle is already assigned

        :return: the registered handle or empty string
        :rtype: str, None
        """
        try:
            return self.any_xpath(handle_xpath)[0].text
        except IndexError:
            return None

    def add_handle(
        self,
        handle,
        handle_xpath='.//tei:idno[@type="handle"]',
        insert_xpath=".//tei:publicationStmt/tei:p",
    ):
        """adds an idno @type=handle element into tei:publicationStmt

        :param handle: the handle
        :type handle: str

        :param handle_xpath: an xpath expression where to look for an handle
        :type handle_xpath: str

        :raises: `HandleAlreadyExist` Error

        :returns: the indo node
        """
        tei_ns = f"{self.ns_tei['tei']}"
        if self.handle_exist(handle_xpath=handle_xpath):
            raise HandleAlreadyExist(
                f"a handle: {self.handle_exist()} is already registered"
            )
        else:
            idno_node = ET.Element(f"{{{tei_ns}}}idno")
            idno_node.set("type", "handle")
            idno_node.text = handle
            insert_node = self.any_xpath(insert_xpath)[0]
            insert_node.append(idno_node)
            return idno_node

    def create_mention_list(self, mentions, event_title=""):
        """creates a tei element with notes of mentions

        :param mentions: a list of dicts with keys `doc_id` and `doc_title`
        :type mentions: noteGrp

        :return: a etree.element
        """
        tei_ns = f"{self.ns_tei['tei']}"
        node_root = ET.Element(f"{{{tei_ns}}}noteGrp")
        mentions_added = {}
        for x in mentions:
            try:
                mentions_added[slugify(x["doc_id"])]
            except KeyError:
                note = ET.Element(f"{{{tei_ns}}}note")
                note.attrib["target"] = x["doc_id"]
                note.attrib["type"] = "mentions"
                if x["doc_date"] is not None:
                    note.attrib["corresp"] = x["doc_date"]
                if x["doc_title_sec"] is not None:
                    note.text = event_title + f"{x['doc_title']} {x['doc_title_sec']}"
                else:
                    note.text = x["doc_title"]
                node_root.append(note)
                mentions_added[slugify(x["doc_id"])] = True
        return node_root
