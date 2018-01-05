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
    while 1:
        try:
            download_image(res["items"][0]["link"], filename)
        except RuntimeError as e:
            print("{}, trying next result".format(e))
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
    twitter.update_status(message, media_ids=[upl_resp.media_id_string])


def run(twitter, gcse):
    adj = adjectives[random.randrange(28479)]
    noun = nouns[random.randrange(4554)]
    query = "{} {}".format(adj, noun)
    print(query)
    try:
        get_image(gcse, query, "tmp.jpg")
    except KeyError:
        print("No result for {}".format(query))
    else:
        pass
        # tweet_image(twitter, "tmp.jpg", sys.argv[2])


if __name__ == "__main__":
    twitter = twitter_api()
    gcse = gcse_api()
    while True:
        run(twitter, gcse)
        time.sleep(60 * 60 * 6)
