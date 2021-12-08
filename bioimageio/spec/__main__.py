import sys
from pprint import pprint

import typer

from bioimageio.spec import __version__, commands, model, rdf

help_version = (
    f"bioimageio.spec {__version__}"
    "\nimplementing:"
    f"\n\tcollection RDF {rdf.format_version}"
    f"\n\tgeneral RDF {rdf.format_version}"
    f"\n\tmodel RDF {model.format_version}"
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
    sys.exit(ret_code)


validate.__doc__ = commands.validate.__doc__


@app.command()
def update_format(
    rdf_source: str = typer.Argument(..., help="RDF source as relative file path or URI"),
    path: str = typer.Argument(..., help="Path to save the RDF converted to the latest format"),
):
    try:
        commands.update_format(rdf_source, path)
        ret_code = 0
    except Exception as e:
        print(f"update_format failed with {e}")
        ret_code = 1
    sys.exit(ret_code)


update_format.__doc__ == commands.update_format.__doc__


# note: single command requires additional (dummy) callback
# see: https://typer.tiangolo.com/tutorial/commands/one-or-multiple/#one-command-and-one-callback
@app.callback()
def callback():
    typer.echo(help_version)


if __name__ == "__main__":
    app()
