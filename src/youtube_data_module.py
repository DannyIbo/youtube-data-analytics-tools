# YouTube Data Module Version 17
# -*- coding: utf-8 -*-

import os
import googleapiclient.discovery
import google_auth_oauthlib.flow
import googleapiclient.errors
import csv
import pandas as pd
import re
import datetime
import pytz
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
import sys

logger = logging.getLogger('youtube_data_module_logger')
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def video_categories(youtube, regionCode="None", part=None, id=None):
    '''Return a json file of categories and a dict, that is reduced to ids and titles'''

    video_category_dict = {'1': 'Film & Animation', '2': 'Autos & Vehicles', '10': 'Music', '15': 'Pets & Animals', '17': 'Sports', '18': 'Short Movies', '19': 'Travel & Events', '20': 'Gaming', '21': 'Videoblogging', '22': 'People & Blogs', '23': 'Comedy', '24': 'Entertainment', '25': 'News & Politics', '26': 'Howto & Style', '27': 'Education', '28': 'Science & Technology', '29': 'Nonprofits & Activism', '30': 'Movies', '31': 'Anime/Animation', '32': 'Action/Adventure', '33': 'Classics', '34': 'Comedy', '35': 'Documentary', '36': 'Drama', '37': 'Family', '38': 'Foreign', '39': 'Horror', '40': 'Sci-Fi/Fantasy', '41': 'Thriller', '42': 'Shorts', '43': 'Shows', '44': 'Trailers'}

    if part == None:
        return video_category_dict
    else:
        request = youtube.videoCategories().list(
            part=part,
            regionCode=regionCode,
            id=id
        )
        video_categories_response = request.execute()
        video_category_dict = {x['id']: x['snippet']['title'] for x in video_categories_response['items']}
        return video_categories_response

def youtubeAPIkey(DEVELOPER_KEY, OAUTHLIB_INSECURE_TRANSPORT = "1", api_service_name = "youtube", api_version = "v3"):
    '''Get YouTube Data API credentials via API Key\n
    Disable OAuthlib's HTTPS verification when running locally.\n
    *DO NOT* leave this option enabled in production.'''

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = OAUTHLIB_INSECURE_TRANSPORT
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)
    return youtube

def youtubeSearchList(youtube, channel_id=None, q=None, maxResults=50, type=None):
    '''
    Return a list of video snippets. \n Documentation: https://developers.google.com/youtube/v3/docs/search/list
    '''
    request = youtube.search().list(
        part="snippet"
        ,channelId=channel_id
        ,maxResults=maxResults
        ,q=q
        ,fields='items(id,snippet),nextPageToken',
        type=type
        )
    responseSearchList = request.execute()
    return responseSearchList

def youtubeSearchListStatistics(youtube, q=None, maxResults=10):
    '''Get video search results for a query. Returns advanced statistics such as counts forlikes, dislikes, views and comments. Return a json file.'''

    query_result = youtubeSearchList(youtube, q=q, maxResults=maxResults, type='video')

    # Create a list of video ids
    video_id_list = [x['id']['videoId'] for x in query_result['items']]

    snippets = video_snippets(youtube, video_id_list, maxResults=10, part="statistics")
    assert len(query_result['items']) == len(snippets), 'Query result length does not match statistics length.'

    counter = 0
    for i in query_result['items']:
        i['statistics'] = snippets[counter]['statistics']
        counter += 1

    return query_result

def videoIdList(youtube, channelId):
    '''
    Return a list of all public video ids (in a specific channel)
    '''
    videoIdList = []
    requestChannelsList = youtube.channels().list(
        part="contentDetails"
        ,id=channelId
        ,fields='items/contentDetails/relatedPlaylists/uploads'
    )
    responseChannelsList = requestChannelsList.execute()

    # Get upload playlist id from dictionary
    channelUploadPlaylistID = responseChannelsList.get('items')[0].get('contentDetails').get('relatedPlaylists').get('uploads')

    # Get items from upload playlist
    playlistNextPageToken = ''

    while playlistNextPageToken != None:
        requestPlaylistItems = youtube.playlistItems().list(
            part="snippet"
            ,maxResults=50
            ,pageToken=playlistNextPageToken
            ,playlistId=channelUploadPlaylistID
        )
        responsePlaylistItems = requestPlaylistItems.execute()

        for video in responsePlaylistItems['items']:
            videoIdList.append(video['snippet']['resourceId']['videoId'])

        playlistNextPageToken = responsePlaylistItems.get('nextPageToken')

    logger.info(f'The channel {channelId} has {len(videoIdList)} public videos')

    return videoIdList

def list_slice(input_list, n=50):
    '''Concatenate n list elements and return a new list of concatenations.\n
    Takes a list as input_list and an integer n for elements to concatenate.'''
    s = 0
    e = n
    list_slices = []

    while s < len(input_list):
        list_slices.append(','.join(input_list[s:e]))
        s = e
        e += n

    return list_slices

def videoSnippet(youtube, videoId, maxResults=50, part="snippet,statistics,contentDetails,player,status"):
    '''
    Return a infos of a specific video\n
    Quota costs per video and info:\n
    snippet 2
    statistics 2
    contentDetails 2
    player 0
    recordingDetails ?
    status 2
    topicDetails 2
    '''
    requestSnippet = youtube.videos().list(
        part=part
        ,id=videoId
    )
    responseSnippet = requestSnippet.execute()
    return responseSnippet

def video_snippets(youtube, video_id_list, maxResults=50, part="snippet,statistics,contentDetails,player,status"):
    '''
    Return a infos of a single or several videos. Input is a list object of video ids.\n
    Quota costs per video and info:\n
    snippet 2
    statistics 2
    contentDetails 2
    player 0
    recordingDetails ?
    status 2
    topicDetails 2
    '''
    video_id_chunks = list_slice(video_id_list, n=50)

    video_snippets =[]
    for chunk in video_id_chunks:
        responseSnippet = videoSnippet(youtube, chunk, part=part)
        [video_snippets.append(i) for i in responseSnippet['items']]

    return video_snippets


def youtubeOauth(scopes, api_service_name, api_version, client_secrets_file, OAUTHLIB_INSECURE_TRANSPORT):
    '''Disable OAuthlib's HTTPS verification when running locally. *DO NOT* leave this option enabled in production.'''
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = OAUTHLIB_INSECURE_TRANSPORT
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube_analytics = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube_analytics

def csv_videolist(filename):
    '''Open csv file and return content as object'''
    with open(filename, 'r') as wbs:
        content = csv.reader(wbs)
    return content

def to_int(string):
    '''Turn duration from text string such as 'PT1H23M09S' to an int'''
    return int(string[:-1]) if string else 0

def get_duration_sec(pt):
    '''Turn duration from text string such as 'PT1H23M09S' to an int of seconds'''
    pattern = 'PT(\d*H)?(\d*M)?(\d*S)?'
    timestamp = [to_int(x) for x in re.findall(pattern, pt)[0]]
    duration_sec = timestamp[0] * 3600 + timestamp[1] * 60 + timestamp[2]
    return duration_sec

def snippets_to_dict(video_snippet_list, yt_credentials=None):
    '''Return a dictionary from a given list of one or more video snippets.\
    The dictionary is optimized for creating a dataframe'''

    # Create an empty dictionary
    df_data = {'video_id': [],
               'published_at': [],
               'channel_id': [],
               'title': [],
               'description': [],
               'channel_title': [],
               'tags': [],
               'category_id': [],
               'category' : [],
               'live_broadcast_content': [],
               'duration': [],
               'duration_sec': [],
               'dimension': [],
               'definition': [],
               'caption': [],
               'licensed_content': [],
               'projection': [],
               'privacy_status': [],
               'license': [],
               'embeddable': [],
               'public_stats_viewable': [],
               'view_count': [],
               'like_count': [],
               'dislike_count': [],
               'favorite_count': [],
               'comment_count': [],
               'thumbnails_default': [],
               'date_data_created': []
              }

    if yt_credentials:
        video_category_dict = video_categories(yt_credentials)
    else:
        del df_data['category']

    for i in video_snippet_list:
        df_data['video_id'].append(i.get('id'))
        df_data['published_at'].append(pd.to_datetime(i.get('snippet').get('publishedAt')))
        df_data['channel_id'].append(i.get('snippet').get('channelId'))
        df_data['title'].append(i.get('snippet').get('title'))
        df_data['description'].append(i.get('snippet').get('description'))
        df_data['channel_title'].append(i.get('snippet').get('channelTitle'))
        df_data['tags'].append(i.get('snippet').get('tags'))
        df_data['category_id'].append(i['snippet'].get('categoryId'))

        if yt_credentials:
            df_data['category'] = video_category_dict[i['snippet'].get('categoryId')]

        df_data['live_broadcast_content'].append(i['snippet'].get('liveBroadcastContent'))
        df_data['duration'].append(i['contentDetails'].get('duration'))

        duration_text = i['contentDetails'].get('duration')
        df_data['duration_sec'].append(get_duration_sec(duration_text))

        df_data['dimension'].append(i['contentDetails'].get('dimension'))
        df_data['definition'].append(i['contentDetails'].get('definition'))
        df_data['caption'].append(i['contentDetails'].get('caption'))
        df_data['licensed_content'].append(i['contentDetails'].get('licensedContent'))
        df_data['projection'].append(i['contentDetails'].get('projection'))
        df_data['privacy_status'].append(i['status'].get('privacyStatus'))
        df_data['license'].append(i['status'].get('license'))
        df_data['embeddable'].append(i['status'].get('embeddable'))
        df_data['public_stats_viewable'].append(i['status'].get('publicStatsViewable'))
        df_data['view_count'].append(int(i['statistics'].get('viewCount') or 0))
        df_data['like_count'].append(int(i['statistics'].get('likeCount') or 0))
        df_data['dislike_count'].append(int(i['statistics'].get('dislikeCount') or 0))
        df_data['favorite_count'].append(int(i['statistics'].get('favoriteCount') or 0))
        df_data['comment_count'].append(int(i['statistics'].get('commentCount') or 0))
        df_data['thumbnails_default'].append(i.get('snippet').get('thumbnails').get('default').get('url'))
        df_data['date_data_created'].append(datetime.datetime.now(tz=pytz.UTC))

    return df_data

def get_channel_snippet(youtube, channel_id, nextPageToken=None):
    '''Get a cannel snippet. Take as input a string of one channel_id or a concatenated string of ids separated by commas without spaces.'''
    request = youtube.channels().list(
        part="snippet",
        id=channel_id,
        maxResults=50,
        pageToken=nextPageToken
    )
    response = request.execute()
    return response


def get_comment_threads(
    youtube,
    part="id,replies,snippet",
    channel_id=None,
    comment_thread_id=None,
    video_id=None,
    maxResults=100
):
    '''Return a .json with top-level comments and meta data. Take as input the youtube credential object and the videoId.\n
    Specify exactly one filter out of: channel_id, comment_thread_id, video_id.\n
    See detailied info in the documentation: https://developers.google.com/youtube/v3/docs/commentThreads/list \n
    Quota costs: id: 0, replies: 2, snippet: 2'''

    # Get items from upload playlist
    commentThreadsNextPageToken = ''
    output = []

    # Calculate the costs for query
    costs = 0
    cost_per_query = 0
    if 'replies' in part:
        cost_per_query += 2
    if 'snippet' in part:
        cost_per_query += 2

    while commentThreadsNextPageToken != None:
        costs += cost_per_query
        request = youtube.commentThreads().list(
            part=part,
            maxResults=maxResults,
            videoId=video_id,
            id=comment_thread_id,
            channelId=channel_id,
            pageToken = commentThreadsNextPageToken
        )
        response = request.execute()
        [output.append(x) for x in response['items']]
        commentThreadsNextPageToken = response.get('nextPageToken')

    if costs > 0:
        logger.info(f'Comment thread query costs: {costs}')

    return output


def comment_threads_to_dict(comments):
    '''Return a dictionary. Take as input a .json file with toplevel comments from threads'''
    df_data = {
    'comment_id':[],
    'author_display_name':[],
    'author_profile_image_url':[],
    'author_channel_url':[],
    'author_channel_id':[],
    'text_display':[],
    'text_original':[],
    'parent_id':[],
    'can_rate':[],
    'viewer_rating':[],
    'like_count':[],
    'published_at':[],
    'updated_at':[],
    'canReply':[],
    'total_reply_count':[],
    'is_public':[]}

    logger.info('Start writing comment threads to dict')

    for i in comments:
        if i.get('snippet').get('topLevelComment'):
            df_data['comment_id'].append(i['id'])
            df_data['author_display_name'].append(i['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            df_data['author_profile_image_url'].append(i['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'])
            df_data['author_channel_url'].append(i['snippet']['topLevelComment']['snippet']['authorChannelUrl'])
            df_data['author_channel_id'].append(i['snippet']['topLevelComment']['snippet']['authorChannelId']['value'])
            df_data['text_display'].append(i['snippet']['topLevelComment']['snippet']['textDisplay'])
            df_data['text_original'].append(i['snippet']['topLevelComment']['snippet']['textOriginal'])
            df_data['parent_id'].append(i['snippet']['topLevelComment']['snippet'].get('parentId'))
            df_data['can_rate'].append(i['snippet']['topLevelComment']['snippet']['canRate'])
            df_data['viewer_rating'].append(i['snippet']['topLevelComment']['snippet']['viewerRating'])
            df_data['like_count'].append(i['snippet']['topLevelComment']['snippet']['likeCount'])
            df_data['published_at'].append(i['snippet']['topLevelComment']['snippet']['publishedAt'])
            df_data['updated_at'].append(i['snippet']['topLevelComment']['snippet']['updatedAt'])
            df_data['canReply'].append(i['snippet']['canReply'])
            df_data['total_reply_count'].append(i['snippet']['totalReplyCount'])
            df_data['is_public'].append(i['snippet']['isPublic'])

        if i.get('replies'):
            for c in i['replies']['comments']:
                df_data['comment_id'].append(c['id'])
                df_data['author_display_name'].append(c['snippet']['authorDisplayName'])
                df_data['author_profile_image_url'].append(c['snippet']['authorProfileImageUrl'])
                df_data['author_channel_url'].append(c['snippet']['authorChannelUrl'])
                df_data['author_channel_id'].append(c['snippet']['authorChannelId']['value'])
                df_data['text_display'].append(c['snippet']['textDisplay'])
                df_data['text_original'].append(c['snippet']['textOriginal'])
                df_data['parent_id'].append(c['snippet'].get('parentId'))
                df_data['can_rate'].append(c['snippet']['canRate'])
                df_data['viewer_rating'].append(c['snippet']['viewerRating'])
                df_data['like_count'].append(c['snippet']['likeCount'])
                df_data['published_at'].append(c['snippet']['publishedAt'])
                df_data['updated_at'].append(c['snippet']['updatedAt'])
                df_data['canReply'].append(c['snippet'].get('canReply'))
                df_data['total_reply_count'].append(c['snippet'].get('totalReplyCount'))
                df_data['is_public'].append(c['snippet'].get('isPublic'))
    logger.info('Done writing comment threads to dict')
    return df_data


def get_comments_list(youtube, part="id", maxResults=100, parent_id=None, id=None):
    '''Return a list of ids and/or snippets for a given comment id. Specify exactly one filter out of: parentId, id.\n
    Take as filter input a string of comma seperated parentIds/ids. Maximum is 50,even though max of maxResults=100.
    Quota costs for 'part' paramter: id: 0, snippet: 1.\n
    Idea for improvement: Calculate the most efficient way, if sippets should be retrieved by the get_comments_list() or get_comments_threads()'''
    # Set false NextPageToken and empty output list
    commentThreadsNextPageToken = ''
    output = []

    # Setup calculation for the costs for query
    costs = 0
    cost_per_query = 0
    if 'snippet' in part:
        cost_per_query += 2

    # Loop as long as there are next pages of results

    while commentThreadsNextPageToken != None:
        # Increment costs
        costs += cost_per_query
        # Do the youtube request
        request = youtube.comments().list(
            part=part,
            maxResults=maxResults,
            parentId=parent_id,
            id=id
        )
        response = request.execute()

        # Append each element sepeerately to the output list
        [output.append(x) for x in response['items']]
        # Get a NextPageToken in case there is one, else set it to None
        commentThreadsNextPageToken = response.get('nextPageToken')

    # Print costs
    if costs > 0:
        logger.info(f'Comment list query costs: {costs}')

    return response

def list_slice(input_list, n=50):
    '''Concatenate n list elements separated by ',' and return a new list of concatenations.\n
    Takes a list as input_list and an integer n for elements to concatenate.'''
    s = 0
    e = n
    list_slices = []
    while s < len(input_list):
        list_slices.append(','.join(input_list[s:e]))
        s = e
        e += n
    return list_slices

def comment_list_to_dict(reply_comments_snippets):
    '''Return a dictionary. Take as input a .json file'''
    df_data = {
    'comment_id':[],
    'author_display_name':[],
    'author_profile_image_url':[],
    'author_channel_url':[],
    'author_channel_id':[],
    'text_display':[],
    'text_original':[],
    'parent_id':[],
    'can_rate':[],
    'viewer_rating':[],
    'like_count':[],
    'published_at':[],
    'updated_at':[]}

    logger.info('Start writing comment list to dict')
    for i in reply_comments_snippets:
        if i.get('id'):
            df_data['comment_id'].append(i['id'])
            df_data['author_display_name'].append(i['snippet']['authorDisplayName'])
            df_data['author_profile_image_url'].append(i['snippet']['authorProfileImageUrl'])
            df_data['author_channel_url'].append(i['snippet']['authorChannelUrl'])
            df_data['author_channel_id'].append(i['snippet']['authorChannelId']['value'])
            df_data['text_display'].append(i['snippet']['textDisplay'])
            df_data['text_original'].append(i['snippet']['textOriginal'])
            df_data['parent_id'].append(i['snippet'].get('parentId'))
            df_data['can_rate'].append(i['snippet']['canRate'])
            df_data['viewer_rating'].append(i['snippet']['viewerRating'])
            df_data['like_count'].append(i['snippet']['likeCount'])
            df_data['published_at'].append(i['snippet']['publishedAt'])
            df_data['updated_at'].append(i['snippet']['updatedAt'])
    logger.info('Done writing comment list to dict')
    return df_data


def get_all_comments(youtube, video_id):

    logger.info('Starting to get comment threads')
    # Get list of snippets of threads
    thread_snippets = get_comment_threads(youtube, part="snippet,replies", video_id=video_id)
    logger.info('Done getting comment threads')

    # Check if the thread comments have more than 5 replies and if true append the id to a dict
    thread_ids_with_more_replies = {}
    already_downloaded_replies = {}

    # Loop through threads and search for >5 replies
    for t_id in thread_snippets:
        if t_id['snippet']['totalReplyCount'] > 5:

            # Wite parent_id of threads with >5 replies to dict index
            thread_ids_with_more_replies[t_id['id']] = True

            # This print statement tries to evaluate an error, that I couldn't fix yet
            logger.info(t_id['id'], 'has more than 5 replies')
            if t_id.get('replies') != None:

                # Write reply id to dict
                for reply_id in t_id['replies']['comments']:
                    already_downloaded_replies[reply_id['id']] = True
            else:
                # This print statement tries to evaluate an error, that I couldn't fix yet
                logger.info(f"* * * * * {t_id['id']} would throw a key error for 'replies' * * * * * ")

    # Get a list of reply ids for thread ids with more than 5 replies
    # Slice list into strings of 50 ids each
    strings_of_thread_ids_with_more_replies = list_slice(list(thread_ids_with_more_replies), n=50)

    # Create empty dict for reply ids
    reply_ids = {}

    # Loop through thread ids with >5 replies
    logger.info('Start getting reply comment ids, that were not downloaded yet')
    for id_string in thread_ids_with_more_replies:
        # Get the reply ids
        replies = get_comments_list(youtube, part="id", parent_id=id_string, id=None)
        # Write the reply ids into a dict, if they are not downlaoded yet
        for r_id in replies['items']:
            if r_id['id'] not in already_downloaded_replies:
                reply_ids[r_id['id']] = True
    logger.info('Done getting reply comment ids, that were not downloaded yet')

    # Create a list with id strings
    strings_of_reply_ids = list_slice(list(reply_ids), n=50)

    # Create empty list for new reply snippets
    reply_snippets = []

    # Get reply snippets, that were not downloaded yet
    logger.info('Start downloading reply comments, that were not downloaded yet')
    for id_string in strings_of_reply_ids:
        r_snippets = get_comments_list(youtube, part="snippet", parent_id=None, id=id_string)
        reply_snippets += r_snippets['items']
    logger.info('Done downloading reply comments, that were not downloaded yet')

    # Create an empty list for already downloaded replies (that came with threads)
    already_downloaded_replies = []

    # Loop through threads and search for >0 replies
    for t_id in thread_snippets:
        # Add already downloaded replies to list
        if t_id['snippet']['totalReplyCount'] > 0:
            already_downloaded_replies += t_id['replies']['comments']

    # Add thread snippets + reply snippets together
    all_snippets = thread_snippets + reply_snippets + already_downloaded_replies
    return all_snippets

def extract_comments(comments):
    '''Extract comments from a json file.Return a dictionary. Take as input the result of function "get_all_comments()"'''
    comment_dict = {}
    for c in comments:
        if c['kind'] == 'youtube#commentThread':
            comment_dict[c['id']] = c['snippet']['topLevelComment']['snippet']['textOriginal']
        else:
            comment_dict[c['id']] = c['snippet']['textOriginal']
    return comment_dict

def concat_comments(comment_dict):
    '''Concat comment in values of a dictionary and return one string. Used for WordCloud input data.'''
    string = ''
    for i, c in comment_dict.items():
        result = re.findall('[a-z0-9]+', c.lower())
        string += ' '.join(result) + ' '
    return string

def concat_listelements(series_object):
    '''Concat elements in lists in series objects and return them as a string. Needed as input for a wordcloud.'''
    result = ''
    for tag_list in series_object:
        if tag_list:
            for tag in tag_list:
                result += ' ' + ''.join(tag).upper()
    return result

def comments_to_df(all_comments):
    '''Extract comments from "get_all_comments()" json and return a dataframe.'''

    new_dict = {
    'id':[],
    'text_original':[],
    'like_count':[],
    'published_at':[],
    'total_reply_count':[]
    }

    for c in all_comments:
        if c['kind'] == 'youtube#commentThread':
            new_dict['id'].append(c['id'])
            new_dict['like_count'].append(c['snippet']['topLevelComment']['snippet']['likeCount'])
            new_dict['text_original'].append(c['snippet']['topLevelComment']['snippet']['textOriginal'])
            new_dict['published_at'].append(pd.to_datetime(c['snippet']['topLevelComment']['snippet']['publishedAt'], utc=True))
            new_dict['total_reply_count'].append(c['snippet']['totalReplyCount'])
        else:
            new_dict['id'].append(c['id'])
            new_dict['like_count'].append(c['snippet']['likeCount'])
            new_dict['text_original'].append(c['snippet']['textOriginal'])
            new_dict['published_at'].append(pd.to_datetime(c['snippet']['publishedAt'], utc=True))
            new_dict['total_reply_count'].append(c['snippet'].get('totalReplyCount'))

    comment_df = pd.DataFrame(data=new_dict).set_index('id')
    return comment_df

def analyze_comment_sentiments(comment_df):
    '''Analyse sentiment. Take as input a comment dataframe from "comments_to_df()"'''
    analyzer = SentimentIntensityAnalyzer()

    sentiment = {
        'neg':[],
        'neu':[],
        'pos':[],
        'compound':[]
    }

    for comment in comment_df['text_original']:
        vs = analyzer.polarity_scores(comment)
        for k, v in vs.items():
            sentiment[k].append(v)

    sentiment_df = pd.DataFrame(data=sentiment)
    comment_sentiment = pd.concat([comment_df.reset_index(), sentiment_df], axis=1)
    return comment_sentiment

def get_channel_video_df(youtube, channel_ids):
    '''Get video data for a list of given channel ids and return a concatenated dataframe.'''

    video_df = pd.DataFrame([])
    for channel_id in channel_ids:

        if video_df.empty == True:
            # Get list of video ids
            v_list = videoIdList(youtube, channel_id)

            # Get data for videos
            video_snippet_list = video_snippets(youtube, v_list, maxResults=50)

            # Write data to a dict
            video_data_dict = snippets_to_dict(video_snippet_list, yt_credentials=youtube)

            # Insert data into a dataframe
            video_df = pd.DataFrame(video_data_dict)

        else:
            # Get list of video ids
            v_list = videoIdList(youtube, channel_id)

            # Get data for videos
            video_snippet_list = video_snippets(youtube, v_list, maxResults=50)

            # Write data to a dict
            video_data_dict = snippets_to_dict(video_snippet_list, yt_credentials=youtube)

            # Insert data into a dataframe
            video_df_temp = pd.DataFrame(video_data_dict)

            # Cancatenate dataframes
            video_df = pd.concat([video_df, video_df_temp])

    return video_df
