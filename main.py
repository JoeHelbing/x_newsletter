#%%
import os
from datetime import datetime, timedelta, timezone
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import tweepy
import pandas as pd

from dotenv import load_dotenv
load_dotenv()
client = tweepy.Client(bearer_token=os.getenv("TWITTER_BEARER_TOKEN"))

#%%
today     = datetime.now(timezone.utc).date()
yesterday = today - timedelta(days=1)

start_time = datetime(
    yesterday.year, yesterday.month, yesterday.day,
    tzinfo=timezone.utc
).isoformat()
end_time = datetime(
    yesterday.year, yesterday.month, yesterday.day,
    23, 59, 59, tzinfo=timezone.utc
).isoformat()
# In[3]: define your single OR‑batch query
query = (
    "from:karpathy OR from:jeremyphoward"
    " -is:retweet"
)
# In[4]: call and inspect the raw Response
response = client.search_recent_tweets(
    query=query,
    start_time=start_time,
    end_time=end_time,
    tweet_fields=["id", "text", "created_at", "conversation_id", "referenced_tweets"],
    expansions=["referenced_tweets.id"],
    max_results=100
)
print(response)           # full namedtuple: .data, .includes, .errors, .meta
print(response.meta)      # paging info (next_token, result_count)  [oai_citation_attribution:1‡Tweepy Documentation](https://docs.tweepy.org/en/stable/examples.html?utm_source=chatgpt.com)
print(response.data[:3])  # first three Tweet objects
# In[5]: paginate through all pages, filter for thread‑starters, collect
tweets = []
for tweet in tweepy.Paginator(
    client.search_recent_tweets,
    query=query,
    start_time=start_time,
    end_time=end_time,
    tweet_fields=["id", "text", "created_at", "conversation_id"],
    expansions=["referenced_tweets.id"],
    max_results=100
).flatten(limit=500):
    # keep only the root of each thread
    if tweet.conversation_id == tweet.id:
        tweets.append({
            "tweet_id":   tweet.id,
            "created_at": tweet.created_at,
            "text":       tweet.text
        })
# In[6]: load into a DataFrame and display
df = pd.DataFrame(tweets)
df.head()  # first few results
