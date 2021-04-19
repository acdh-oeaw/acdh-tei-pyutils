"""Console script for acdh_collatex_utils."""
import click
import glob
import os
import tqdm
from collections import defaultdict
from lxml import etree as ET


from acdh_tei_pyutils.tei import TeiEnricher
from acdh_tei_pyutils.utils import previous_and_next


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
