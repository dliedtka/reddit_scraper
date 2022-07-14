#!/usr/bin/env python3

import os
import pickle
import re
from psaw import PushshiftAPI
from datetime import datetime
import urllib.request
from PIL import Image



class Scraper:
    '''
    '''
    def __init__(self, new=False):
        '''
        @param new Set True to start a new Scraper (will delete all collected images in Dataset).
        '''
        dir_path = os.path.dirname(os.path.abspath(__file__))
        existing_data = os.path.exists(f"{dir_path}/data.pkl")
        start_new = new or (not existing_data)
        
        if not start_new:
            with open(f"{dir_path}/data.pkl", "rb") as fin:
                self.dir_path, self.newest, self.oldest = pickle.load(fin)
        
        else:
            for fname in os.listdir(f"{dir_path}/images"):
                os.unlink(f"{dir_path}/images/{fname}")
            self.dir_path = dir_path
            self.newest = None 
            self.oldest = None
            with open(f"{dir_path}/data.pkl", "wb") as fout:
                pickle.dump((self.dir_path, self.newest, self.oldest), fout)


    def __image_count(self):
        '''
        '''
        counter = 0
        for fname in os.listdir(f"{self.dir_path}/images"):
            if "tmp.jpg" not in fname:
                counter += 1
        return counter


    def stats(self):
        '''
        '''
        pass 


    def __determine_age_gender(self, title):
        '''
        @param title The title of the post.
        '''
        age = None
        gender = None
        
        candidate = re.search("[\[\(].*?[\]\)]", title)
        if candidate is not None:
            candidate = candidate.group()[1:-1].lower()
        
            for i in range(len(candidate)-1):
                if candidate[i:i+2].isdigit():
                    age = int(candidate[i:i+2])
        
            if 'm' in candidate:
                gender = 'm'
            elif 'f' in candidate:
                gender = 'f'
        
        return (age, gender)


    def scrape(self, before=None, limit=0, notify=0):
        '''
        @param limit Set to stop scraping after this many images, or 0 to scrape indefinitely.
        @param notify Set to get notified whenever you scrape that many images, or 0 for no notification.
        @param before If set, collect images older than that date time.
        '''
        # api call
        api = PushshiftAPI()
        posts = api.search_submissions(
            before=before,
            subreddit="selfies",
            filter=["url", "date", "title"],
        )

        session_counter = 0
        total_counter = self.__image_count()
        # loop over posts indefinitely
        for post in posts:
            post_url = post.url
            post_title = post.title
            post_date = datetime.fromtimestamp(post.created_utc)
            if post_url[-4:] == ".jpg":
                # newest/oldest checks
                if self.newest is not None and (post_date <= self.newest and post_date >= self.oldest):
                    # recursive call specifying before
                    # allows us to skip over already collected images between newest and oldest
                    self.scrape(before=self.oldest, limit=(limit-session_counter), notify=notify)
                    break
                
                # try to get age and gender, for now skip if you can't
                age, gender = self.__determine_age_gender(post_title)
                if age is None or gender is None or age < 18:
                    continue
                else:
                    age_gender_str = f"{age}{gender}"
                # informs filename
                fname = f"{(total_counter + session_counter):06}_{age_gender_str}"

                try:
                    # save image to file
                    urllib.request.urlretrieve(post_url, f"images/tmp.jpg")
                    # check for image corruption
                    my_image = Image.open(f"images/tmp.jpg")
                except:
                    continue
                # check for deleted image

                # newest/oldest updates
                update = False
                if self.newest is not None:
                    if post_date > self.newest:
                        #print (f"Previous newest: {self.newest}, Next: {post_date}")
                        self.newest = post_date
                        update = True 
                    if post_date < self.oldest:
                        #print (f"Previous oldest: {self.oldest}, Next: {post_date}")
                        self.oldest = post_date
                        update = True
                else:
                    self.newest = post_date
                    self.oldest = post_date 
                    update = True
                # pickle dump
                if update:
                    with open(f"{self.dir_path}/data.pkl", "wb") as fout:
                        pickle.dump((self.dir_path, self.newest, self.oldest), fout)
                
                # save to permanent file name
                my_image.save(f"images/{fname}.jpg")
                session_counter += 1

                # notify
                if notify > 0 and (total_counter + session_counter) % notify == 0:
                    print (f"Counter: {total_counter + session_counter}, Date: {post_date}, URL: {post_url}")

                # break out of loop
                if session_counter >= limit:
                    break



if __name__ == "__main__":
    '''
    '''
    # convert main function to command input

    my_scraper = Scraper(new=True)
    my_scraper.scrape(limit=10, notify=5)

    my_scraper2 = Scraper()
    my_scraper2.scrape(limit=10, notify=5)
                    