import warnings, urllib, time, sys
warnings.simplefilter('ignore', DeprecationWarning)

try:
    import json
except ImportError:
    import simplejson as json

from config import USERNAME, PASSWORD

FILE = "my_tweets.json"
USER_TIMELINE = "http://%s:%s@twitter.com/statuses/user_timeline.json" % (
    urllib.quote(USERNAME), urllib.quote(PASSWORD))

def load_all():
    try:
        return json.load(open(FILE))
    except IOError:
        return []

def fetch_and_save_new_tweets():
    tweets = load_all()
    old_tweet_ids = set(t['id'] for t in tweets)
    if tweets:
        since_id = max(t['id'] for t in tweets)
    else:
        since_id = None
    new_tweets = fetch_all(since_id)
    num_new_saved = 0
    for tweet in new_tweets:
        if tweet['id'] not in old_tweet_ids:
            tweets.append(tweet)
            num_new_saved += 1
    tweets.sort(key = lambda t: t['id'], reverse=True)
    # Delete the 'user' key
    for t in tweets:
        if 'user' in t:
            del t['user']
    # Save back to disk
    json.dump(tweets, open(FILE, 'w'), indent = 2)
    print "Saved %s new tweets" % num_new_saved

def fetch_all(since_id = None):
    all_tweets = []
    seen_ids = set()
    page = 0
    args = {'count': 200}
    if since_id is not None:
        args['since_id'] = since_id
    
    all_tweets_len = len(all_tweets)
    
    while True:
        args['page'] = page
        body = urllib.urlopen("%s?%s" % (USER_TIMELINE, urllib.urlencode(args))).read()
        page += 1
        tweets = json.loads(body)
        if 'error' in tweets:
            raise ValueError, tweets
        if not tweets:
            break
        for tweet in tweets:
            if tweet['id'] not in seen_ids:
                seen_ids.add(tweet['id'])
                all_tweets.append(tweet)
        #print "Fetched another %s" % (len(all_tweets) - all_tweets_len)
        all_tweets_len = len(all_tweets)
        time.sleep(2)
    
    all_tweets.sort(key = lambda t: t['id'], reverse=True)
    return all_tweets

if __name__ == '__main__':
    fetch_and_save_new_tweets()
