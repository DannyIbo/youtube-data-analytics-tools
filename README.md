# YouTube Data Analytics Tools
Compare channels (i.e. video count, video views, video tags, links in descriptions etc.) and analyze video comments (time series, sentigment, used words count etc.)

![Example plots](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/ezgif-1-7954082339d8.gif)

## Description
The script has a browser-based user interface and runs on flask. It downloads data directly from YouTube using the Data API v3. The data gets extracted and transformed into a pandas dataframe. Matplotlib, Seaborn and WordCloud are used to save plots as images.

## Features
1. Compare channel KPIs such as video count, views, duration, un-/clickable link count and video tags and show visualizations.
2. Analyse video comments with time series and sentiments  and show visualizations.

## Installation & Requirements
- You need a YouTube Data API key to make this work. I do not publish mine here. Get your own for free at !!!![https://console.developers.google.com/](https://console.developers.google.com/)
- On Windows 10 open the comand line and type `setx YOUTUBE_API_KEY “REPLACE_THIS_TEXT_WITH_YOUR_YOUTUBE_DATA_API_KEY”`
- Clone this repository
- `pip install -r requirements.txt`

## Visualizations / Example Plots
The following example plots can be found in the repository in the folder `/example_plots`.
### Example plots: Comparing channels
The browser interface lets user compare up to 3 channels. Theoretically a comparison of more channels is possible by modifying the URL. Please check the ***'To Dos'*** for the expected limits of this work around.
#### Barplot for visualizing video counts per channel
The number of publicly available videos is counted in visualized.
![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/UCqC_GY2ZiENFz2pwL0cSfAw_UCf2WBemooP2gBBx3lrraNQw_UCCndqRyI-5Zl8Mutlq71ASw_barplot_channel_video_count.png)

#### Barplot for visualizing count of (un-)clickable links in video descriptions
In YouTube's video descriptions links need to be formatted with an `https://` to be clickable. This condition is checked and counted.

![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/UCqC_GY2ZiENFz2pwL0cSfAw_UCf2WBemooP2gBBx3lrraNQw_UCCndqRyI-5Zl8Mutlq71ASw_barplot_links.png)

#### Word Cloud for Video Tags
Video Tags are not visible in the first place for users. There are browser plug-ins that can make them visible.
![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/UCCndqRyI-5Zl8Mutlq71ASw_wordcloud.png)

#### Histogram for video durations
For each channel in the comparison a single histogram is plotted, saved and displayed.
![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/UCqC_GY2ZiENFz2pwL0cSfAw_histogram_video_duration_count.png)

#### Table of Top 5 viewed videos
A table shows the top 5 viewed videos for each channel.

	No image of the table is served at this point. Sorry.

### Example Plots: Analysing video comments
#### Time series lineplot of cumulative sum of comments
This plot shows how the number of comments and their sentiments evolved over time.
![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/mDbSFyReulk_lineplot_cumsum_video_comments_pos_neg.png)

#### Comment sentiment and like cunt scatter plot
The plot shows comments with their sentiment and on a logarithmic scaled y-axis the number of likes for these comments.
![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/mDbSFyReulk_scatterplot_sentiment_likecount.png)

#### Word Cloud for video comments
The word cloud visuaizes the most used words considering all comments and sub-comments.English stopwords are removed by default.
![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/master/example_plots/mDbSFyReulk_wordcloud.png)

## Video Examples
### Video example: Comparing channels
In 1m27s the [video](https://www.youtube.com/watch?v=Qg7F0WIKFhM) walks you through the process of comparing channels.

[![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/presentation/video_screenshots/2019124-channels.jpg)](https://www.youtube.com/watch?v=Qg7F0WIKFhM)

### Video example: Analyse video comments
In 1m24s the [video](https://www.youtube.com/watch?v=TOowWqhAbyw) walks you through the process analysing comments.

[![enter image description here](https://github.com/DannyIbo/youtube-data-analytics-tools/raw/presentation/video_screenshots/2019124-comments.jpg)](https://www.youtube.com/watch?v=TOowWqhAbyw)

## Inspiration
Working as an analyst and consultant gave me repeated tasks that took a lot of time. I wanted to automate tasks that are frequently required in the industry, especially in video production companies for the content intelligence.

## To Dos
1. Some plots show floats instead of integers, which does not make too much sense at the specific points so far and needs to be changed.
2. The plots get stored but not deleted afterwards. Deleting should be scheduled or another way needs to be found, that files do not take to much disc space.
3.  The filenames for plots used in channel comparisons consist of the channel ids right now. Technically it works fine as long as there are only three channels to compare. The more channels get compared, the longer the file names get. This could be a problem at some point for operating systems.
4. For now I was using a free API with a limit of 10.000 queries per day. This could be easily exceeded if channels have a lot of videos or videos have a lot of comments. Channels with up to 4.000 videos and videos with up 1.000 comments worked fine. Solutions would be to get a paid API or at least to estimate the query costs and predict, if the query could be executed until the end.
5. The Word Clouds exclude english stopwords right now. To make the tool applicable to more different languages, an option should be added to exclude also stopwords from other languages.
