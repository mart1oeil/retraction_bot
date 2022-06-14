import tweepy
import datetime
import retraction_scraper
import configargparse  as cap
# import os

def get_last_tweet():
    filepath = "data/last_tweet.txt"
    if os.path.isfile(filepath):
        with open(filepath, "r") as file:
            last_tweet = file.readlines()
            return last_tweet
    else:
        return ""


def save_last_tweet_(id,month):
    dir = "data"
    filepath = "data/last_tweet.txt"
    if os.path.isdir(dir) == False:
        try:
            os.makedirs(dir)
        except OSError:
            print ("Creation of the directory %s failed" % dir)
    else:
        print ("Successfully created the directory %s" % dir)
    with open(filepath,"w") as file:
        file.write(str(id)+"\n"+month)


argparser = cap.ArgParser(default_config_files=['keys.yml'])
argparser.add('-c', is_config_file=True, help='config file path')
argparser.add('--api', env_var='BOT_API')
argparser.add('--api-secret', env_var='BOT_API_SECRET')
argparser.add('--access', env_var='BOT_ACCESS')
argparser.add('--access-secret', env_var='BOT_ACCESS_SECRET')

args = argparser.parse_args()


client = tweepy.Client(
    consumer_key=args.api, consumer_secret=args.api_secret,
    access_token=args.access, access_token_secret=args.access_secret
)


today = datetime.date.today()
today = datetime.date(2022, 6, 14)

yesterday = today - datetime.timedelta(days=1)

month = today.month
year = today.year




##from_date = str(today.month)+"/01/"+str(today.year)
##to_date = str(today.month)+"/"+str(today.day)+"/"+str(today.year)

from_date = "{:02d}".format(yesterday.month)+"/"+"{:02d}".format(yesterday.day)+"/"+str(yesterday.year)
## to_date = "{:02d}".format(today.month)+"/"+"{:02d}".format(today.day)+"/"+str(today.year)

retraction_text = "Article retracté : "
concern_text = "Mise en garde de l'éditeur : "

scraped = retraction_scraper.scraper(country="France",from_date=from_date,to_date=from_date)
#resp = get_last_tweet()
resp = ""
for row in scraped :
    doi = "http://dx.doi.org/"+row["original_doi"]
    authors_text = row["authors"][0]+" et al. "
    text = row["title"] + ", de "+ authors_text + " "
    if row["retraction_nature"] == "Retraction":
        text = retraction_text + text
    elif row["retraction_nature"] == "Expression of concern":
        text = concern_text + text
    len_max = 257 #short links on twitter are 23 characters so the max of the text's length is 257
    if len(text)> len_max:
        len_title = len_max - 1 - len(authors_text) - 5 - 4 # 1 space at the end / 5 characters for ", de " / 4 characters for "..."
        if row["retraction_nature"] == "Retraction":
            len_title = len_title - len(retraction_text)
            new_title = row["title"][0:len_title]+"..."
            text = retraction_text + new_title+", de "+authors_text+" "
        elif row["retraction_nature"] == "Expression of concern":
            len_title = len_title - len(concern_text)
            new_title = row["title"][0:len_title]+"..."
            text = concern_text + new_title + ", de " + authors_text + " "
        else:
            new_title = row["title"][0:len_title]+"..."
            text = new_title+", de "+authors_text+" "
    text = text + doi
    if not resp or resp[1] is not "{:02d}".format(yesterday.month):
        try:
            response = client.create_tweet(text=text)
        except tweepy.errors.Forbidden:
            print("403 forbidden, perhaps tweet already exists?")

    else :
        response = client.create_tweet(text=text,  in_reply_to_tweet_id=resp[0])
"""     resp = response.data['id']
    if resp:
        save_last_tweet_(resp,"{:02d}".format(yesterday.month)) """



