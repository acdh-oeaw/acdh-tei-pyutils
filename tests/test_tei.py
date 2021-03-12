#!/usr/bin/env python

"""Tests for `acdh_tei_pyutils.tei` module."""

import glob
import os
import unittest

from acdh_tei_pyutils.tei import NER_TAG_MAP, TeiReader


FILES = glob.glob(
    "./acdh_tei_pyutils/files/*.xml",
    recursive=False
)


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
    
    def test_002_parsing_from_file(self):
        for x in FILES:
            doc = TeiReader(xml=x)
            parent_node = doc.any_xpath(any_xpath='//tei:body')[0]
            ne_list = doc.extract_ne_dicts(parent_node)
            self.assertIsInstance(ne_list, list)
            