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
    def __load(self, dir_path):
        '''
        '''
        with open(f"{dir_path}/data.pkl", "rb") as fin:
            data_struct = pickle.load(fin)
        self.dir_path = data_struct[0]
        self.newest = data_struct[1]
        self.oldest = data_struct[2]
        self.male_ages = data_struct[3]
        self.female_ages = data_struct[4]        


    def __save(self):
        '''
        '''
        data_struct = (self.dir_path, self.newest, self.oldest, self.male_ages, self.female_ages)
        with open(f"{self.dir_path}/data.pkl", "wb") as fout:
                    pickle.dump(data_struct, fout)


    def __delete_tmp(self):
        '''
        '''
        if os.path.exists(f"{self.dir_path}/images/tmp.jpg"):
            os.unlink(f"{self.dir_path}/images/tmp.jpg")
                

    def __init__(self, new=False):
        '''
        @param new Set True to start a new Scraper (will delete all collected images in Dataset).
        '''
        dir_path = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(f"{dir_path}/images"):
            os.mkdir(f"{dir_path}/images")

        existing_data = os.path.exists(f"{dir_path}/data.pkl")
        start_new = new or (not existing_data)
        
        if not start_new:
            self.__load(dir_path)
            self.__delete_tmp()
        
        else:
            for fname in os.listdir(f"{dir_path}/images"):
                os.unlink(f"{dir_path}/images/{fname}")
            self.dir_path = dir_path
            self.newest = None 
            self.oldest = None
            self.male_ages = []
            self.female_ages = []
            self.__save()


    def image_count(self):
        '''
        '''
        return len(self.male_ages) + len(self.female_ages)


    def __bucket_ages(self, age_list):
        '''
        @param age_list A list of ages to put in buckets
        @return A dictionary matching age buckets to occurrences.
        '''
        # for now doing 10 year buckets
        buckets = {"18-27": 0, "28-37": 0, "38-47": 0, "48-57": 0, "58-67": 0, "68+": 0}
        for age in age_list:
            if age >= 18 and age < 28:
                buckets["18-27"] += 1
            elif age < 38:
                buckets["28-37"] += 1
            elif age < 48:
                buckets["38-47"] += 1
            elif age < 58:
                buckets["48-57"] += 1
            elif age < 68:
                buckets["58-67"] += 1
            else:
                buckets["68+"] += 1
        return buckets 


    def stats(self):
        '''
        @return A string of dataset stats.
        '''
        stat_str = "Dataset statistics:\n\n"
        # total images
        stat_str += f"Total images: {self.image_count()}\n\n"

        # gender breakdown
        stat_str += f"Male / female counts: \t"
        stat_str += f"{len(self.male_ages)} ({(len(self.male_ages) / self.image_count() * 100.):.2f}%) / "
        stat_str += f"{len(self.female_ages)} ({(len(self.female_ages) / self.image_count() * 100.):.2f}%)"
        stat_str += "\n\n"
        
        # total age breakdown
        stat_str += "Total age breakdown:\n"
        age_list = self.male_ages + self.female_ages
        age_buckets = self.__bucket_ages(age_list)
        sorted_buckets = sorted(age_buckets.keys())
        for key in sorted_buckets:
            stat_str += f"{key}: \t{age_buckets[key]} "
            stat_str += f"({(age_buckets[key] / self.image_count() * 100.):.2f}%)\n"
        stat_str += "\n"
        
        # male age breakdown
        stat_str += "Male age breakdown:\n"
        age_buckets = self.__bucket_ages(self.male_ages)
        for key in sorted_buckets:
            stat_str += f"{key}: \t{age_buckets[key]} "
            stat_str += f"({(age_buckets[key] / len(self.male_ages) * 100.):.2f}%)\n"
        stat_str += f"\n"

        # female age breakdown
        stat_str += "Female age breakdown:\n"
        age_buckets = self.__bucket_ages(self.female_ages)
        for key in sorted_buckets:
            stat_str += f"{key}: \t{age_buckets[key]} "
            stat_str += f"({(age_buckets[key] / len(self.female_ages) * 100.):.2f}%)\n"
        
        return stat_str


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
        total_counter = self.image_count()
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
                    # save to permanent file name
                    my_image.save(f"images/{fname}.jpg")
                except:
                    continue
                # check for deleted image, looks like this is handled by API/subreddit

                # newest/oldest updates
                if self.newest is not None:
                    if post_date > self.newest:
                        #print (f"Previous newest: {self.newest}, Next: {post_date}")
                        self.newest = post_date
                    if post_date < self.oldest:
                        #print (f"Previous oldest: {self.oldest}, Next: {post_date}")
                        self.oldest = post_date
                else:
                    self.newest = post_date
                    self.oldest = post_date 
                
                # update counts 
                if gender == 'm':
                    self.male_ages.append(age)
                else:
                    self.female_ages.append(age)
                # save data structure
                self.__save()
                session_counter += 1

                # notify
                if notify > 0 and (total_counter + session_counter) % notify == 0:
                    print (f"{datetime.now()}, Images in dataset: {total_counter + session_counter}, Date: {post_date}, URL: {post_url}")

                # break out of loop
                if session_counter >= limit:
                    break

        # delete tmp
        self.__delete_tmp()



if __name__ == "__main__":
    '''
    '''
    my_scraper = Scraper()
    
    # command input
    while 1:
        command = input("Command? [scrape/stats/quit] > ")
        if command.lower() not in ["scrape", "stats", "quit"]:
            print ("Unrecognized command.")
            continue

        elif command == "quit":
            break 

        elif command == "stats":
            print (my_scraper.stats())

        # scrape
        else:
            command = input("New scraper? (Will delete dataset) [y/n (default) /quit] > ")
            if command.lower() == "quit":
                continue
            if command.lower() in ["y", "yes"]:
                print (f"Are you sure? Current dataset ({my_scraper.image_count()} images) will be deleted.")
                command = input("Type 'yes' to confirm, enter to quit > ")
                if command.lower() == "yes":
                    my_scraper = Scraper(new=True)
                    print ("New scraper initialized, dataset deleted.")
                else:
                    print ("Dataset NOT deleted.")
                    continue
            print ("How many images do you want to scrape? ")
            limit = input("Set a limit, or 0 to scrape continuously (not recommended, might get stuck, default 1000) > ")
            if limit == "":
                limit = 1000
            elif not limit.isdigit() or int(limit) < 0:
                print ("Invalid limit.")
                continue
            else:
                limit = int(limit)
            notify = input("The terminal will notify you every X images (or 0 for no notification, default 100). X? > ")
            if notify == "":
                notify = 100
            elif not notify.isdigit() or int(notify) < 0:
                print ("Invalid notify value.")
                continue
            else:
                notify = int(notify)
            my_scraper.scrape(limit=limit, notify=notify)
