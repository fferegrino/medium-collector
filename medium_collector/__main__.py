from datetime import datetime
from pathlib import Path

import click

from medium_collector.download import download
from medium_collector.kaggle_datasets import upload_to_kaggle
from medium_collector.s3 import upload_files


@click.group()
def cli():
    pass


@cli.command()
def from_mail():
    message = datetime.now().strftime("%A, %B %e, %Y")
    data_path = Path("data")
    if not data_path.exists():
        data_path.mkdir()
    download.download_from_mail(data_path)
    upload_files(data_path)
    upload_to_kaggle(data_path, message)


if __name__ == "__main__":
    cli()
