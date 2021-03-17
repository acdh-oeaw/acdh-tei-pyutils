#!/usr/bin/env python

"""Tests for `acdh_tei_pyutils.tei` module."""

import glob
import unittest

from acdh_tei_pyutils.tei import NER_TAG_MAP, TeiReader


FILES = glob.glob(
    "./acdh_tei_pyutils/files/*.xml",
    recursive=False
)

XSL = glob.glob(
    "./acdh_tei_pyutils/files/*.xsl",
    recursive=False
)[0]


class TestTEIReader(unittest.TestCase):
    """Tests for `acdh_tei_pyutils.tei.TEIReader` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_001_ner_mapping(self):
        self.assertIsInstance(NER_TAG_MAP, dict)

    def test_002_parsing_from_file(self):
        for x in FILES:
            doc = TeiReader(xml=x)
            parent_node = doc.any_xpath(any_xpath='//tei:body')[0]
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
            if y['ner_dicts']:
                self.assertTrue(
                    y['ner_dicts'][0]['text'] in ["Prag", "Broschüre", "Böhmen"]
                )

    def test_005_ner_offsets(self):
        doc = TeiReader(xml=FILES[0])
        ne_offsets = doc.extract_ne_offsets()
        print(ne_offsets[2])
        self.assertIsInstance(ne_offsets, list)

    def test_006_markup_cleanup(self):
        doc = TeiReader(xml=FILES[0])
        ent_list = doc.get_elements()
        self.assertTrue('{http://www.tei-c.org/ns/1.0}unclear' in ent_list)
        doc = TeiReader(xml=FILES[0], xsl=XSL)
        ent_list = doc.get_elements()
        self.assertFalse('{http://www.tei-c.org/ns/1.0}unclear' in ent_list)
