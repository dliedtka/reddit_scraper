#!/usr/bin/env python3

# goal of this script is just to pull an image and comments from r/selfies

import praw 
#import requests
import re
import urllib.request
from PIL import Image


def make_square(im, min_size=100, fill_color=(0, 0, 0, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGB', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im


def determine_age_gender(title):
    age = None
    gender = None
    
    candidate = re.search("[\[\(].*?[\]\)]", title)
    if candidate is not None:
        candidate = candidate.group()[1:-1].lower()
    
        for i in range(len(candidate)-1):
            if candidate[i:i+2].isdigit():
                age = candidate[i:i+2]
    
        if 'm' in candidate:
            gender = 'm'
        elif 'f' in candidate:
            gender = 'f'
    
    if age is None or gender is None:
        return "test"
    else:
        return age+gender


with open("app_auth.txt", "r") as fin:
    auth_data = fin.read().split()

reddit = praw.Reddit(client_id=auth_data[0], client_secret=auth_data[1], user_agent=auth_data[2])

new_posts = reddit.subreddit('selfies').new(limit=10)
# check out using after/before
# save dates or earliest and latest post for future scraping sessions?


counter = 0
for post in new_posts:
    counter += 1

    post_title = post.title
    post_url = post.url
    #print (post_title)
    #print (post_url)

    # try to get age and gender, if you can't get it put in test set
    age_gender = determine_age_gender(post_title)
    # informs filename
    fname = f"images/{counter:06}_{age_gender}"

    '''
    # needed for r/rateme, not for r/selfies
    counter = 0
    while counter == 0 or r.status_code != 200:
        counter += 1
        r = requests.get(post_url)

    print (f"got it after {counter} tries")

    html = r.content.decode("utf-8")
    img_link = re.search("<img src=\".*?\"", html).group()[len("<img src=\""):-1].replace("amp;", "")
    print (img_link)

    # if "blur" is in URL, may just want to skip (have to click to unblur)
    # how to handle videos? Maybe just get a None
    '''

    # now to save image to file
    urllib.request.urlretrieve(post_url, f"{fname}.jpg")

    # make image a square
    try:
        my_image = Image.open(f"{fname}.jpg")
        make_square(my_image).save(f"{fname}.jpg")
    except:
        counter -= 1
        pass

    print ("")
