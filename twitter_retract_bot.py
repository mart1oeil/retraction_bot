import tweepy
import datetime
import calendar
import retraction_scraper
import configargparse  as cap

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

# Create Tweet 

# The app and the corresponding credentials must h  ave the Write permission

# Check the App permissions section of the Settings tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps

# Make sure to reauthorize your app / regenerate your access token and secret 
# after setting the Write permission


today = datetime.date.today()

month = today.month
year = today.year

last_day_month = calendar.monthrange(year=year,month=month)[1]

if today.day == last_day_month :

    from_date = str(today.month)+"/01/"+str(today.year)
    to_date = str(today.month)+"/"+str(today.day)+"/"+str(today.year)

    retraction_text = "Article retracté ce mois : "
    concern_text = "Doutes émis par l'éditeur : "


    scraped = retraction_scraper.scraper(country="France",from_date=from_date,to_date=to_date)
    resp =""
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
        if not resp:
            response = client.create_tweet(text=text)
        else :
            response = client.create_tweet(text=text,  in_reply_to_tweet_id=resp)
        resp = response.data['id']
else :
    print("not today")


