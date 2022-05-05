import sys
from pprint import pprint

import typer

from bioimageio.spec import __version__, collection, commands
from bioimageio.spec.__main__ import app
from bioimageio.spec.partner.utils import enrich_partial_rdf_with_imjoy_plugin

app.info.help += (
    f"\n+\nbioimageio.spec.partner {__version__}\nimplementing:\n\tpartner collection RDF {collection.format_version}"
)


@app.command()
def validate_partner_collection(
    rdf_source: str = typer.Argument(..., help="RDF source as relative file path or URI"),
    update_format: bool = typer.Option(
        False,
        help="Update format version to the latest (might fail even if source adheres to an old format version). "
        "To inform the format update the source may specify fields of future versions in "
        "config:future:<future version>.",  # todo: add future documentation
    ),
    update_format_inner: bool = typer.Option(
        None, help="For collection RDFs only. Defaults to value of 'update-format'."
    ),
    verbose: bool = typer.Option(False, help="show traceback of unexpected (no ValidationError) exceptions"),
):
    summary = commands.validate(
        rdf_source, update_format, update_format_inner, enrich_partial_rdf=enrich_partial_rdf_with_imjoy_plugin
    )
    if summary["error"] is not None:
        print(f"Error in {summary['name']}:")
        pprint(summary["error"])
        if verbose:
            print("traceback:")
            pprint(summary["traceback"])
        ret_code = 1
    else:
        print(f"No validation errors for {summary['name']}")
        ret_code = 0

    if summary["warnings"]:
        print(f"Validation Warnings for {summary['name']}:")
        pprint(summary["warnings"])

    sys.exit(ret_code)


validate_partner_collection.__doc__ = (
    "A special version of the bioimageio validate command that enriches the RDFs defined in collections by parsing any "
    "associated imjoy plugins. This is implemented using the 'enrich_partial_rdf' of the regular validate command:\n"
    + commands.validate.__doc__
)

if __name__ == "__main__":
    app()
