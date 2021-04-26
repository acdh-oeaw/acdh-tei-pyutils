#!/usr/bin/env python

"""Tests for `acdh_tei_pyutils.tei` module."""

import glob
import unittest

from acdh_tei_pyutils.tei import (
    NER_TAG_MAP, TeiReader, TeiEnricher,
    HandleAlreadyExist
)


FILES = glob.glob(
    "./acdh_tei_pyutils/files/*.xml",
    recursive=False
)

XSL = glob.glob(
    "./acdh_tei_pyutils/files/*.xsl",
    recursive=False
)[0]

IDS_AND_SO = [
    ['base_value', 'id_value', 'prev_value', 'next_value'],
    ['base_value', 'id_value', None, None],
    ['base_value/', 'id_value', 'prev_value', 'next_value'],
    [None, None, None, None]
]
FULL_IDS = [
    'base_value/id_value',
    'base_value/id_value',
    'base_value/id_value',
    None
]


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
    
    # def test_002_add_context(self): # ToDo: check for ordering of files
    #     dummy_data = zip(FILES, IDS_AND_SO, FULL_IDS)
    #     for x in dummy_data:
    #         doc = TeiEnricher((x[0]))
    #         doc.add_base_and_id(*x[1])
    #         full_id = doc.get_full_id()
    #         self.assertEqual(full_id, x[2])
    
    def test_003_handle_exist(self):
        hdl_doc = TeiEnricher(xml='./acdh_tei_pyutils/files/tei.xml')
        self.assertIn('http', hdl_doc.handle_exist())
        hdl_no = TeiEnricher(xml='./acdh_tei_pyutils/files/tei_no_id.xml')
        self.assertIsNone(hdl_no.handle_exist())
    
    def test_004_add_handle(self):
        hdl_doc = TeiEnricher(xml='./acdh_tei_pyutils/files/tei.xml')
        self.assertRaises(HandleAlreadyExist, lambda: hdl_doc.add_handle('1234/5432'))
        hdl_no = TeiEnricher(xml='./acdh_tei_pyutils/files/tei_no_id.xml')
        handle_node = hdl_no.add_handle('1234/5432')
        self.assertEqual(handle_node.text, '1234/5432')
        self.assertEqual(hdl_no.handle_exist(), '1234/5432')


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
