import os
import unittest
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.cli import mentions_to_indices


class MentionsToIndex(unittest.TestCase):
    """Tests for `acdh_tei_pyutils.mentions_to_index` function."""

    def setUp(self):
        """Set up test fixtures, if any."""
        print("setting up files")
        self.ref_event_text = "REF EVENT TEXT"
        self.mention_xpath = "//tei:rs/@ref"
        self.title_xpath = "//tei:title"
        self.test_path = "/tmp/acdh_pyutil_cli_test"
        self.editions_path = f"{self.test_path}/editions/"
        self.indices_path = f"{self.test_path}/indices/"
        os.makedirs(self.editions_path, exist_ok=True)
        os.makedirs(self.indices_path, exist_ok=True)
        edition_content = """
    <?xml version='1.0' encoding='UTF-8'?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0" xml:base="." xml:id="fb_17000316_HanssGeorgWagner.xml">
        <body>
            <title>test document</title>
            <rs ref="#test_person">Maxi Muster</rs>
        </body>
    </TEI>
"""
        pers_index_content = """
    <?xml version='1.0' encoding='UTF-8'?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0" xml:base="." xml:id="fb_17000316_HanssGeorgWagner.xml">
        <body>
            <listPerson>
                <person xml:id="test_person">
                    <persName source="#ignaza112">
                        <forename>
                            Maxi
                        </forename>
                        <surname>
                            Muster
                        </surname>
                    </persName>
                </person>
            </listPerson>
        </body>
    </TEI>
"""
        self.edition_doc = TeiReader(edition_content)
        self.person_index_doc = TeiReader(pers_index_content)
        self.edition_doc_path = self.editions_path + "text_document.xml"
        self.person_index_doc_path = self.indices_path + "persons.index"
        self.edition_doc.tree_to_file(self.edition_doc_path)
        self.edition_doc.tree_to_file(self.person_index_doc_path)

    def tearDown(self):
        """Tear down test fixtures, if any."""
        import shutil

        print("removing files")
        shutil.rmtree(self.test_path)

    def test_001_mentions_to_index(self):
        import click.testing

        runner = click.testing.CliRunner()
        args = f'-f "{self.edition_doc_path}" -i "{self.person_index_doc}"'
        args += f' -m "{self.mention_xpath}" -t "{self.ref_event_text}" -x "{self.title_xpath}"'
        result = runner.invoke(mentions_to_indices, args, catch_exceptions=False)
        print(result.output)
        print(result.exc_info)
        print(result.exception)
        assert result.exception is None
        assert result.exit_code == 0
