"""Console script for acdh_collatex_utils."""

import click
import glob
import os
import tqdm
from collections import defaultdict
from lxml import etree as ET
from acdh_tei_pyutils.tei import TeiEnricher
from acdh_tei_pyutils.utils import previous_and_next

from acdh_handle_pyutils.client import HandleClient

NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}


@click.command()  # pragma: no cover
@click.option(
    "-g", "--glob-pattern", default="./editions/*.xml", show_default=True
)  # pragma: no cover
@click.option("-b", "--base-value")  # pragma: no cover
def add_base_id_next_prev(glob_pattern, base_value):  # pragma: no cover
    """Console script add @xml:base, @xml:id and @prev @next attributes to root element"""
    files = sorted(glob.glob(glob_pattern))

    for prev_value, current, next_value in tqdm.tqdm(
        previous_and_next(files), total=len(files)
    ):
        doc = TeiEnricher(current)
        id_value = os.path.split(current)[1]
        if prev_value:
            prev_id = os.path.split(prev_value)[1]
        else:
            prev_id = None
        if next_value:
            next_id = os.path.split(next_value)[1]
        else:
            next_id = None
        doc.add_base_and_id(base_value, id_value, prev_id, next_id)
        doc.tree_to_file(file=current)


@click.command()  # pragma: no cover
@click.option(
    "-g", "--glob-pattern", default="./editions/*.xml", show_default=True
)  # pragma: no cover
@click.option("-user", "--hdl-user")  # pragma: no cover
@click.option("-pw", "--hdl-pw")  # pragma: no cover
@click.option(
    "-provider",
    "--hdl-provider",
    default="http://pid.gwdg.de/handles/",
    show_default=True,
)  # pragma: no cover
@click.option(
    "-prefix", "--hdl-prefix", default="21.11115", show_default=True
)  # pragma: no cover
@click.option(
    "-resolver", "--hdl-resolver", default="https://hdl.handle.net/", show_default=True
)  # pragma: no cover
@click.option(
    "-hxpath", "--hdl-xpath", default=".//tei:idno[@type='handle']", show_default=True
)  # pragma: no cover
@click.option(
    "-hixpath",
    "--hdlinsert-xpath",
    default=".//tei:publicationStmt/tei:p",
    show_default=True,
)  # pragma: no cover
def add_handles(
    glob_pattern,
    hdl_user,
    hdl_pw,
    hdl_provider,
    hdl_prefix,
    hdl_resolver,
    hdl_xpath,
    hdlinsert_xpath,
):  # pragma: no cover
    """Console script to register handels base on the values of @xml:id and @xml:base"""
    files = sorted(glob.glob(glob_pattern))
    hdl_client = HandleClient(
        hdl_user,
        hdl_pw,
        hdl_provider=hdl_provider,
        hdl_prefix=hdl_prefix,
        hdl_resolver=hdl_resolver,
    )
    for x in tqdm.tqdm(files, total=len(files)):
        doc = TeiEnricher(x)
        if doc.handle_exist():
            continue
        parsed_data = doc.get_full_id()
        if parsed_data is None:
            continue
        hdl = hdl_client.register_handle(parsed_data)
        print(hdl)
        doc.add_handle(hdl, handle_xpath=hdl_xpath, insert_xpath=hdlinsert_xpath)
        doc.tree_to_file(x)


@click.command()  # pragma: no cover
@click.option(
    "-f", "--files", default="./editions/*.xml", show_default=True
)  # pragma: no cover
@click.option(
    "-i", "--indices", default="./indices/list*.xml", show_default=True
)  # pragma: no cover
@click.option(
    "-m", "--mention-xpath", default=".//tei:rs[@ref]/@ref", show_default=True
)  # pragma: no cover
@click.option(
    "-t", "--event-title", default="erwähnt in ", show_default=True
)  # pragma: no cover
@click.option(
    "-x",
    "--title-xpath",
    default='.//tei:title[@type="main"]/text()',
    show_default=True,
)  # pragma: no cover
def mentions_to_indices(
    files, indices, mention_xpath, event_title, title_xpath
):  # pragma: no cover
    """Console script write pointers to mentions in index-docs"""
    files = sorted(glob.glob(files))
    index_files = sorted(glob.glob(indices))
    ref_doc_dict = defaultdict(list)
    doc_ref_dict = defaultdict(list)
    click.echo(
        click.style(f"collecting list of mentions from {len(files)} docs", fg="green")
    )
    for x in tqdm.tqdm(files):
        filename = os.path.split(x)[1]
        doc = TeiEnricher(x)
        doc_base = doc.any_xpath("./@xml:base")[0]
        doc_id = doc.any_xpath("./@xml:id")[0]
        doc_uri = f"{doc_base}/{doc_id}"
        doc_title = doc.any_xpath(title_xpath)[0]
        refs = doc.any_xpath(mention_xpath)
        for ref in set(refs):
            if ref.startswith("#"):
                ref = ref[1:]
            ref_doc_dict[ref].append(
                {
                    "doc_uri": doc_uri,
                    "doc_path": x,
                    "doc_title": doc_title,
                    "doc_id": doc_id,
                    "doc_date": None,
                    "doc_title_sec": None,
                }
            )
            doc_ref_dict[filename].append(ref)
    click.echo(
        click.style(
            f"collected {len(ref_doc_dict.keys())} of mentioned entities from {len(files)} docs",
            fg="green",
        )
    )
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath(".//tei:body//*[@xml:id]")
        for ent in ent_nodes:
            ent_id = ent.xpath("@xml:id", namespaces=doc.nsmap)[0]
            mentions = ref_doc_dict[ent_id]
            ent_name = ent.tag
            note_grp = doc.create_mention_list(mentions, event_title)
            try:
                list(note_grp[0])
                # TEI schema does not allow noteGrp in event after e.g. listPerson, ... so we need to insert it before
                if ent_name == "{http://www.tei-c.org/ns/1.0}event":
                    ent.insert(1, note_grp)
                else:
                    ent.append(note_grp)
            except IndexError:
                pass
        doc.tree_to_file(file=x)

    all_ent_nodes = {}
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath(".//tei:body//*[@xml:id]")
        for ent in ent_nodes:
            all_ent_nodes[ent.xpath("@xml:id")[0]] = ent
    click.echo(click.style("DONE", fg="green"))


@click.command()  # pragma: no cover
@click.option(
    "-f", "--files", default="./editions/*.xml", show_default=True
)  # pragma: no cover
@click.option(
    "-i", "--indices", default="./indices/list*.xml", show_default=True
)  # pragma: no cover
@click.option(
    "-m", "--mention-xpath", default=".//tei:rs[@ref]/@ref", show_default=True
)  # pragma: no cover
@click.option(
    "-x", "--title-xpath", default=".//tei:title/text()", show_default=True
)  # pragma: no cover
@click.option("-xs", "--title-sec-xpath", required=False)  # pragma: no cover
@click.option("-d", "--date-xpath", required=False)  # pragma: no cover
@click.option(
    "-b", "--blacklist-ids", default=[], multiple=True, show_default=True
)  # pragma: no cover
def denormalize_indices(
    files,
    indices,
    mention_xpath,
    title_xpath,
    title_sec_xpath,
    date_xpath,
    blacklist_ids=[],
):  # pragma: no cover
    """Write pointers to mentions in index-docs and copy index entries into docs"""
    files = sorted(glob.glob(files))
    index_files = sorted(glob.glob(indices))
    ref_doc_dict = defaultdict(list)
    doc_ref_dict = defaultdict(list)
    click.echo(
        click.style(f"collecting list of mentions from {len(files)} docs", fg="green")
    )
    for x in tqdm.tqdm(files):
        filename = os.path.split(x)[1]
        if "list" in filename:
            continue
        doc = TeiEnricher(x)
        doc_base = doc.any_xpath("./@xml:base")[0]
        doc_id = doc.any_xpath("./@xml:id")[0]
        doc_uri = f"{doc_base}/{doc_id}"
        try:
            doc_title = doc.any_xpath(title_xpath)[0]
        except IndexError:
            doc_title = f"ERROR in title xpath of file: {doc_id}"
            print(f"ERROR in -x title xpath of file: {doc_id}")
        if title_sec_xpath:
            try:
                doc_title_sec = doc.any_xpath(title_sec_xpath)[0]
            except IndexError:
                doc_title_sec = f"ERROR in -xs secondary title xpath of file: {doc_id}"
                print(f"ERROR in secondary title xpath of file: {doc_id}")
        else:
            doc_title_sec = None
        if date_xpath:
            try:
                doc_date = doc.any_xpath(date_xpath)[0]
            except IndexError:
                doc_date = f"ERROR in date xpath of file: {doc_id}"
                print(f"ERROR in -d date xpath of file: {doc_id}")
        else:
            doc_date = None
        refs = doc.any_xpath(mention_xpath)
        for ref in set(refs):
            if ref.startswith("#") and len(ref.split(" ")) == 1:
                ref = ref[1:]
            if ref.startswith("#") and len(ref.split(" ")) > 1:
                refs = ref.split(" ")
                ref = refs[0]
                ref = ref[1:]
                for r in refs[1:]:
                    ref_doc_dict[r[1:]].append(
                        {
                            "doc_uri": doc_uri,
                            "doc_id": doc_id,
                            "doc_path": x,
                            "doc_title": doc_title,
                            "doc_title_sec": doc_title_sec,
                            "doc_date": doc_date,
                        }
                    )
            ref_doc_dict[ref].append(
                {
                    "doc_uri": doc_uri,
                    "doc_id": doc_id,
                    "doc_path": x,
                    "doc_title": doc_title,
                    "doc_title_sec": doc_title_sec,
                    "doc_date": doc_date,
                }
            )
            doc_ref_dict[filename].append(ref)
    click.echo(
        click.style(
            f"collected {len(ref_doc_dict.keys())} of mentioned entities from {len(files)} docs",
            fg="green",
        )
    )
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath(".//tei:body//*[@xml:id]")
        for ent in ent_nodes:
            ent_id = ent.xpath("@xml:id")[0]
            mention = ref_doc_dict[ent_id]
            if ent_id in blacklist_ids:
                continue
            ent_name = ent.tag
            note_grp = doc.create_mention_list(mention)
            try:
                list(note_grp[0])
                # TEI schema does not allow noteGrp in event after e.g. listPerson, ... so we need to insert it before
                if ent_name == "{http://www.tei-c.org/ns/1.0}event":
                    ent.insert(1, note_grp)
                else:
                    ent.append(note_grp)
            except IndexError:
                pass
        doc.tree_to_file(file=x)

    all_ent_nodes = {}
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath(".//tei:body//*[@xml:id]")
        for ent in ent_nodes:
            all_ent_nodes[ent.xpath("@xml:id")[0]] = ent

    click.echo(
        click.style(
            f"writing {len(all_ent_nodes)} index entries into {len(files)} files",
            fg="green",
        )
    )
    for x in tqdm.tqdm(files):
        try:
            filename = os.path.split(x)[1]
            doc = TeiEnricher(x)
            root_node = doc.any_xpath(".//tei:text")[0]
            for bad in doc.any_xpath(".//tei:back"):
                bad.getparent().remove(bad)
            refs = doc.any_xpath(mention_xpath)
            ent_dict = defaultdict(list)
            for ref in set(refs):
                # print(ref, type(ref))
                if ref.startswith("#") and len(ref.split(" ")) == 1:
                    ent_id = ref[1:]
                elif ref.startswith("#") and len(ref.split(" ")) > 1:
                    refs = ref.split(" ")
                    ref = refs[0]
                    ent_id = ref[1:]
                    for r in refs[1:]:
                        try:
                            index_ent = all_ent_nodes[r[1:]]
                            ent_dict[index_ent.tag].append(index_ent)
                        except KeyError:
                            continue
                else:
                    ent_id = ref
                try:
                    index_ent = all_ent_nodes[ent_id]
                    ent_dict[index_ent.tag].append(index_ent)
                except KeyError:
                    continue
            back_node = ET.Element("{http://www.tei-c.org/ns/1.0}back")
            for key in ent_dict.keys():
                if key.endswith("person"):
                    list_person = ET.Element("{http://www.tei-c.org/ns/1.0}listPerson")
                    back_node.append(list_person)
                    for ent in ent_dict[key]:
                        list_person.append(ent)
                if key.endswith("place"):
                    list_place = ET.Element("{http://www.tei-c.org/ns/1.0}listPlace")
                    back_node.append(list_place)
                    for ent in ent_dict[key]:
                        list_place.append(ent)
                if key.endswith("org"):
                    list_org = ET.Element("{http://www.tei-c.org/ns/1.0}listOrg")
                    back_node.append(list_org)
                    for ent in ent_dict[key]:
                        list_org.append(ent)
                if key.endswith("bibl") or key.endswith("biblStruct"):
                    list_bibl = ET.Element("{http://www.tei-c.org/ns/1.0}listBibl")
                    back_node.append(list_bibl)
                    for ent in ent_dict[key]:
                        list_bibl.append(ent)
                if key.endswith("item"):
                    list_item = ET.Element("{http://www.tei-c.org/ns/1.0}list")
                    back_node.append(list_item)
                    for ent in ent_dict[key]:
                        list_item.append(ent)
                if key.endswith("event"):
                    list_eve = ET.Element("{http://www.tei-c.org/ns/1.0}listEvent")
                    back_node.append(list_eve)
                    for ent in ent_dict[key]:
                        list_eve.append(ent)
            root_node.append(back_node)
            doc.tree_to_file(file=x)
        except Exception as e:
            print(f"failed to process {x} due to {e}")
    click.echo(click.style("DONE", fg="green"))


@click.command()  # pragma: no cover
@click.option(
    "-f", "--files", default="./data/editions/*.xml", show_default=True
)  # pragma: no cover
@click.option(
    "-i", "--indices", default="./data/indices/list*.xml", show_default=True
)  # pragma: no cover
@click.option(
    "-t",
    "--doc-person",
    default="./data/indices/index_person_day.xml",
    show_default=True,
)  # pragma: no cover
@click.option(
    "-t", "--doc-work", default="./data/indices/index_work_day.xml", show_default=True
)  # pragma: no cover
def schnitzler(files, indices, doc_person, doc_work):  # pragma: no cover
    """Console script write pointers to mentions in index-docs"""
    files = sorted(glob.glob(files))
    index_files = sorted(glob.glob(indices))
    doc_person = TeiEnricher(doc_person)
    doc_work = TeiEnricher(doc_work)
    all_ent_nodes = {}
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath(".//tei:body//*[@xml:id]")
        for ent in ent_nodes:
            all_ent_nodes[ent.xpath("@xml:id")[0]] = ent

    no_matches = []
    for x in tqdm.tqdm(files, total=len(files)):
        day = x.split("/")[-1].replace("entry__", "").replace(".xml", "")
        doc = TeiEnricher(x)
        root_node = doc.any_xpath(".//tei:text")[0]
        back_node = ET.Element("{http://www.tei-c.org/ns/1.0}back")
        for bad in doc.any_xpath(".//tei:back"):
            bad.getparent().remove(bad)

        xpath = f".//item[@target='{day}']/ref/text()"
        ids = doc_person.any_xpath(xpath)
        list_person_node = ET.Element("{http://www.tei-c.org/ns/1.0}listPerson")
        if len(ids) > 0:
            for id in ids:
                try:
                    nodes = all_ent_nodes[id]
                except KeyError:
                    no_matches.append(id)
                    continue
                list_person_node.append(nodes)
            if len(list_person_node) > 0:
                back_node.append(list_person_node)

        ids = doc_work.any_xpath(xpath)
        list_work_node = ET.Element("{http://www.tei-c.org/ns/1.0}listBibl")
        if len(ids) > 0:
            for id in ids:
                try:
                    nodes = all_ent_nodes[id]
                except KeyError:
                    no_matches.append(id)
                    continue
                list_work_node.append(nodes)
            if len(list_work_node) > 0:
                back_node.append(list_work_node)
        place_ids = doc.any_xpath('.//tei:rs[@ref and @type="place"]/@ref')
        if len(place_ids) > 0:
            list_place_node = ET.Element("{http://www.tei-c.org/ns/1.0}listPlace")
            for pl in place_ids:
                try:
                    pl_node = all_ent_nodes[pl[1:]]
                except KeyError:
                    no_matches.append(pl)
                    continue
                list_place_node.append(pl_node)
            if len(list_place_node) > 0:
                back_node.append(list_place_node)
        if len(back_node) > 0:
            root_node.append(back_node)
            doc.tree_to_file(file=x)
    distinct_no_match = set(no_matches)
    print(distinct_no_match)
