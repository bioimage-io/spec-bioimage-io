import sys
from pathlib import Path
from pprint import pprint

import typer

from bioimageio.spec import __version__, collection, commands, model, rdf

try:
    from bioimageio.spec.partner.utils import enrich_partial_rdf_with_imjoy_plugin
except ImportError:
    enrich_partial_rdf_with_imjoy_plugin = None
    partner_help = ""
else:
    partner_help = f"\n+\nbioimageio.spec.partner {__version__}\nimplementing:\n\tpartner collection RDF {collection.format_version}"

help_version = (
    f"bioimageio.spec {__version__}"
    "\nimplementing:"
    f"\n\tcollection RDF {collection.format_version}"
    f"\n\tgeneral RDF {rdf.format_version}"
    f"\n\tmodel RDF {model.format_version}" + partner_help
)

# prevent rewrapping with \b\n: https://click.palletsprojects.com/en/7.x/documentation/#preventing-rewrapping
app = typer.Typer(
    help="\b\n" + help_version,
    context_settings={"help_option_names": ["-h", "--help", "--version"]},  # make --version display help with version
)  # https://typer.tiangolo.com/


@app.command()
def validate(
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
    summary = commands.validate(rdf_source, update_format, update_format_inner)
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


validate.__doc__ = commands.validate.__doc__


if enrich_partial_rdf_with_imjoy_plugin is not None:

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


@app.command()
def update_format(
    rdf_source: str = typer.Argument(..., help="RDF source as relative file path or URI"),
    path: str = typer.Argument(..., help="Path to save the RDF converted to the latest format"),
):
    try:
        commands.update_format(rdf_source, path)
        ret_code = 0
    except Exception as e:
        print(f"update-format failed with {e}")
        ret_code = 1
    sys.exit(ret_code)


update_format.__doc__ == commands.update_format.__doc__


@app.command()
def update_rdf(
    source: str = typer.Argument(..., help="relative file path or URI to RDF source"),
    update: str = typer.Argument(..., help="relative file path or URI to (partial) RDF as update"),
    output: Path = typer.Argument(..., help="Path to save the updated RDF to"),
    validate: bool = typer.Option(True, help="Whether or not to validate the updated RDF"),
):
    """Update a given RDF with a (partial) RDF-like update"""
    try:
        commands.update_rdf(source, update, output, validate)
        ret_code = 0
    except Exception as e:
        print(f"update-rdf failed with {e}")
        ret_code = 1
    sys.exit(ret_code)


@app.callback()
def callback():
    typer.echo(help_version)


if __name__ == "__main__":
    app()
