# selfie_scraper

Scrape images from Reddit ([r/selfies](https://www.reddit.com/r/selfies/)) in order to generate a male/female classification and age prediction dataset.

Will try to determine ground truth (male/female and age) based on post title. For now, skips posts without age and gender apparent in title.


## Usage

```
python3 scraper.py
```

It should hopefully be self explanatory from there.


## To Do

- Fully document, comment, specify method types/returns, etc... probably not going to do it, sorry.


## Future

[r/selfie](https://www.reddit.com/r/selfie/) appears way more active, but it seems age and gender are less commonly in post titles. May rework code to grab images from there as well. Even if age and gender aren't in post title, store images just so I have more images to train face localization (see my [head_hunter repo](https://github.com/dliedtka/head_hunter)), which will occur before age/gender prediction. Can also more thoroughly try to parse age and gender.


## References

- https://towardsdatascience.com/scraping-reddit-data-1c0af3040768 
- https://www.reddit.com/r/pushshift/comments/vwk47r/how_can_i_download_all_images_from_a_subreddit/


## Installs

```
pip3 install psaw
```
