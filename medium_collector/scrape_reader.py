import csv
import datetime
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

TAG_REMOVAL_RE = re.compile(r"(<!--.*?-->|<[^>]*>)")
CLAPS_RE = re.compile(r"(\d+(?:.\d)?[K]?)\sclap(?:s)?")
METADATA_INFO_RE = re.compile(
    r"([a-zA-Z]{3}) ([0-9]+)(?:, ([0-9]{4}))? · ([0-9])+ min(?:s)? read"
)

csv.field_size_limit(sys.maxsize)

FIELDS = ["url", "title", "subtitle", "tags", "claps", "comments"]


def process_tags(scraped_tags):
    possible_tags = [
        possible_tag.strip('"') for possible_tag in scraped_tags.split(",")
    ]
    for tags in possible_tags:
        if not tags:
            continue
        soup_list = BeautifulSoup(tags, "lxml")
        tags = [li.get_text() for li in soup_list.find_all("li")]
        return "|".join(tags)


def process_metadata(metadata):
    soup = BeautifulSoup(metadata, "lxml")
    text = None
    try:
        text = soup.body.find_all("div",recursive=False)[1].find_all("span", recursive=False)[0].text
    except:
        pass

    try:
        if text is None:
            [metadata] = soup.select("div > div > span:nth-child(2)")
            text = metadata.get_text()
    except:
        pass

    if text is not None:
        match = re.match(METADATA_INFO_RE, text)
        if match:
            return {
                "year": int(match.group(3)) if match.group(3) else None,
                "month": match.group(1),
                "day": int(match.group(2)),
                "minutes_read": int(match.group(4)),
            }
    else:
        pass
    return {}


def process_comments(comments):
    try:
        first_par = comments.find("(")
        if first_par > 0:
            last_par = comments.find(")")
            return int(comments[first_par + 1 : last_par])
    except ValueError:
        pass
    return 0

def process_scrape_date(extract_date):
    try:
        return datetime.datetime.strptime(extract_date, "%Y-%m-%d %H:%M:%S +0000")
    except:
        return None

def process_claps(claps):
    match = re.match(CLAPS_RE, claps)
    if match:
        return match.group(1)
    return None


HEADERS_DETAILS = [
    "url",
    "title",
    "subtitle",
    "tags",
    "minutes_read",
    "claps",
    "comments",
    "year",
    "month",
    "day",
    "scrape_date",
]

HEADER_ERRORS = ["url", "error"]


def process_details(input_files, output_file, error_file):

    with open(output_file, "w") as writable_details, open(error_file, "w") as writable_errors:
        for input_file in input_files:
            with open(input_file) as readable:
                reader = csv.DictReader(readable)
                errors_writer = csv.DictWriter(writable_errors, fieldnames=HEADER_ERRORS)
                errors_writer.writeheader()
                details_writer = csv.DictWriter(writable_details, fieldnames=HEADERS_DETAILS)
                details_writer.writeheader()
                for article in reader:
                    if article.get("error"):
                        errors_writer.writerow({"url":article["url"], "error":article["error"]})
                        continue

                    del article["error"]
                    body = article.pop("body")
                    article["title"] = TAG_REMOVAL_RE.sub("", article["title"])
                    article["subtitle"] = TAG_REMOVAL_RE.sub("", article.pop("subtitle"))
                    article["tags"] = process_tags(article["tags"])
                    article["claps"] = process_claps(article["claps"])
                    article["comments"] = process_comments(article["comments"])
                    article.update(process_metadata(article.pop("metadata")))
                    article["scrape_date"] = process_scrape_date(article.pop("extract_date"))
                    if "year" in article and article["year"] is None and article["scrape_date"] is not None:
                        article["year"] = article["scrape_date"].year
                    details_writer.writerow(article)

