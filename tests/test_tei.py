#!/usr/bin/env python

"""Tests for `acdh_tei_pyutils.tei` module."""

import glob
import unittest
import lxml.etree as ET
from acdh_tei_pyutils.tei import NER_TAG_MAP, TeiReader, TeiEnricher, HandleAlreadyExist
from acdh_tei_pyutils.utils import (
    normalize_string,
    make_entity_label,
    get_birth_death_year,
    check_for_hash,
    add_graphic_url_to_pb,
    extract_fulltext,
    get_xmlid,
)


FILES = sorted(glob.glob("./acdh_tei_pyutils/files/*.xml", recursive=False))

XSL = glob.glob("./acdh_tei_pyutils/files/*.xsl", recursive=False)[0]

IDS_AND_SO = [
    ["base_value", "id_value", "prev_value", "next_value"],
    [None, None, None, None],
    ["base_value", "id_value", None, None],
    ["base_value/", "id_value", "prev_value", "next_value"],
]
FULL_IDS = ["base_value/id_value", None, "base_value/id_value", "base_value/id_value"]


class TestTeiEnricher(unittest.TestCase):
    """Tests for `acdh_tei_pyutils.tei.TeiEnricher` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_001_init(self):
        for x in FILES:
            doc = TeiEnricher(xml=x)
            self.assertIsInstance(doc.return_string(), str)

    def test_002_add_context(self):  # ToDo: check for ordering of files
        dummy_data = zip(FILES, IDS_AND_SO, FULL_IDS)
        for x in dummy_data:
            doc = TeiEnricher((x[0]))
            doc.add_base_and_id(*x[1])
            full_id = doc.get_full_id()
            self.assertEqual(full_id, x[2])

    def test_003_handle_exist(self):
        hdl_doc = TeiEnricher(xml="./acdh_tei_pyutils/files/tei.xml")
        self.assertIn("http", hdl_doc.handle_exist())
        hdl_no = TeiEnricher(xml="./acdh_tei_pyutils/files/tei_no_id.xml")
        self.assertIsNone(hdl_no.handle_exist())

    def test_004_add_handle(self):
        hdl_doc = TeiEnricher(xml="./acdh_tei_pyutils/files/tei.xml")
        self.assertRaises(HandleAlreadyExist, lambda: hdl_doc.add_handle("1234/5432"))
        hdl_no = TeiEnricher(xml="./acdh_tei_pyutils/files/tei_no_id.xml")
        handle_node = hdl_no.add_handle("1234/5432")
        self.assertEqual(handle_node.text, "1234/5432")
        self.assertEqual(hdl_no.handle_exist(), "1234/5432")


class TestTEIReader(unittest.TestCase):
    """Tests for `acdh_tei_pyutils.tei.TeiReader` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_001_ner_mapping(self):
        self.assertIsInstance(NER_TAG_MAP, dict)

    def test_002_parsing_from_file(self):
        for x in FILES:
            doc = TeiReader(xml=x)
            parent_node = doc.any_xpath(any_xpath="//tei:body")[0]
            ne_list = doc.extract_ne_elements(parent_node)
            self.assertIsInstance(ne_list, list)

    def test_003_extract_ner_list(self):
        doc = TeiReader(xml=FILES[0])
        ne_list = doc.get_text_nes_list()
        self.assertIsInstance(ne_list, list)
        self.assertTrue(len(ne_list), 2)

    def test_004_check_ner_list(self):
        doc = TeiReader(xml=FILES[0])
        ne_list = doc.get_text_nes_list()
        for y in ne_list:
            print(y)
            if y["ner_dicts"]:
                self.assertTrue(
                    y["ner_dicts"][0]["text"] in ["Prag", "Broschüre", "Böhmen"]
                )

    def test_005_ner_offsets(self):
        doc = TeiReader(xml=FILES[0])
        ne_offsets = doc.extract_ne_offsets()
        print(ne_offsets[2])
        self.assertIsInstance(ne_offsets, list)

    def test_006_markup_cleanup(self):
        doc = TeiReader(xml=FILES[0])
        ent_list = doc.get_elements()
        self.assertTrue("{http://www.tei-c.org/ns/1.0}unclear" in ent_list)
        doc = TeiReader(xml=FILES[0], xsl=XSL)
        ent_list = doc.get_elements()
        self.assertFalse("{http://www.tei-c.org/ns/1.0}unclear" in ent_list)

    def test_007_normalize_string(self):
        string = """\n\nhallo
mein schatz ich liebe    dich
    du bist         die einzige für mich
        """
        normalized = normalize_string(string)
        self.assertTrue("\n" not in normalized)

    def test_008_make_pers_name_labels(self):
        test_names = """
<TEI xmlns="http://www.tei-c.org/ns/1.0" >
    <back>
        <persName>
            <forename>Johann</forename>
            <surname>Thayer</surname>
        </persName>
        <orgName>orgName</orgName>
        <placeName>PlaceName</placeName>
        <persName>
            <forename>Josef</forename>
            <forename type="taken" subtype="later">Karl</forename>
            <surname>Crcil</surname>
            <surname type="taken" subtype="later">Graf</surname>
        </persName>
        <persName></persName>
        <persName>
            <forename>NurVorname</forename>
        </persName>
        <persName xml:lang="de">
            <surname>NurNachname</surname>
            <forename></forename>
        </persName>
    </back>
</TEI>
"""
        labels = [
            "Thayer, Johann",
            "orgName",
            "PlaceName",
            "Crcil, Josef Karl",
            "no label provided",
            "NurVorname",
            "NurNachname",
        ]
        doc = TeiReader(test_names)
        for i, x in enumerate(doc.any_xpath(".//tei:back/*")):
            label, lang = make_entity_label(x, default_lang="en")
            self.assertEqual(label, labels[i])
        self.assertEqual(lang, "de")

    def test_009_birth_death_year(self):
        test_str = """
<listPerson xmlns="http://www.tei-c.org/ns/1.0">
    <person>
        <birth when-iso="1983-08-04"></birth>
    </person>
    <person>
        <death when="1982-08-04"></death>
    </person>
    <person>
        <death when="foo"></death>
        <birth when-iso="bar"></birth>
    </person>
    </listPerson>
"""
        doc = TeiEnricher(test_str)
        results = set()
        for x in doc.any_xpath(".//tei:person"):
            birth_year = get_birth_death_year(x, xpath_part="@when-iso")
            death_year = get_birth_death_year(x, birth=False)
            results.add(birth_year)
            results.add(death_year)
        self.assertTrue(1982 in results)
        self.assertTrue(1983 in results)
        self.assertTrue(None in results)

    def test_010_check_for_hash(self):
        test_values = ["#hansi", "hansi"]
        for x in test_values:
            checked = check_for_hash(x)
            self.assertEqual(checked, "hansi")

    def test_011_pb_facs_uris(self):
        test_str = """
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <facsimile>
        <surfaceGrp>
            <surface type="recto" xml:id="D_000002-003-000-facs001-l001-p001">
                <graphic ana="status:checked" source="wienbibliothek"
                url="https://www.digital.wienbibliothek.at/wbrobv02/i3f/v21/2540032/full/full/0/default.jpg"/>
            </surface>
            <surface type="verso" xml:id="D_000002-003-000-facs001-l001-p002">
                <graphic ana="status:checked" source="wienbibliothek"
                url="https://www.digital.wienbibliothek.at/wbrobv02/i3f/v21/2540034/full/full/0/default.jpg"/>
            </surface>
        </surfaceGrp>
    </facsimile>
    <pb facs="#D_000002-003-000-facs001-l001-p001" n="1"/>
    <pb facs="#D_000002-003-000-facs001-l001-p002" n="2"/>
    <pb facs="#D_000002-003-000-facs001-l001-p003" n="2"/>
</TEI>
"""
        doc = TeiReader(test_str)
        new_doc = add_graphic_url_to_pb(doc)
        graphic_urls = new_doc.any_xpath(".//tei:graphic/@url")
        pb_urls = new_doc.any_xpath(".//tei:pb/@url")
        for x in pb_urls:
            self.assertTrue(x in graphic_urls)

    def test_012_extract_fulltext(self):
        test_str = """
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <body>
    <lb n="N001"/>Durchleücht<supplied>i</supplied>ger Curfü<supplied>r</supplied>st,
    mein herzallerlibster <choice><expan>herr</expan><abbr>h</abbr></choice> bruder
      <lb n="N002"/>Ich kom nuhr in eil, dero Liebden zu participiren die victori,
      <lb n="N003"/>so <choice><expan>Prinz</expan><abbr>P</abbr></choice> Eugen
      in Italien gehabt. Ist sehr scharf
      <lb n="N004"/>her gangen, der <choice><expan>Prinz</expan><abbr>Pz</abbr></choice>
      ist durch den hals geschoßen, <choice><expan>Prinz</expan><abbr>Pr</abbr></choice> Joseph
      <lb n="N005"/>auch durch die wang, aber bede gottlob ohn gefahr,
    </body>
</TEI>
"""
        doc = TeiReader(test_str)
        body = doc.any_xpath(".//tei:body")[0]
        ft = extract_fulltext(body)
        self.assertTrue("PrinzPz" in ft)
        ft = extract_fulltext(body, tag_blacklist=["{http://www.tei-c.org/ns/1.0}abbr"])
        self.assertFalse("PrinzPz" in ft)

    def test_013_get_xmlid(self):
        node = ET.Element("{http://www.tei-c.org/ns/1.0}person")
        node.attrib["{http://www.w3.org/XML/1998/namespace}id"] = "foo"
        xml_id = get_xmlid(node)
        self.assertEqual("foo", xml_id)
