"""Tests for `acdh_tei_pyutils.utils` module."""

import unittest

from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import make_bibl_label


class TestTeiEnricher(unittest.TestCase):
    def test_001(self):
        doc = TeiReader("tests/listbibl_test.xml")
        for x in doc.any_xpath(".//tei:biblStruct[@xml:id]"):
            label = make_bibl_label(x, max_title_length=50)
            n = x.attrib["n"]
            self.assertEqual(label, n)
