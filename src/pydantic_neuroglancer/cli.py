import click
from pydantic_neuroglancer.url_state import parse_url


@click.command()
@click.argument("url", type=click.STRING)
def url_to_json(url: str):
    click.echo(parse_url(url).json(indent=2))


if __name__ == "__main__":
    url_to_json()
