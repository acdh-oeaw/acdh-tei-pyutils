"""Console script for acdh_collatex_utils."""
import click
import glob
import os
import tqdm
from collections import defaultdict


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
