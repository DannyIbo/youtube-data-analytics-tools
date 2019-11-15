from flask import Flask, render_template, request, redirect, url_for
# from config import config
from src import youtube_data_module_17 as ydt
from src import viz
import pandas as pd
import os


# API_KEY = config.config['YouTube']['danny']
API_KEY = os.environ.get('API_KEY')
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/select_video')
def select_video():
    result_dictionary = request.args
    query = result_dictionary['query']
    youtube = ydt.youtubeAPIkey(API_KEY)
    query_result = ydt.youtubeSearchListStatistics(youtube, q=query)
    return render_template(
        'select_video2.html',
        query_result=query_result,
        query=query
    )

@app.route('/video_comments')
def video_comments():
    video_id = request.args.get('video_id')
    youtube = ydt.youtubeAPIkey(API_KEY)
    print('Getting all comments')
    all_snippets = ydt.get_all_comments(youtube, video_id)
    print('Writing comments to dict')
    comment_dict = ydt.extract_comments(all_snippets)
    # List of images that will be displayed
    image_names = []
    print('Generating wordcloud')
    # Create wordcloud, save image, append image name
    comment_string = ydt.concat_comments(comment_dict)
    video_title = video_id
    image_names.append(viz.create_wordcloud(comment_string, stopwords=None, video_id=video_id, channel_title=video_title))
    # Extract comments and create dataframe
    comment_df = ydt.comments_to_df(all_snippets)
    # Analyse sentiment
    comment_sentiment = ydt.analyze_comment_sentiments(comment_df)
    # Split daraframes into neutral, positive, negative
    comment_sentiment2, pos_sent, neg_sent = viz.split_sentiment_pos_neg(comment_sentiment)
    # Create lineplot, save image, append name
    image_names.append(viz.lineplot_cumsum_video_comments(comment_sentiment2, video_id))
    # Plot 2
    image_names.append(viz.lineplot_cumsum_video_comments_pos_neg(comment_sentiment2, pos_sent, neg_sent, video_id))
    # Plot 3
    image_names.append(viz.scatterplot_sentiment_likecount(comment_sentiment2, pos_sent, neg_sent, video_id))
    # Calculate correlation
    like_count_sentiment_corr = round(comment_sentiment2.corr().loc['like_count'][5],2)
    return render_template(
        'video_comments2.html',
        image_names=image_names,
        like_count_sentiment_corr=like_count_sentiment_corr
    )

@app.route('/select_channels2', methods=['GET', 'POST'])
def select_channels2():
    result_dictionary = request.args
    channel_names = []
    # Extract channel ids from dict
    for channel_name in result_dictionary:
        if len(result_dictionary.get(channel_name)) > 0:
            channel_names.append(result_dictionary[channel_name])
    # Get credentials
    youtube = ydt.youtubeAPIkey(API_KEY)
    # Execut query
    query_results = {}
    for cn in channel_names:
        result = ydt.youtubeSearchList(youtube, channel_id=None, q=cn, maxResults=5, type='channel')
        query_results[cn] =  result
    return render_template(
        'select_channels3.html',
        query_results=query_results
    )

@app.route('/channels', methods=['GET', 'POST'])
def channels():
    result_dictionary = request.args
    # Extract channel_ids from request result
    channel_ids = []
    for c_id in result_dictionary:
        if len(result_dictionary[c_id]) == 24:
            channel_ids.append(result_dictionary[c_id])
    # Get credentials
    youtube = ydt.youtubeAPIkey(API_KEY)
    # Get Data
    video_df = ydt.get_channel_video_df(youtube, channel_ids)
    # List of images that will be displayed
    image_names = []
    # Create a barplot, save the image, append name to list
    image_names.append(viz.barplot_channel_video_count(video_df, channel_ids))
    # Create a barplot with counts of clickable links, save the image, append name to list
    image_names.append(viz.barplot_links(video_df, channel_ids))
    # Create histograms and wordclouds, save the images, append names to list
    channel_titles = []
    for channel_id in channel_ids:
        channel_video_df = video_df[video_df['channel_id'] == channel_id]
       # Set channel title
        channel_title = channel_video_df['channel_title'].unique()[0]
        # Append channel title
        channel_titles.append(channel_title)
        image_names.append(viz.histogram_video_duration_count_single(channel_video_df, channel_id, channel_title=channel_title))
        # Create wordcloud, save image, appen name to list
        channel_video_series = channel_video_df['tags']
        wordcloud_string = ydt.concat_listelements(channel_video_series)
        image_names.append(viz.create_wordcloud(wordcloud_string, stopwords=None, video_id=channel_id, channel_title=channel_title))
    # Modifiy dataframe for table
    metric = 'view'
    df_table = video_df.sort_values(by=f'{metric}_count',ascending=False).groupby('channel_title').head().sort_values(by=f'{metric}_count', ascending=False)[['channel_title', 'title', f'{metric}_count']].rename(columns={'channel_title':'Channel Title', 'title':'Video Title', f'{metric}_count':f'{metric.capitalize()} Count'}).set_index('Channel Title')
    df_table = df_table.reset_index()
    df_table = df_table.set_index(df_table.index + 1)
    df_table = df_table.reset_index()
    df_table = df_table.rename(columns={'index':'Rank'})
    df_table = df_table.set_index(['Rank', 'Channel Title', 'Video Title',f'{metric.capitalize()} Count'])
    df_table.reset_index(inplace=True)
    return render_template(
        'channels2.html',
        result_dictionary=result_dictionary,
        video_df=video_df,
        image_names=image_names,
        channel_ids=channel_ids,
        channel_titles=channel_titles,
        tables=[df_table.to_html(index=False, classes='table-striped')],
    )



if __name__ == '__main__':
    app.run(port=3000, debug=True)
