import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from src import sql
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Plot configurations
FIG_W = 10 # Width of plots
FIG_H = 5 # Height of plots
ROT = 0 # Rotation of x-axis labels
TS = 15 # Title size

def barplot_channel_video_count(df_all, channel_ids):
    '''Create a barplot and save the image to a folder. Return image name. Take a dataframe with videodata  as input. Input channel_ids to render image name.'''

    channel_ids_string = '_'.join(channel_ids)
    image_name = f'static/images/{channel_ids_string}_barplot_channel_video_count.png'

    plt.figure(figsize=(FIG_W, FIG_H))
    df_all.groupby('channel_title').size().sort_values(ascending=False).plot.bar()
    plt.xticks(rotation=ROT)
    plt.xlabel("Channel Name")
    plt.ylabel("Video Count")
    plt.title('Video Counts per Channel', fontdict = {'fontsize' : TS})
    plt.savefig(image_name, dpi=100)

    return image_name

def histogram_video_duration_count(df_all, channel_ids):
    '''Create a histogram and save the image to a folder. Return image name. Take a dataframe with videodata  as input. Input channel_ids to render image name.'''

    df_all['duration_min'] = df_all['duration_sec'].astype('int') / 60

    # Calculate outlier and clean them
    outlier = (df_all['duration_min'].describe()['75%'] - df_all['duration_min'].describe()['25%']) * 1.5 + df_all['duration_min'].describe()['75%']
    df_all = df_all[df_all['duration_min'] <= outlier]

    bin_size = int(df_all['duration_min'].max())
    labels = df_all['channel_title'].unique()

    data = []
    for channel in labels:
        video_durations = df_all[df_all['channel_title'] == channel]['duration_min'].to_numpy()
        data.append(video_durations)

    # Create image name
    channel_ids_string = '_'.join(channel_ids)
    image_name = f'static/images/{channel_ids_string}_histogram_video_duration_count.png'

    plt.figure(figsize=(FIG_W, FIG_H))
    plt.hist(data, bins=bin_size, alpha=0.5)
    plt.legend(labels)
    plt.xlabel('Duration of videos in minutes')
    plt.ylabel('Videos count')
    plt.title('Video counts of durations', fontdict = {'fontsize' : TS})
    plt.savefig(image_name, dpi=100)

    return image_name

def histogram_video_duration_count_single(df_all, channel_id, channel_title=None):
    '''Create a histogram and save the image to a folder. Return image name. Take a dataframe with videodata  as input. Input channel_ids to render image name.'''

    df_all = df_all[df_all['channel_id'] == channel_id]

    # Calculate outlier and clean them
    outlier = (df_all['duration_sec'].describe()['75%'] - df_all['duration_sec'].describe()['25%']) * 1.5 + df_all['duration_sec'].describe()['75%']
    df_all = df_all[df_all['duration_sec'] <= outlier]

    df_all['duration_min'] = df_all['duration_sec'] / 60
    df_all['duration_min'] = df_all['duration_min'].astype('int32')

    bin_size = df_all['duration_min'].max()
    if bin_size < 1:
        bin_size = 1

    image_name = f'static/images/{channel_id}_histogram_video_duration_count.png'

    plt.figure(figsize=(FIG_W, FIG_H))
    plt.hist(df_all['duration_min'], bins=bin_size, alpha=0.5, edgecolor='black', linewidth=1)
    plt.legend(df_all['channel_title'].unique())
    plt.title(f'Video Counts of Durations for "{channel_title}"', fontdict = {'fontsize' : TS})
    plt.xlabel('Video Duration in Minutes')
    plt.ylabel('Video Count')
    plt.xlim(0,bin_size)
    plt.savefig(image_name, dpi=100)

    return image_name

def barplot_links(video_df, channel_ids):
    '''Create a barplot with counts on how many video descriptions hae clickable links. Save the plot as image.'''

    # Check if there is 'http' in description and insert result
    video_df['Links in decription'] = video_df['description'].str.contains('http').apply(lambda x: 'Clickable Link' if x else 'No clickable Link')

    channel_ids_string = '_'.join(channel_ids)
    image_name = f'static/images/{channel_ids_string}_barplot_links.png'

    video_df = video_df.groupby(['channel_title', 'Links in decription'])[['video_id']].count().reset_index()
    sns.set(style="whitegrid")
    g = sns.catplot(x="channel_title",
                    y="video_id",
                    hue="Links in decription",
                    data=video_df,
                    height=6,
                    kind="bar",
                    palette="muted"
    )
    g.despine(left=True)
    g.set_xlabels("Channel Name")
    g.set_ylabels("Video Count")
    # g.set_title('Links in Video Descriptions', fontdict = {'fontsize' : TS})
    plt.savefig(image_name, dpi=100)

    return image_name

def create_wordcloud(text, stopwords=STOPWORDS,video_id=None, channel_title=None):
    '''Return a word cloud image name and save the image. Take as input a string of text and a video id or a channel name for creating the title.'''

    wordcloud = WordCloud(
        max_font_size=50,
        min_font_size=10,
        max_words=100,
        prefer_horizontal=1,
        # for transparnt background: mode='RGBA', background_color=None
        # mode="RGBA",
        background_color="white",
        stopwords=stopwords,
        # Increase for lager images
        scale=2.0,
        # Disable word pairs
        collocations=False
    ).generate(text)

    # Create filename
    if video_id == None:
        temp_id = sql.set_temp_id()
        image_name = f'static/images/{temp_id}_wordcloud.png'
    else:
        image_name = f'static/images/{video_id}_wordcloud.png'

    if channel_title:
        title = channel_title
    else:
        title = video_id

    plt.figure(figsize = (FIG_W, FIG_H))
    plt.title(f'Wordcloud for "{title}"', fontdict = {'fontsize' : TS})
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(image_name, dpi=100)

    return image_name

def split_sentiment_pos_neg(comment_sentiment):
    '''Split dataframe into positive, neutral and negative dataframes. Used for plotting.'''

    comment_sentiment.sort_values(by='published_at', inplace=True)
    comment_sentiment['count'] = 1
    comment_sentiment['cumsum'] = comment_sentiment['count'].cumsum()

    # Select negative and poitive comments
    neg_sent = comment_sentiment[comment_sentiment['compound'] < -0.5]
    neg_sent['count'] = 1
    neg_sent['cumsum'] = neg_sent['count'].cumsum()
    pos_sent = comment_sentiment[comment_sentiment['compound'] > 0.5]
    pos_sent['count'] = 1
    pos_sent['cumsum'] = pos_sent['count'].cumsum()

    return comment_sentiment, pos_sent, neg_sent

def lineplot_cumsum_video_comments(comment_sentiment, video_id):
    '''Create and save a lineplot for the cumsum of video comments over time. Return image name.'''

    image_name = f'static/images/{video_id}_lineplot_cumsum_video_comments.png'

    plt.figure(figsize=(FIG_W, FIG_H))
    plt.plot(comment_sentiment['published_at'], comment_sentiment['cumsum'])
    plt.xticks(rotation=ROT)
    plt.title('Cumulative sum of comments over time', fontdict = {'fontsize' : TS})
    plt.xlabel('Date')
    plt.ylabel('Sum of comments')
    plt.grid(b=True)
    plt.savefig(image_name, dpi=100)

    return image_name

def lineplot_cumsum_video_comments_pos_neg(comment_sentiment, pos_sent, neg_sent, video_id):
    '''Create and save a lineplot for the cumsum of positive and negative sentiments of video comments over time seperately. Return image name.'''

    image_name = f'static/images/{video_id}_lineplot_cumsum_video_comments_pos_neg.png'

    plt.figure(figsize=(FIG_W, FIG_H))
    plt.plot('published_at', 'cumsum', data=pos_sent, marker='', color='green', linewidth=1, linestyle='-', label="Positive Sentiment")
    plt.plot('published_at', 'cumsum', data=neg_sent, marker='', color='red', linewidth=1, linestyle='-', label="Negative Sentiment")
    plt.legend()
    plt.title('Cumulative sum of comments over time', fontdict = {'fontsize' : TS})
    plt.xlabel('Date')
    plt.ylabel('Sum of comments')
    plt.xticks(rotation=ROT)
    plt.grid(b=True)
    plt.savefig(image_name, dpi=100)

    return image_name

def scatterplot_sentiment_likecount(comment_sentiment, pos_sent, neg_sent, video_id):
    '''Create a scatterplot with like counts vs.sentiment. Save image.Return image name. Take as input the output of "split_sentiment_pos_neg()" and a video id.'''

    image_name = f'static/images/{video_id}_scatterplot_sentiment_likecount.png'

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    plt.scatter(comment_sentiment['compound'], np.log1p(comment_sentiment['like_count']), label='Neutral Sentiment')
    plt.scatter(pos_sent['compound'], np.log1p(pos_sent['like_count']), color='green', label='Positive Sentiment')
    plt.scatter(neg_sent['compound'], np.log1p(neg_sent['like_count']), color='red', label='Negative Sentiment')
    plt.xticks(rotation=ROT)
    plt.title('Sentiment / Like count', fontdict = {'fontsize' : TS})
    plt.xlabel('Sentiment')
    plt.ylabel('Logarithm of Like count')
    plt.legend()
    plt.grid(b=True)
    fig.savefig(image_name, dpi=100)

    return image_name

def top_videos(video_df, metric='view', n=5):
    '''Return a table with top n videos of all channels in the dataframe considering a given metric. Possible metrics are like, dislike, comment and view'''

    df_table = video_df.sort_values(by=f'{metric}_count',ascending=False).groupby('channel_title').head(n).sort_values(by=f'{metric}_count', ascending=False)[['channel_title', 'title', f'{metric}_count']].rename(columns={'channel_title':'Channel Title', 'title':'Video Title', f'{metric}_count':f'{metric.capitalize()} Count'}).set_index('Channel Title')
    df_table = df_table.reset_index()
    df_table = df_table.set_index(df_table.index + 1)
    df_table = df_table.reset_index()
    df_table = df_table.rename(columns={'index':'Rank'})
    df_table = df_table.set_index(['Rank', 'Channel Title', 'Video Title',f'{metric.capitalize()} Count'])
    df_table.reset_index(inplace=True)

    return df_table
