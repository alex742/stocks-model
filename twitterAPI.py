from twitter import api

# initialize api instance
twitter_api = api.Api(consumer_key='EBkDD4HtvWGK7jZNaDP9HmWdu',
                        consumer_secret='X1dDhfWZkH39ywSOhVsgIT9WUcGYXI2wRZZ6Z5uu2a6buJIEkP',
                        access_token_key='805207123504365568-df1kPDJDGcSsTXKYjkVeWJ2urywjXbA',
                        access_token_secret='qFPbr7Rn9YwcuKn43sgXOFS2mYjwUWITOmYgdNOrZUPeV')

# test authentication
# print(twitter_api.VerifyCredentials())


def buildTestSet(search_keyword):

    tweets_fetched = twitter_api.GetSearch(search_keyword, count=1, result_type='recent', include_entities=True, return_json=True)
    
    print("Fetched " + str(len(tweets_fetched["statuses"])) + " tweets for the term " + search_keyword)

    return [{
            "id": tweet["id_str"],
            "text": tweet["text"],
            "created_at": tweet["created_at"],
            "retweeted": tweet["retweeted"],
            "retweets": tweet["retweet_count"],
            "favourites": tweet["favorite_count"],
            "entities":{
                "hastags": tweet["entities"]["hashtags"],
                "url": tweet["entities"]["urls"],
                "user_mentions": tweet["entities"]["user_mentions"]
            },
            "user": {
                "screen_name": tweet["user"]["screen_name"],
                "follower_count": tweet["user"]["followers_count"],
                "friend_count": tweet["user"]["friends_count"]
            },
            "stock_price": None
            } for tweet in tweets_fetched["statuses"]]
        
def tweet_to_string(tweet):
    return "id: " + tweet["id"],
    "created_at: " + tweet["created_at"], # when the tweet was tweeted
    "text: " + tweet["text"], # content of the tweet
    "hashtags: " + tweet["entities"]["hashtags"], # list of hashtags used ["text"]
    "user_mentions: " + tweet["entities"]["user_mentions"], # list of usermentions ["screen_name"]
    "urls: " + tweet["entities"]["urls"], # list of urls["expanded_url"]
    "retweeted: " + tweet["retweeted"], # was this a retweet
    "retweet_count: " + tweet["retweet_count"], # how many times was this retweeted
    "favorite_count: " + tweet["favorite_count"], # how many times was this favourited 
    "screen_name: " + tweet["user"]["screen_name"], # handle of the user
    "followers_count: " + tweet["user"]["followers_count"], # number of people who follow them
    "friends_count: " + tweet["user"]["friends_count"] # number of people who they follow

tweets = buildTestSet("Bitcoin")

print(tweet_to_string(tweets[0]))