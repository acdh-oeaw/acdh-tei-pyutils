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


@click.command()  # pragma: no cover
@click.option('-g', '--glob-pattern', default='./editions/*.xml', show_default=True)  # pragma: no cover
@click.option('-b', '--base-value')  # pragma: no cover
def add_base_id_next_prev(glob_pattern, base_value):  # pragma: no cover
    """Console script add @xml:base, @xml:id and @prev @next attributes to root element"""
    files = sorted(glob.glob(glob_pattern))

    for prev_value, current, next_value in tqdm.tqdm(previous_and_next(files), total=len(files)):
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
@click.option('-g', '--glob-pattern', default='./editions/*.xml', show_default=True)  # pragma: no cover
@click.option('-user', '--hdl-user')  # pragma: no cover
@click.option('-pw', '--hdl-pw')  # pragma: no cover
@click.option('-provider', '--hdl-provider', default="http://pid.gwdg.de/handles/", show_default=True)  # pragma: no cover
@click.option('-prefix', '--hdl-prefix', default="21.11115", show_default=True)  # pragma: no cover
@click.option('-resolver', '--hdl-resolver', default="https://hdl.handle.net/", show_default=True)  # pragma: no cover
@click.option('-hxpath', '--hdl-xpath', default=".//tei:idno[@type='handle']", show_default=True)  # pragma: no cover
@click.option('-hixpath', '--hdlinsert-xpath', default=".//tei:publicationStmt/tei:p", show_default=True)  # pragma: no cover
def add_handles(glob_pattern, hdl_user, hdl_pw, hdl_provider, hdl_prefix, hdl_resolver, hdl_xpath, hdlinsert_xpath):  # pragma: no cover
    """Console script to register handels base on the values of @xml:id and @xml:base"""
    files = sorted(glob.glob(glob_pattern))
    hdl_client = HandleClient(
        hdl_user, hdl_pw, hdl_provider=hdl_provider, hdl_prefix=hdl_prefix, hdl_resolver=hdl_resolver
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
        doc.add_handle(
            hdl,
            handle_xpath=hdl_xpath,
            insert_xpath=hdlinsert_xpath
        )
        doc.tree_to_file(x)
        

@click.command()  # pragma: no cover
@click.option('-f', '--files', default='./editions/*.xml', show_default=True)  # pragma: no cover
@click.option('-i', '--indices', default='./indices/list*.xml', show_default=True)  # pragma: no cover
@click.option('-t', '--event-title', default='erwähnt in ', show_default=True)  # pragma: no cover
def mentions_to_indices(files, indices, event_title):  # pragma: no cover
    """Console script write pointers to mentions in index-docs"""
    files = sorted(glob.glob(files))
    index_files = sorted(glob.glob(indices))
    ref_doc_dict = defaultdict(list)
    doc_ref_dict = defaultdict(list)
    click.echo(
        click.style(
            f"collecting list of mentions from {len(files)} docs",
            fg='green'
        )
    )
    for x in tqdm.tqdm(files):
        filename = os.path.split(x)[1]
        doc = TeiEnricher(x)
        doc_base = doc.any_xpath('./@xml:base')[0]
        doc_id = doc.any_xpath('./@xml:id')[0]
        doc_uri = f"{doc_base}/{doc_id}"
        doc_title = doc.any_xpath('.//tei:title[@type="main"]/text()')[0]
        refs = doc.any_xpath('.//tei:rs[@ref]/@ref')
        for ref in refs:
            ref_doc_dict[ref[1:]].append({
                "doc_uri": doc_uri,
                "doc_path": x,
                "doc_title": doc_title
            })
            doc_ref_dict[filename].append(ref[1:])
    click.echo(
        click.style(
            f"collected {len(ref_doc_dict.keys())} of mentioned entities from {len(files)} docs",
            fg='green'
        )
    )
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath('.//tei:body//*[@xml:id]')
        for ent in ent_nodes:
            ent_id = ent.xpath('@xml:id')[0]
            mention = ref_doc_dict[ent_id]
            event_list = doc.create_mention_list(mention, event_title=event_title)
            try:
                list(event_list[0])
                ent.append(event_list)
            except IndexError:
                pass
        doc.tree_to_file(file=x)

    all_ent_nodes = {}
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath('.//tei:body//*[@xml:id]')
        for ent in ent_nodes:
            all_ent_nodes[ent.xpath('@xml:id')[0]] = ent
    click.echo(
        click.style(
            "DONE",
            fg='green'
        )
    )


@click.command()  # pragma: no cover
@click.option('-f', '--files', default='./editions/*.xml', show_default=True)  # pragma: no cover
@click.option('-i', '--indices', default='./indices/list*.xml', show_default=True)  # pragma: no cover
@click.option('-t', '--event-title', default='erwähnt in ', show_default=True)  # pragma: no cover
@click.option('-x', '--title-xpath', default='.//tei:title/text()', show_default=True)  # pragma: no cover
def denormalize_indices(files, indices, event_title, title_xpath):  # pragma: no cover
    """Write pointers to mentions in index-docs and copy index entries into docs"""
    files = sorted(glob.glob(files))
    index_files = sorted(glob.glob(indices))
    ref_doc_dict = defaultdict(list)
    doc_ref_dict = defaultdict(list)
    click.echo(
        click.style(
            f"collecting list of mentions from {len(files)} docs",
            fg='green'
        )
    )
    for x in tqdm.tqdm(files):
        filename = os.path.split(x)[1]
        doc = TeiEnricher(x)
        doc_base = doc.any_xpath('./@xml:base')[0]
        doc_id = doc.any_xpath('./@xml:id')[0]
        doc_uri = f"{doc_base}/{doc_id}"
        doc_title = doc.any_xpath(title_xpath)[0]
        refs = doc.any_xpath('.//tei:rs[@ref]/@ref')
        for ref in refs:
            ref_doc_dict[ref[1:]].append({
                "doc_uri": doc_uri,
                "doc_path": x,
                "doc_title": doc_title
            })
            doc_ref_dict[filename].append(ref[1:])
    click.echo(
        click.style(
            f"collected {len(ref_doc_dict.keys())} of mentioned entities from {len(files)} docs",
            fg='green'
        )
    )
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath('.//tei:body//*[@xml:id]')
        for ent in ent_nodes:
            ent_id = ent.xpath('@xml:id')[0]
            mention = ref_doc_dict[ent_id]
            event_list = doc.create_mention_list(mention, event_title=event_title)
            try:
                list(event_list[0])
                ent.append(event_list)
            except IndexError:
                pass
        doc.tree_to_file(file=x)

    all_ent_nodes = {}
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath('.//tei:body//*[@xml:id]')
        for ent in ent_nodes:
            all_ent_nodes[ent.xpath('@xml:id')[0]] = ent

    click.echo(
        click.style(
            f"writing {len(all_ent_nodes)} index entries into {len(files)} files",
            fg='green'
        )
    )
    for x in tqdm.tqdm(files):
        filename = os.path.split(x)[1]
        doc = TeiEnricher(x)
        root_node = doc.any_xpath('.//tei:text')[0]
        refs = doc.any_xpath('.//tei:rs[@ref]/@ref')
        ent_dict = defaultdict(list)
        for ref in refs:
            ent_id = ref[1:]
            try:
                index_ent = all_ent_nodes[ent_id]
                ent_dict[index_ent.tag].append(index_ent)
            except KeyError:
                continue
        back_node = ET.Element("{http://www.tei-c.org/ns/1.0}back")
        for key in ent_dict.keys():
            if key.endswith('person'):
                list_person = ET.Element("{http://www.tei-c.org/ns/1.0}listPerson")
                back_node.append(list_person)
                for ent in ent_dict[key]:
                    list_person.append(ent)
            if key.endswith('place'):
                list_place = ET.Element("{http://www.tei-c.org/ns/1.0}listPlace")
                back_node.append(list_place)
                for ent in ent_dict[key]:
                    list_place.append(ent)
            if key.endswith('org'):
                list_org = ET.Element("{http://www.tei-c.org/ns/1.0}listOrg")
                back_node.append(list_org)
                for ent in ent_dict[key]:
                    list_org.append(ent)
            if key.endswith('bibl'):
                list_bibl = ET.Element("{http://www.tei-c.org/ns/1.0}listBibl")
                back_node.append(list_bibl)
                for ent in ent_dict[key]:
                    list_bibl.append(ent)
        root_node.append(back_node)
        doc.tree_to_file(file=x)
    click.echo(
        click.style(
            "DONE",
            fg='green'
        )
    )


@click.command()  # pragma: no cover
@click.option('-f', '--files', default='./editions/*.xml', show_default=True)  # pragma: no cover
@click.option('-i', '--indices', default='./indices/list*.xml', show_default=True)  # pragma: no cover
@click.option('-t', '--doc-person', default='./indices/index_person_day.xml', show_default=True)  # pragma: no cover
@click.option('-t', '--work-list', default='./indices/listwork.xml', show_default=True)  # pragma: no cover

def schnitzler(files, indices, doc_person, work_list):  # pragma: no cover
    """Console script write pointers to mentions in index-docs"""
    files = sorted(glob.glob(files))
    index_files = sorted(glob.glob(indices))
    doc_person = TeiEnricher(doc_person)
    list_work = TeiEnricher(work_list)
    all_ent_nodes = {}
    for x in index_files:
        doc = TeiEnricher(x)
        ent_nodes = doc.any_xpath('.//tei:body//*[@xml:id]')
        for ent in ent_nodes:
            all_ent_nodes[ent.xpath('@xml:id')[0]] = ent

    no_matches = []
    for x in tqdm.tqdm(files, total=len(files)):
        day = x.split('/')[-1].replace('entry__', '').replace('.xml', '')
        xpath = f".//item[@target='{day}']/ref/text()"
        person_ids = doc_person.any_xpath(xpath)
        doc = TeiEnricher(x)
        root_node = doc.any_xpath('.//tei:text')[0]
        back_node = ET.Element("{http://www.tei-c.org/ns/1.0}back")
        list_person_node = ET.Element("{http://www.tei-c.org/ns/1.0}listPerson")
        if len(person_ids) > 0:
            for pers_id in person_ids:
                xpath = f'.//tei:person[@xml:id="{pers_id}"]'
                try:
                    pers_node = all_ent_nodes[pers_id]
                except KeyError:
                    no_matches.append(pers_id)
                    continue
                list_person_node.append(pers_node)
            if len(list_person_node) > 0:
                back_node.append(list_person_node)
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
        work_matches = list_work.any_xpath(f".//tei:body//*[@when='{day}']/parent::*")
        if len(work_matches) > 0:
            list_bibl_node = ET.Element("{http://www.tei-c.org/ns/1.0}listBible")
            for work in work_matches:
                title_node = work.xpath('./*[@key]')[0]
                title_text = title_node.text
                title_id = title_node.xpath('@key')[0]
                bibl_node = ET.Element("{http://www.tei-c.org/ns/1.0}bibl")
                title_node = ET.Element("{http://www.tei-c.org/ns/1.0}bibl")
                title_node.text = title_text
                bibl_node.set('{http://www.w3.org/XML/1998/namespace}id', title_id)
                bibl_node.append(title_node)
                list_bibl_node.append(bibl_node)
            back_node.append(list_bibl_node)
        if len(back_node) > 0:
            root_node.append(back_node)
            doc.tree_to_file(file=x)
    distinct_no_match = set(no_matches)
    print(distinct_no_match)
