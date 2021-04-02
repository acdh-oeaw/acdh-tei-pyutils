"""Console script for acdh_collatex_utils."""
import click
import glob
import os
import tqdm


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
