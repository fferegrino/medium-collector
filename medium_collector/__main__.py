import click
from decouple import config
import csv
from pathlib import Path
from medium_collector.reader import read_from_mail
from medium_collector.parser import read_email

FIELDS = ["date", "to", "from", "subject",
            "section_title", "post_title", "post_subtitle",
            "post_url", "author_name", "author_handle", 
            "site_name", "site_slug", "members_only"]

@click.command()
def import_medium():
    data_path = Path("data")
    data_path.mkdir(parents=True)
    with open(data_path / "mails.csv", "w") as writable:
        writer = csv.DictWriter(writable, fieldnames=FIELDS)
        writer.writeheader()
        messages = read_from_mail(config("IMAP_SERVER"),config("EMAIL_ACCOUNT"),config("EMAIL_PASS"), "INBOX.Daily Digests")
        for msg_id, email in messages:
            articles = read_email(email)
            for article in articles:
                writer.writerow(article)

if __name__ == '__main__':
    import_medium()