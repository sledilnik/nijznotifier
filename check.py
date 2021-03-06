#!/usr/bin/env python

import hashlib
import os
import re
import time

import requests
from dateutil import parser
from lxml import html
from slack_webhook import Slack
import json
import logging

logging.basicConfig(level=logging.INFO)

CACHE_FILE = os.getenv('CACHE_FILE', '/tmp/cache.json')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', '#sandbox')

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'
}

if SLACK_WEBHOOK_URL:
    slack = Slack(url=SLACK_WEBHOOK_URL)
else:
    slack = None


def parse_page():
    resp = requests.get(
        'https://www.nijz.si/sl/dnevno-spremljanje-okuzb-s-sars-cov-2-covid-19', headers=headers)
    resp.raise_for_status()
    tree = html.fromstring(resp.content)
    date = parser.parse(tree.xpath("//div[@class='meta']/text()")[0])
    links = tree.xpath(
        "//div[contains(@class, 'field-name-body')]//a[contains(@href, '/sites/www.nijz.si/files/uploaded/')]/@href")

    single_vax = tree.xpath(".//table//tr")[0].xpath("./td[1]//text()")[0].replace('.', '')
    double_vax = tree.xpath(".//table//tr")[1].xpath("./td[1]//text()")[0].replace('.', '')
    filtered_links = list(filter(lambda url: url.endswith('.xlsx'), links))
    return (date, filtered_links, {'double_vax': double_vax, 'single_vax': single_vax})


def file_hash(url):
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    m = hashlib.sha256()
    m.update(resp.content)
    return m.hexdigest()


def notify_new(url, extra=None):
    text = ""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Changes on NIJZ webpage detected"
            }
        }
    ]

    if isinstance(url, str):
        text = "New file: {}".format(url)
    if isinstance(url, set):
        text = "New files: {}".format(', '.join(url))

        for u in url:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": u
                    }
                }
            )

    if extra and 'doub':
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Cepljeni"
            }
        })
        blocks.append(
            {
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": ":syringe:: {}\n:syringe::syringe:: {}".format(extra.get('single_vax', '???'), extra.get('double_vax', '???'))
                }
            }
        )

    logging.info("Notification: {}".format(text))

    if slack:
        slack.post(
            username="NIJZ bot",
            channel=SLACK_CHANNEL,
            blocks=blocks
        )


def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()
    except json.decoder.JSONDecodeError:
        os.remove(CACHE_FILE)
        return set()


def persist_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(list(data), f)


def loop():
    logging.info("Staring NIJZ checker")
    last_hash = load_cache()
    while True:
        logging.info('Parsing NIZJ page')
        date, links, extra = parse_page()
        new_hash = set()
        new_files = set()
        for link in links:
            url = "https://www.nijz.si/{}".format(link)
            new_hash.add(file_hash(url))
            new_files.add(url)
        if new_hash != last_hash:
            notify_new(new_files, extra)
        last_hash = new_hash
        persist_cache(last_hash)
        time.sleep(300)


if __name__ == '__main__':
    loop()
