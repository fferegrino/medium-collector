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

def get_checkpoint():
    try:
        with open("checkpoint.txt") as readable:
            return int(readable.read())
    except:
        return 1

def write_checkpoint(checkpoint):
    with open("checkpoint.txt", "w") as writable:
        writable.write(str(checkpoint))
        writable.write("\n")

@click.command()
def import_medium():
    data_path = Path("data")
    data_path.mkdir(parents=True, exist_ok=True)
    mails_csv = data_path / "mails.csv"
    write_headers = not mails_csv.exists()
    checkpoint = get_checkpoint()
    with open(mails_csv, "a") as writable:
        writer = csv.DictWriter(writable, fieldnames=FIELDS)
        if write_headers:
            writer.writeheader()
        messages = read_from_mail(config("IMAP_SERVER"),config("EMAIL_ACCOUNT"),config("EMAIL_PASS"), "INBOX.Daily Digests", checkpoint=checkpoint)
        for msg_id, email in messages:
            articles = read_email(email)
            for article in articles:
                writer.writerow(article)
            checkpoint = msg_id
    write_checkpoint(checkpoint)

if __name__ == '__main__':
    import_medium()