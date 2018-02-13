#!/usr/bin/env python3
"""Facebook attending pics

Usage:
    rgap_get_fbattendingpics.py <app_id> <app_secret> <event_id> <output_dir>
    rgap_get_fbattendingpics.py <app_id> <app_secret> <event_id>

    rgap_get_fbattendingpics.py -h

Arguments:
    app_id          facebook app_id
    app_secret      facebook app_secret
    event_id        event id

"""

import os
import sys
import json
import datetime
import csv
import time
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def request_until_succeed(url):
    req = Request(url)
    success = False
    times = 0
    while success is False:
        try:
            times += 1
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            if times == 20:
                print("Exited after trying 20 times.")
                sys.exit(0)

            print("Error for URL {}: {}".format(url, datetime.datetime.now()))
            print("Retrying.")

    return response.read()


# Needed to write tricky unicode correctly to csv
def unicode_decode(text):
    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


def getFacebookPageFeedUrl(base_url):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    fields = "&fields=picture.type(large),name"

    return base_url + fields


def processFacebookPageFeedStatus(status):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_name = status['name']
    status_picture = '' if 'picture' not in status else status['picture']['data']['url']

    return (status_id, status_name, status_picture)


def scrapeFacebookPageFeedStatus(page_id, access_token, output_dir):

    with open(output_dir + '/{}_facebook_statuses.csv'.format(page_id), 'w') as file:
        w = csv.writer(file)

        w.writerow(["status_id", "name", "picture"])

        has_next_page = True
        num_processed = 0
        scrape_starttime = datetime.datetime.now()
        after = ''
        base = "https://graph.facebook.com/v2.11"
        node = "/{}/attending".format(page_id)
        parameters = "/?access_token={}".format(access_token)
        print(parameters)

        print("Scraping {} Facebook Event: {}\n".format(page_id, scrape_starttime))

        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = base + node + parameters + after
            # print(base_url)

            url = getFacebookPageFeedUrl(base_url)
            statuses = json.loads(request_until_succeed(url).decode('utf-8'))

            prev_id = None
            for status in statuses['data']:

                status_data = processFacebookPageFeedStatus(status)
                if prev_id == status_data[0]:  # In case of a duplicate
                    continue
                prev_id = status_data[0]

                w.writerow(status_data)

                num_processed += 1
                if num_processed % 100 == 0:
                    print("{} Statuses Processed: {}".format
                          (num_processed, datetime.datetime.now()))

            # if there is no next page, we're done.
            if 'paging' in statuses:
                after = statuses['paging']['cursors']['after']
            else:
                has_next_page = False

        print("\nDone!\npage_id - {} Statuses Processed in {}".format(
              num_processed, datetime.datetime.now() - scrape_starttime))


def main(args):
    app_id = args['<app_id>']
    app_secret = args['<app_secret>']
    event_id = args['<event_id>']

    output_dir = args['<output_dir>']
    if not output_dir:
        output_dir = os.getcwd()
    elif not os.path.exists(output_dir):
        os.makedirs(output_dir)

    access_token = app_id + "|" + app_secret
    scrapeFacebookPageFeedStatus(event_id, access_token, output_dir)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
