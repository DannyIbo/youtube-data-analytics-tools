# YouTube Data Analytics Tools

## Main functionalities
1. Compare channel KPIs such as video count, views, duration, un-/clickable link count and video tags
2. Analyse video comments with time series and sentiments

## Description
The script has a browser-based user interface and runs on flask. It downloads data directly from YouTube using the Data API v3. The data gets extracted and transformed into a pandas dataframe. Matplotlib, Seaborn and WordCloud are used to save plots as images.

## Visualizations
### Comparing channels
####
![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/55643f54091b48010f99100ddbfaa07257149178/static/images/UCV9pZxcKWF6fZ1ZQzDWofgw_barplot_links.png)
### Analysing video comments

## Demo
### Comparing channels
<iframe width="560" height="315" src="https://www.youtube.com/embed/Qg7F0WIKFhM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

### Analyse video comments
<iframe width="560" height="315" src="https://www.youtube.com/embed/TOowWqhAbyw" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Requirements
You need a YouTube Data API to make this work. I do not publish mine here.
Get your own for free at [https://console.developers.google.com/](https://console.developers.google.com/)


## Inspiration
Working as an analyst and consultant gave me repeated tasks that took a lot of time. I wanted to automate tasks that are frequently required in the industry, especially in video production companies for he content intelligence.

## To Dos
1. Some plots show floats instead of integers, which does not make too much sense at the specific points so far and needs to be changed.
2. The plots get stored but not deleted afterwards. Deleting should be scheduled or another way needs to be found, that files do not take to much disc space.
3.  The filenames for plots used in channel comparisons consist of the channel ids right now. Technically it works fine as long as there are only three channels to compare. The more channels get compared, the longer the file names get. This could be a problem at some point for operating systems.
4. For now I was using a free API with a limit of 10.000 queries per day. This could be easily exceeded if channels have a lot of videos or videos have a lot of comments. Channels with up to 4.000 videos and videos with up 1.000 comments worked fine. Solutions would be to get a paid API or at least to estimate the query costs and predict, if the query could be executed until the end.
