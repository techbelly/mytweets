#!/usr/bin/env python2.6
import oauth2 as oauth
import httplib2, urllib, time, sys, re, os, json
from csv_ext import UnicodeWriter, UnicodeReader
import urllib2

def get(url,args,retries=1):
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_TOKEN_SECRET)
    client = oauth.Client(consumer, token)
    
    for i in range(retries+1):
        resp, content = client.request("%s?%s" % (url, urllib.urlencode(args)), 'GET')
        if resp['status'] == '502':
            time.sleep(2)
        else:
            return content
        
    return "[]"

def pages_of_tweets(method, since_id):
    url = "http://twitter.com/statuses/%s.json" % method
    args = {'count': 200, 'page': 0}
    if since_id is not None:
        args['since_id'] = since_id
    while True:
        content = get(url, args)
        tweets = json.loads(content)
        if not tweets:
            break
        if 'error' in tweets:
            raise ValueError, tweets['error']
        yield tweets
        args['page'] += 1

def concatenated(lists):
    for l in lists:
        for item in l:
            yield item

def unique(items):
    seen_ids = set()
    for item in items:
        if item['id'] not in seen_ids:
            seen_ids.add(item['id'])
            yield item

def sorted_by_id(items):
    return sorted(items, key=lambda t: t['id'])

def normalize(item):
    if not re.search('://', item):
        return 'http://' + item
    else:
        return item

def dereference(url):
    redir = httplib2.Http(timeout=10)
    redir.follow_redirects = False
    redir.force_exception_to_status_code = True
    response = redir.request(normalize(url))[0]
    if 'status' in response and response['status'] == '301':
        return unicode(response['location'])
    else:
        return url

def with_urls_expanded(items):
    for tweet in items:
        try:
            url_regex = '(\A|\\b)([\w-]+://)?\S+[.][^\s.]\S*'
            url_matches = (re.search(url_regex,word) for word in tweet['text'].split())
            potential_urls = (match.group(0) for match in url_matches if match is not None)
            for url in potential_urls:
                lengthened = dereference(url)
                if not lengthened == url:
                    tweet['text'] = tweet['text'].replace(url, lengthened)
        except:
            pass
        yield tweet

def new_tweets(method, since_id):
    tweets = concatenated(pages_of_tweets(method, since_id))
    tweets = unique(tweets)
    tweets = with_urls_expanded(tweets)
    tweets = sorted_by_id(tweets)
    return tweets

def csv_fields(tweets):
    for tweet in tweets:
        yield [tweet["id"],
               tweet["user"]["screen_name"],
               tweet["user"]["id"],
               tweet["text"],
               tweet['created_at'],
               tweet["in_reply_to_status_id"],
               tweet["in_reply_to_user_id"],
               tweet["in_reply_to_screen_name"]]

def report(string):
    if sys.stdout.isatty():
        print string

def write_csv(tweets, filename):
    file = open(filename, 'ab')
    writer = UnicodeWriter(file)
    count = 0
    for tweet in csv_fields(tweets):
        writer.writerow(tweet)
        count += 1
    file.close()
    report("%d tweets added to %s" % (count, filename))

def last_tweet_id(filename):
    fields  =  UnicodeReader(open(filename))
    ids     =  (int(field[0]) for field in fields)
    return reduce(max,ids,None)

def update_csv(method, filename):
    if os.path.isfile(filename):
        since_id = last_tweet_id(filename)
    else:
        since_id = None
    tweets = new_tweets(method,since_id)
    write_csv(tweets,filename)

if __name__ == '__main__':

    try:
        response=urllib2.urlopen('http://google.com',timeout=1)
    except urllib2.URLError as err:
        print "No network connection. Giving up"
        sys.exit(1)

    try:
        from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    except ImportError:
        print "Keys and tokens not specified. Create a config.py file."
        sys.exit(1)

    if '-f' in sys.argv:
        FILE_PATH = sys.argv[sys.argv.index('-f') + 1]
    else:
        try:
            from config import FILE_PATH
        except ImportError:
            print "File_path not specified. Create a config.py file. Or use -f on the command line. Cheerio"
            sys.exit(1)

    update_csv("user_timeline", "%s/mytweets.csv" % FILE_PATH)
    update_csv("home_timeline", "%s/myfriends.csv" % FILE_PATH)
   


