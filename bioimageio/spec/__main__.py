from pprint import pprint

import typer

from bioimageio.spec import __version__, commands

app = typer.Typer()  # https://typer.tiangolo.com/


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
    verbose: bool = typer.Option(False, help="show traceback of exceptions"),
) -> int:
    errors = commands.validate(rdf_source, update_format, update_format_inner, verbose)
    if errors:
        print(f"Errors for {rdf_source}")
        pprint(errors)
        return 1
    else:
        print(f"No validation errors for {rdf_source}")
        return 0


validate.__doc__ = commands.validate.__doc__


if __name__ == "__main__":
    print(f"bioimageio.spec package version {__version__}")
    app()
