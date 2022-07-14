# selfie_scraper

Attempting to scrape images from Reddit (r/selfies) in order to generate a male/female classification and age prediction dataset.

Will try to determine ground truth (male/female and age) based on post title.


## Eventual Workflow

1. Scrape images for dataset.
2. Crop images to just faces.
    - Try to implement on own with CNN object localization. This will require making images squares and then resizing to the same resolution.
    - Could look for existing face localization implementations.
3. Implement gender classifier and age prediction CNNs.
    - Will need to again square and resize face images to same resolution.
    - Will age prediction work better with classification age buckets or as a regression problem?


## To Do

- Implement stats
- Change main function to take command input
- Fully document, comment, specify method types/returns, etc.


## References

- https://towardsdatascience.com/scraping-reddit-data-1c0af3040768 
- https://www.reddit.com/r/pushshift/comments/vwk47r/how_can_i_download_all_images_from_a_subreddit/


## Installs

```
pip3 install psaw
```
