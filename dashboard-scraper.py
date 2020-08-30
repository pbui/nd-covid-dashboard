#!/usr/bin/env python3

import datetime
import html
import os
import re
import tempfile
import time

import requests

# Constants

DASHBOARD_URL               = 'https://here.nd.edu/our-approach/dashboard/'
DASHBOARD_STATIC_IMAGE_RX   = r"<param name='static_image' value='([^']+)'"
DASHBOARD_DATE_RX           = r"(\d+/\d+/\d{4})"
DASHBOARD_DATA_RX           = r"\n([\d,]+)\s+([\d,]+)\s+([\d,]+)"

# Functions

def extract_static_image_url(url=DASHBOARD_URL):
    response = requests.get(url)
    return html.unescape(
        re.findall(DASHBOARD_STATIC_IMAGE_RX, response.text)[-1]
    )

def download_static_image(url, workspace):
    response = requests.get(url)
    path     = os.path.join(workspace, 'dashboard.png')
    with open(path, 'wb') as fs:
        fs.write(response.content)
    return path

def scan_static_image(image, workspace):
    os.system(f'tesseract-ocr {image} {workspace}/dashboard -l eng 2> /dev/null')
    return f'{workspace}/dashboard.txt'

def make_timestamp():
    timestamp = datetime.datetime.fromtimestamp(time.time())
    ctime     = timestamp.ctime()
    return f'{ctime[0:3]}, {timestamp.day:02d} {ctime[4:7]}' + timestamp.strftime(' %Y %H:%M:%S +0000')

def generate_rss_feed(date, data):
    total = sum(int(d.replace(',', '')) for d in data[0:3])
    print(f'''<rss version="2.0">
<channel>
<title>Notre Dame Covid Dashboard</title>
<link>{DASHBOARD_URL}</link>
<description>
Notre Dame Covid Dashboard
</description>
<item>
<title>Covid Dashboard ({date}): Graduate={data[0]}, Undergraduate={data[1]}, Employee={data[2]}, Total={total}</title>
<author>pbui</author>
<link>{DASHBOARD_URL}#{''.join([date] + list(data))}</link>
<pubDate>{make_timestamp()}</pubDate>
</item>
</channel>
</rss>
''')


# Main Execution

def main():
    with tempfile.TemporaryDirectory() as workspace:
        url   = extract_static_image_url()
        image = download_static_image(url, workspace)
        text  = scan_static_image(image, workspace)
        date  = re.findall(DASHBOARD_DATE_RX, open(text).read())[0]
        data  = re.findall(DASHBOARD_DATA_RX, open(text).read())[0]
        generate_rss_feed(date, data)

if __name__ == '__main__':
    main()
