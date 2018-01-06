import logging
import os
import sys
import requests
import tweepy
import configparser
import googleapiclient.discovery
import random
import time
from adjectives import adjectives
from nouns import nouns


from pprint import pprint

config = configparser.ConfigParser()
config.read("creds.ini")


def twitter_api():
    auth = tweepy.OAuthHandler(config["consumer"]["key"],
                               config["consumer"]["secret"])
    auth.set_access_token(config["access"]["token"],
                          config["access"]["secret"])
    return tweepy.API(auth)


def gcse_api():
    return googleapiclient.discovery.build("customsearch", "v1",
                                           developerKey=config["gcse"]["api_key"])


def get_image(gcse, search, filename):
    res = gcse.cse().list(q=search, num=10,
                          searchType="image",
                          cx=config["gcse"]["id"]).execute()
    for item in res["items"]:
        try:
            download_image(item["link"], "{}".format(filename))
        except RuntimeError as e:
            logging.warning("{}, trying next result".format(e))
        else:
            break


def download_image(url, filename):
    req = requests.get(url, stream=True)
    if req.status_code == 200:
        with open(filename, "wb") as image:
            for chunk in req:
                image.write(chunk)
    else:
        raise RuntimeError("Couldn't download file {}".format(filename))


def tweet_image(twitter, filepath, message):
    upl_resp = twitter.media_upload(filepath)
    resp = twitter.update_status(message, media_ids=[upl_resp.media_id_string])


def run(twitter, gcse):
    filename2 = "tmp2.jpg"
    filename1 = "tmp1.jpg"
    q1 = "fantom alpaca"
    while True:
        q2 = "{} {}".format(adjectives[random.randrange(1684)],
                            nouns[random.randrange(4566)])
        logging.info("new query: {}".format(q2))
        try:
            get_image(gcse, q2, filename2)
        except KeyError as e:
            logging.warning("{}, skipping".format(e), file=sys.stderr)
            continue
        tweet_image(twitter, filename1, q2)
        logging.info("tweeting image [{} ({})] with msg [{}]".format(filename1, q1, q2))
        os.rename(filename2, filename1)
        q1 = q2
        time.sleep(60 * 60 * 3)


if __name__ == "__main__":
    logging.basicConfig(filename="log",
                        format="%(asctime)s %(levelname)s:  %(message)s",
                        level=logging.DEBUG)
    twitter = twitter_api()
    gcse = gcse_api()
    run(twitter, gcse)
