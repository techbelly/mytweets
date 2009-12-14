"""
Saves your tweets to a local file
"""

import urllib, time, sys

try:
    import json
except ImportError:
    import simplejson as json

if '-u' in sys.argv and '-p' in sys.argv:
    USERNAME=sys.argv[sys.argv.index('-u')+1]
    PASSWORD=sys.argv[sys.argv.index('-p')+1]
else:
    try:
        from config import USERNAME, PASSWORD
    except ImportError:
        print "Username and password not specified. Create a config.py file or use the -u and -p command line options"
        sys.exit()
         
if '-t' in sys.argv:
    FILE = "my_tweets.txt"
    import pickle
    
    def load_all():
        try:
            return pickle.load(open(FILE))
        except IOError:
            return []
    
    def write_all(tweets):
        pickle.dump(tweets, open(FILE, 'w'))
else:
    FILE = "my_tweets.json"
    
    def load_all():
        try:
            return json.load(open(FILE))
        except IOError:
            return []
    
    def write_all(tweets):
        json.dump(tweets, open(FILE, 'w'), indent = 2)

USER_TIMELINE = "http://%s:%s@twitter.com/statuses/user_timeline.json" % (
    urllib.quote(USERNAME), urllib.quote(PASSWORD))

def fetch_and_save_new_tweets():
    tweets=load_all()
    old_tweet_ids = set(t['id'] for t in tweets)
    if tweets:
        since_id = max(t['id'] for t in tweets)
    else:
        since_id = None
    try:
        new_tweets = fetch_all(since_id)
    except ValueError:
        print "An error occurred while getting your tweets. Check your that your username and password are correct."
        sys.exit()
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
    write_all(tweets)
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
        all_tweets_len = len(all_tweets)
        time.sleep(2)
    
    all_tweets.sort(key = lambda t: t['id'], reverse=True)
    return all_tweets



if __name__ == '__main__':
    fetch_and_save_new_tweets()
