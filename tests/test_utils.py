"""Tests for `acdh_tei_pyutils.utils` module."""

import unittest

import lxml.etree as ET

from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext_with_spacing, make_bibl_label


class TestTeiEnricher(unittest.TestCase):
    def test_001(self):
        doc = TeiReader("tests/listbibl_test.xml")
        for x in doc.any_xpath(".//tei:biblStruct[@xml:id]"):
            label = make_bibl_label(x, max_title_length=50)
            n = x.attrib["n"]
            self.assertEqual(label, n)

    def test_extract_fulltext_with_spacing(self):
        """Test extract_fulltext_with_spacing with TEI namespace XML"""
        # Create a sample TEI XML document
        tei_ns = "http://www.tei-c.org/ns/1.0"
        xml_str = f"""
        <TEI xmlns="{tei_ns}">
            <text>
                <body>
                    <div>
                        <head>Test Header</head>
                        <p>This is a paragraph with <emph>emphasis</emph> in it.</p>
                        <p>Another paragraph here.</p>
                        <salute>Best regards</salute>
                        <closer>The Author</closer>
                    </div>
                </body>
            </text>
        </TEI>
        """
        root = ET.fromstring(xml_str.encode("utf-8"))

        # Test basic extraction
        result = extract_fulltext_with_spacing(root)
        self.assertIn("Test Header", result)
        self.assertIn("This is a paragraph with emphasis in it.", result)
        self.assertIn("Another paragraph here.", result)
        self.assertIn("Best regards", result)
        self.assertIn("The Author", result)

        # Test with blacklist
        result_blacklist = extract_fulltext_with_spacing(root, tag_blacklist=["closer"])
        self.assertNotIn("The Author", result_blacklist)
        self.assertIn("Test Header", result_blacklist)

    def test_extract_fulltext_with_spacing_space_elements(self):
        """Test extract_fulltext_with_spacing with space elements"""
        tei_ns = "http://www.tei-c.org/ns/1.0"
        xml_str = f"""
        <TEI xmlns="{tei_ns}">
            <text>
                <body>
                    <p>Word1<space unit="chars"/>Word2</p>
                </body>
            </text>
        </TEI>
        """
        root = ET.fromstring(xml_str.encode("utf-8"))
        result = extract_fulltext_with_spacing(root)

        # Should have space between Word1 and Word2
        self.assertIn("Word1", result)
        self.assertIn("Word2", result)
        # Verify words are separated
        self.assertTrue(
            "Word1 Word2" in result or "Word1  Word2" in result.replace("  ", " ")
        )
