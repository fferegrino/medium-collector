from pathlib import Path

import click
from decouple import config

from medium_collector.mail_writers import write_emails
from medium_collector.reader import read_from_mail
from medium_collector.utils import get_checkpoint, write_checkpoint
from medium_collector.scrape_reader import process_details


@click.group()
def cli():
    pass


@cli.command()
def download_from_mail():
    data_path = Path("data")
    data_path.mkdir(parents=True, exist_ok=True)
    mails_csv = data_path / "mails.csv"
    mail_articles_csv = data_path / "articles_mails.csv"
    write_mails_headers = not mails_csv.exists()
    write_mail_article_headers = not mail_articles_csv.exists()

    checkpoint = get_checkpoint()

    messages = read_from_mail(
        config("IMAP_SERVER"),
        config("EMAIL_ACCOUNT"),
        config("EMAIL_PASS"),
        "INBOX.Daily Digests",
        checkpoint=checkpoint,
    )

    checkpoint = write_emails(
        mails_csv,
        write_mails_headers,
        messages,
        mail_articles_csv,
        write_mail_article_headers,
        checkpoint,
    )

    write_checkpoint(checkpoint)

@cli.command()
def parse_details():

    input_file = Path("scrape/medium_initial.csv")
    output_file = Path("data/articles_details.csv")
    error_file = Path("data/errored_out.csv")

    process_details([input_file], output_file, error_file)

if __name__ == "__main__":
    cli()
