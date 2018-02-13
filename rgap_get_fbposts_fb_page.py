#!/usr/bin/env python3
"""Facebook posts from a fan page

Usage:
    rgap_get_fbposts_fb_page.py <app_id> <app_secret> <page_id> <since_date> <until_date> <output_dir>
    rgap_get_fbposts_fb_page.py <app_id> <app_secret> <page_id> <since_date> <until_date>
    rgap_get_fbposts_fb_page.py <app_id> <app_secret> <page_id> <output_dir>
    rgap_get_fbposts_fb_page.py <app_id> <app_secret> <page_id>

    rgap_get_fbposts_fb_page.py -h

Arguments:
    app_id          facebook app_id
    app_secret      facebook app_secret
    page_id         fanpage id
    since_date      starting date formatted as YYYY-MM-DD
    until_date      ending date formatted as YYYY-MM-DD
    output_dir      output directory

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
    fields = "&fields=message,description,link,picture,created_time,type,name,id," + \
        "comments.limit(0).summary(true),shares,reactions" + \
        ".limit(0).summary(true)"

    return base_url + fields


def getReactionsForStatuses(base_url):

    reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
    reactions_dict = {}   # dict of {status_id: tuple<6>}

    for reaction_type in reaction_types:
        fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
            reaction_type.upper())

        url = base_url + fields
        data = json.loads(request_until_succeed(url).decode('utf-8'))['data']

        data_processed = []
        prev_id = None
        for status in data:
            id = status['id']
            if prev_id == id:  # In case of a duplicate
                continue
            prev_id = id
            count = status['reactions']['summary']['total_count']
            data_processed.append((id, count))

        for id, count in data_processed:
            if id in reactions_dict:
                reactions_dict[id] = reactions_dict[id] + (count,)
            else:
                reactions_dict[id] = (count,)

    return reactions_dict


def processFacebookPageFeedStatus(status):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_type = status['type']

    status_message = '' if 'message' not in status else \
        unicode_decode(status['message'])
    status_description = '' if 'description' not in status else \
        unicode_decode(status['description'])
    link_name = '' if 'name' not in status else \
        unicode_decode(status['name'])
    status_picture = '' if 'picture' not in status else \
        unicode_decode(status['picture'])
    status_link = '' if 'link' not in status else \
        unicode_decode(status['link'])

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
        status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + \
        datetime.timedelta(hours=-5)  # EST
    status_published = status_published.strftime(
        '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
        status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
        status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    return (status_id, status_message, status_description, link_name, status_picture, status_type, status_link,
            status_published, num_reactions, num_comments, num_shares)


def scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date, output_dir):

    with open(output_dir + '/{}_facebook_statuses.csv'.format(page_id), 'w') as file:
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "status_description", "link_name", "status_picture", "status_type",
                    "status_link", "status_published", "num_reactions",
                    "num_comments", "num_shares", "num_likes", "num_loves",
                    "num_wows", "num_hahas", "num_sads", "num_angrys",
                    "num_special"])

        has_next_page = True
        num_processed = 0
        scrape_starttime = datetime.datetime.now()
        after = ''
        base = "https://graph.facebook.com/v2.9"
        node = "/{}/posts".format(page_id)
        parameters = "/?limit={}&access_token={}".format(100, access_token)
        since = "&since={}".format(since_date) if since_date \
            is not '' and since_date is not None else ''
        until = "&until={}".format(until_date) if until_date \
            is not '' and since_date is not None else ''

        print("Scraping {} Facebook Page: {}\n".format(page_id, scrape_starttime))

        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = base + node + parameters + after + since + until
            # print(base_url)

            url = getFacebookPageFeedUrl(base_url)
            statuses = json.loads(request_until_succeed(url).decode('utf-8'))
            reactions = getReactionsForStatuses(base_url)

            prev_id = None
            for status in statuses['data']:

                # Ensure it is a status with the expected metadata
                if 'reactions' in status:
                    status_data = processFacebookPageFeedStatus(status)
                    if prev_id == status_data[0]:  # In case of a duplicate
                        continue
                    prev_id = status_data[0]

                    reactions_data = reactions[status_data[0]]

                    # calculate thankful/pride through algebra (it will sometimes be wrong because of lack of syncronization)
                    num_special = status_data[8] - sum(reactions_data)
                    w.writerow(status_data + reactions_data + (num_special,))

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
    page_id = args['<page_id>']
    since_date = args['<since_date>']
    until_date = args['<until_date>']

    output_dir = args['<output_dir>']
    if not output_dir:
        output_dir = os.getcwd()
    elif not os.path.exists(output_dir):
        os.makedirs(output_dir)

    access_token = app_id + "|" + app_secret
    scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date, output_dir)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
