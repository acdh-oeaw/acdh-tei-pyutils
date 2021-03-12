import re
from acdh_xml_pyutils.xml import XMLReader

NER_TAG_MAP = {
    "persName": "PER",
    "person": "PER",
    "placeName": "LOC",
    "place": "LOC",
    "orgName": "ORG",
    "org": "ORG",
    "work": "WORK",
    "workName": "WORK",
    "name": "NAME"
}


class TeiReader(XMLReader):

    """ a class to read an process tei-documents"""

    def any_xpath(self, any_xpath='//tei:rs'):

        """ Runs any xpath expressions against the parsed document
        :param any_xpath: Any XPath expression.
        :return: The result of the xpath
        """
        return self.tree.xpath(any_xpath, namespaces=self.ns_tei)

    def extract_ne_elements(self, parent_node, ne_xpath='//tei:rs'):

        """ extract elements tagged as named entities
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.
        :return: A list of elements
        """

        ne_elements = parent_node.xpath(ne_xpath, namespaces=self.ns_tei)
        return ne_elements
    
    def extract_ne_dicts(self, parent_node, ne_xpath='//tei:rs', NER_TAG_MAP=NER_TAG_MAP):

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
            text = "".join(x.xpath('.//text()'))
            item['text'] = re.sub('\s+', ' ', text).strip()
            try:
                ne_type = NER_TAG_MAP.get("{}".format(x.xpath('./@type')[0]), 'MISC')
            except IndexError as e:
                ne_type = NER_TAG_MAP.get("{}".format(x.xpath("name()")), 'MISC')
            item['ne_type'] = ne_type
            ne_dicts.append(item)

        return ne_dicts