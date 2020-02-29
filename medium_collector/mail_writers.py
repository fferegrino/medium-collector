import csv

from medium_collector.parser import get_articles, parse_mail

MAILS_HEADERS = ["id", "date", "to", "from", "subject"]
ARTICLE_MAIL_HEADERS = [
    "mail_id",
    "post_url",
    "post_title",
    "post_subtitle",
    "section_title",
    "members_only",
    "author_name",
    "author_handle",
    "site_name",
    "site_slug",
]


def write_articles(file, write_headers, articles, mail_id):
    with open(file, "a") as mail_article_writable:
        mail_article_writer = csv.DictWriter(
            mail_article_writable, fieldnames=ARTICLE_MAIL_HEADERS
        )

        if write_headers:
            mail_article_writer.writeheader()

        for article in articles:
            article["mail_id"] = mail_id
            mail_article_writer.writerow(article)


def write_emails(
    file,
    write_headers,
    mails,
    mail_articles_csv,
    write_mail_article_headers,
    current_checkpoint,
):
    with open(file, "a") as writable:
        mails_writer = csv.DictWriter(writable, fieldnames=MAILS_HEADERS)
        if write_headers:
            mails_writer.writeheader()
        for msg_id, email in mails:
            mail_info, decoded_mail = parse_mail(email)

            articles = get_articles(decoded_mail)
            write_articles(
                mail_articles_csv, write_mail_article_headers, articles, mail_info["id"]
            )
            write_mail_article_headers = False
            mails_writer.writerow(mail_info)

            current_checkpoint = msg_id
    return current_checkpoint
