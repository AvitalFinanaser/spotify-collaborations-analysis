import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import pandas as pd

# ~ Spotify songs extraction from 'Top songs of 2000-2023' playlist

# Load credentials from a JSON file
credentials = json.load(open('credentials.json'))
client_id = credentials['client_id']
client_secret = credentials['client_secret']

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Provided playlist URL
playlist_url = 'https://open.spotify.com/playlist/6Q1m6h43xSG5yiT4gzDHoW?si=4dd439e990974000'

# Extract playlist ID from URL
playlist_id = playlist_url.split('/')[-1].split('?')[0]

# Fetch playlist tracks
results = sp.playlist_tracks(playlist_id)
playlist_tracks_data = results['items']

# Initialize lists to store track details
playlist_tracks_id = []
playlist_tracks_titles = []
playlist_tracks_artists = []
playlist_tracks_first_artists = []
playlist_tracks_genres = []
playlist_tracks_album_desc = []

# Extract track details
for track in playlist_tracks_data:
    playlist_tracks_id.append(track['track']['id'])
    playlist_tracks_titles.append(track['track']['name'])

    # Add a list of all artists involved in the song to the list of artists for the playlist
    artist_list = []
    for artist in track['track']['artists']:
        artist_list.append(artist['name'])
    playlist_tracks_artists.append(artist_list)
    playlist_tracks_first_artists.append(artist_list[0])

    # Fetch additional track details
    track_details = sp.track(track['track']['id'])
    album_id = track_details['album']['id']

    # Fetch album description
    album_details = sp.album(album_id)
    playlist_tracks_album_desc.append(album_details.get('description', 'No description available'))

    # Fetch artist genres
    artist_id = track_details['artists'][0]['id']
    artist_details = sp.artist(artist_id)
    genres = artist_details.get('genres', [])
    playlist_tracks_genres.append(genres if genres else ['No genres available'])

# Fetch audio features
features = sp.audio_features(playlist_tracks_id)

# Convert features to DataFrame
features_df = pd.DataFrame(data=features, columns=features[0].keys())
features_df['title'] = playlist_tracks_titles
features_df['first_artist'] = playlist_tracks_first_artists
features_df['all_artists'] = playlist_tracks_artists
features_df['genres'] = playlist_tracks_genres
features_df['album_description'] = playlist_tracks_album_desc

# Select relevant columns
features_df = features_df[['id', 'title', 'first_artist', 'all_artists', 'genres', 'album_description',
                           'danceability', 'energy', 'key', 'loudness', 'mode', 'acousticness',
                           'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']]

# Save the DataFrame to a CSV file
output_file_path = r"C:\Users\avita\Downloads\playlist_features.csv"
features_df.to_csv(output_file_path, index=False, encoding='utf-8')

print(f"Playlist features saved to {output_file_path}")

# ~ Spotify songs extraction from 'Top songs of 2000-2023' playlist

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json

# Load credentials from a JSON file
credentials = json.load(open('credentials.json'))
client_id = credentials['client_id']
client_secret = credentials['client_secret']

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to extract MetaData from a playlist that's longer than 100 songs
def get_playlist_tracks_more_than_100_songs(username, playlist_id):
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    print(f"Total tracks fetched: {len(tracks)}")

    # Initialize lists to store track details
    playlist_tracks_id = []
    playlist_tracks_titles = []
    playlist_tracks_artists = []
    playlist_tracks_first_release_date = []
    playlist_tracks_popularity = []

    # Extract track details
    for i, track in enumerate(tracks):
        print(f"Processing track {i + 1}/{len(tracks)}")
        playlist_tracks_id.append(track['track']['id'])
        playlist_tracks_titles.append(track['track']['name'])
        playlist_tracks_first_release_date.append(track['track']['album']['release_date'])
        playlist_tracks_popularity.append(track['track']['popularity'])

        artist_list = [artist['name'] for artist in track['track']['artists']]
        playlist_tracks_artists.append(artist_list)

    # Fetch audio features in batches
    def fetch_audio_features_in_batches(track_ids, batch_size=100):
        features = []
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            features.extend(sp.audio_features(batch))
        return features

    print("Fetching audio features...")
    audio_features = fetch_audio_features_in_batches(playlist_tracks_id)

    # Convert features to DataFrame
    print("Converting features to DataFrame...")
    features_df = pd.DataFrame(data=audio_features, columns=audio_features[0].keys())
    features_df['title'] = playlist_tracks_titles
    features_df['all_artists'] = playlist_tracks_artists
    features_df['popularity'] = playlist_tracks_popularity
    features_df['release_date'] = playlist_tracks_first_release_date

    # Select relevant columns
    features_df = features_df[['id', 'title', 'all_artists', 'popularity', 'release_date',
                               'danceability', 'energy', 'key', 'loudness', 'mode', 'acousticness',
                               'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']]

    return features_df

df_spotify = pd.read_csv(r"C:\\Users\\avita\\Downloads\\playlist_features_2000-2023.csv", encoding='utf-8')

### Artists collaborations count

import pandas as pd
from collections import defaultdict

# Load the dataset
df = pd.read_csv(r"C:\Users\avita\Downloads\playlist_features_2000-2023.csv")

# Initialize a list to store edges
edges = []

# Extract collaborations
for artists in df['all_artists']:
    artist_list = eval(artists)  # Convert string representation of list back to list
    if len(artist_list) > 1:
        for i in range(len(artist_list)):
            for j in range(i + 1, len(artist_list)):
                edges.append([artist_list[i], artist_list[j]])

# Initialize a dictionary to count collaborations for each artist
collaborations_count = defaultdict(int)

# Count collaborations
for edge in edges:
    collaborations_count[edge[0]] += 1
    collaborations_count[edge[1]] += 1

# Convert the dictionary to a DataFrame and sort it
collaborations_df = pd.DataFrame(list(collaborations_count.items()), columns=['artist', 'collaborations'])
collaborations_df = collaborations_df.sort_values(by='collaborations', ascending=False)

# Save the results to a CSV file
output_path = r"C:\Users\avita\Downloads\artist_collaborations_count.csv"
collaborations_df.to_csv(output_path, index=False, encoding='utf-8')

print(f"Artist collaborations count saved to {output_path}")

# ~ Artist features - getting more artists properties

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
import time

df_spotify = pd.read_csv(r"C:\\Users\\avita\\Downloads\\playlist_features_2000-2023.csv", encoding='utf-8')
df_spotify.isnull().sum()

# Extract unique artists
unique_artists = []
for index, row in df_spotify.iterrows():
    artists = eval(row['all_artists'])
    for artist in artists:
        unique_artists.append(artist)

unique_artists = list(set(unique_artists))
# Number of different artists
len(unique_artists)

# Load credentials from a JSON file
credentials = json.load(open('credentials.json'))
client_id = credentials['client_id']
client_secret = credentials['client_secret']

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Initialize lists to store artist features
artist_ids = []
artist_names = unique_artists
artist_followers = []
artist_popularity = []
artist_genres = []

# Fetch artist features
for i, artist_name in enumerate(artist_names):
    try:
        print(f"Processing artist {i + 1}/{len(artist_names)}: {artist_name}")
        results = sp.search(q=f'artist:{artist_name}', type='artist')
        if results['artists']['items']:
            artist = results['artists']['items'][0]
            artist_ids.append(artist['id'])
            artist_followers.append(artist['followers']['total'])
            artist_popularity.append(artist['popularity'])
            artist_genres.append(artist['genres'] if artist['genres'] else ['No genres available'])
        else:
            print(f"No results found for artist: {artist_name}")
            artist_ids.append('N/A')
            artist_followers.append(0)
            artist_popularity.append(0)
            artist_genres.append(['No genres available'])
    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify API error: {e}")
        if e.http_status == 429:  # Rate limit exceeded
            retry_after = int(e.headers.get('Retry-After', 10))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue
    except Exception as e:
        print(f"Error processing artist {artist_name}: {e}")
        artist_ids.append('N/A')
        artist_followers.append(0)
        artist_popularity.append(0)
        artist_genres.append(['No genres available'])

# Create a DataFrame for artist features
artist_features_df = pd.DataFrame({
    'artist_id': artist_ids,
    'artist': artist_names,
    'followers': artist_followers,
    'popularity': artist_popularity,
    'genres': artist_genres
})

# Save the artist features DataFrame to a CSV file
artist_features_df.to_csv('C:\\Users\\avita\\Downloads\\artist_features.csv', index=False, encoding='utf-8')

# Look at outliers
errored_artists = artist_features_df[(artist_features_df['followers'] == 0) | (artist_features_df['popularity'] == 0)]

# ~ Genres

artist_features_df = pd.read_csv(r"C:\\Users\\avita\\Downloads\\artist_features_unclean.csv", encoding='utf-8')

# Extract unique artists
unique_generes = []
for index, row in artist_features_df.iterrows():
    genres = eval(row['genres'])
    for genere in genres:
        unique_generes.append(genere)
unique_generes = list(set(unique_generes))
# Number of different artists
len(unique_generes)

# Update the 'genres' column to keep only the first genre
artist_features_df['genres'] = artist_features_df['genres'].apply(
    lambda x: eval(x)[0] if isinstance(eval(x), list) and eval(x) else 'No genres available')
unique_generes = artist_features_df['genres'].unique()
len(unique_generes)

# Define core genres
core_genres = ['pop', 'rock', 'hip hop', 'rap', 'r&b', 'country', 'latin', 'electronic', 'jazz', 'classical', 'metal',
               'indie', 'folk', 'reggae', 'dance', 'soul', 'funk']


# Function to map genre to core genre
def map_to_core_genre(genre):
    genre = genre.lower()  # Convert genre to lowercase for comparison
    for core_genre in core_genres:
        if core_genre in genre:
            return core_genre
    return genre


# Apply the mapping function to the 'genres' column
artist_features_df['genre'] = artist_features_df['genres'].apply(map_to_core_genre)
unique_generes = artist_features_df['genre'].unique()
len(unique_generes)

# Specific generes
specific_generes = [genre for genre in unique_generes if genre not in core_genres]

core_genres_specific = {
    'pop': ['scottish singer-songwriter', 'chill guitar', 'neo mellow', 'girl group', 'british soul', 'alt z',
            'new french touch', 'boy band', 'gen z singer-songwriter', 'kleinkunst', 'nouvelle chanson francaise',
            'irish singer-songwriter', 'lustrum', 'show tunes', 'soul', 'irish pop', 'folk-pop', 'indie pop',
            'neo soul'],
    'rock': ['canadian punk', 'birmingham grime', 'old school hard trance', 'grunge', 'british invasion', 'beatlesque',
             'acoustic punk', 'emo'],
    'electronic': ['elctro house', 'white noise', 'electro house', 'drum and bass', 'edm', 'house', 'lo-fi chill',
                   'aussietronica', 'uk funky', 'nordic house', 'dutch house', 'calming instrumental', 'ambeat',
                   'tech house', 'hypertechno', 'deep groove house', 'sped up', 'slap house', 'electro', 'complextro',
                   'breaks', 'deep euro house', 'deep house', 'disco house', 'downtempo', 'dutch trance', 'hip house',
                   'brostep', 'basshall', 'covertronica', 'beats', 'escape room', 'gaming edm', 'dark clubbing',
                   'funktronica', 'instrum', 'melbourne bounce international', 'classic hardstyle'],
    'hip hop': ['g funk', 'afrobeats', 'melodic drill', 'brooklyn drill', 'birmingham grime', 'uk funky',
                'drill francais'],
    'r&b': ['gospel', 'neo soul', 'southern soul', 'bedroom soul', 'afro soul', 'british soul'],
    'latin': ['kompa', 'gruperas inmortales', 'axe', 'corrido', 'banda', 'carnaval'],
    'metal': ['american melodeath'],
    'funk': ['funk', 'blues'],
    'folk': ['shanty'],
    'jazz': ['jawaiian'],
}

# Create a reverse mapping from specific genre to core genre
specific_to_core_mapping = {}
for core, specifics in core_genres_specific.items():
    for specific in specifics:
        specific_to_core_mapping[specific] = core


# Function to map specific genre to core genre
def map_to_specific_genre(genre):
    return specific_to_core_mapping.get(genre, 'pop')


# Apply manually mapping
artist_features_df['genre'] = artist_features_df['genre'].apply(
    lambda x: map_to_specific_genre(x) if x in specific_generes else x)

# Check if all the mapping worked - yes!
len([genre for genre in artist_features_df['genre'].unique() if genre not in core_genres])

# Drop the genres column
artist_features_df = artist_features_df.drop('genres', axis=1)

# Save the new artist's features df
artist_features_df.to_csv('C:\\Users\\avita\\Downloads\\artist_features_clean.csv', index=False, encoding='utf-8')

# SNA - Network representation

import pandas as pd
from collections import defaultdict

# ~ Edge list

df_spotify = pd.read_csv(r"playlist_features_2000-2023.csv", encoding='ISO-8859-1')

# Initialize a dictionary to store collaboration counts
collaborations = defaultdict(int)

# Iteration on each song and add the collaboration between each pair
for index, row in df_spotify.iterrows():
    artists = eval(row['all_artists'])  # Convert the string representation of the list back to a list
    if len(artists) > 1:  # There is more than one artist preforming in the song
        for i in range(len(artists)):
            for j in range(i + 1, len(artists)):
                artist_pair = tuple(sorted([artists[i], artists[j]]))
                collaborations[artist_pair] += 1

# Create a DataFrame for the edge list
edges = pd.DataFrame([(a, b, count) for (a, b), count in collaborations.items()],
                     columns=['Source', 'Target', 'Weight'])

edges.to_csv('edges_cleaned.csv', index=False, encoding='utf-8')

# Edges with ID

# Load the data

df_spotify = pd.read_csv(r"playlist_features_2000-2023.csv", encoding='ISO-8859-1')

# Initialize a dictionary to store collaboration counts
collaborations = defaultdict(int)

# Iterate over the rows to count collaborations
for index, row in df_spotify.iterrows():
    artists = eval(row['all_artists'])  # Convert the string representation of the list back to a list
    if len(artists) > 1:
        for i in range(len(artists)):
            for j in range(i + 1, len(artists)):
                artist_pair = tuple(sorted([artists[i], artists[j]]))
                collaborations[artist_pair] += 1

# Create a mapping from artist names to their unique IDs
artist_id_map = {}
for index, row in df_spotify.iterrows():
    artists = eval(row['all_artists'])
    for artist in artists:
        if artist not in artist_id_map:
            artist_id_map[artist] = row['id']

# Create a DataFrame for the edge list
edges = pd.DataFrame([(artist_id_map[a], artist_id_map[b], count) for (a, b), count in collaborations.items()],
                     columns=['Source', 'Target', 'Weight'])

# ~ Nodes list

df_artist_features = pd.read_csv(r"C:\\Users\\avita\\Downloads\\artist_features_clean.csv", encoding='utf-8')

# Rename columns to fit Gephi's expected format
df_artist_features = df_artist_features.rename(columns={
    'artist': 'Label',
    'artist_id': 'ID',
    'followers': 'Followers',
    'popularity': 'Popularity',
    'clean_genre': 'Genre'
})

df_artist_features.to_csv('C:\\Users\\avita\\Downloads\\nodes.csv', index=False, encoding='utf-8')

# Filter the graph according to degree

# Load graph

import pandas as pd

df_nodes = pd.read_csv(r"nodes.csv", encoding='utf-8')
df_edges = pd.read_csv(r"edges.csv", encoding='utf-8')

df_nodes.columns
df_edges.columns

unique = df_nodes["ID"].unique()

errors = [a for a in df_edges["Source"] if a not in unique]

# Filter the graph according to degree 2

import pandas as pd

# Load the data
nodes = pd.read_csv('nodes.csv')
edges = pd.read_csv('edges.csv')

# Calculate the degree of each node
degree = pd.concat([edges['Source'], edges['Target']]).value_counts()

# Filter nodes with a degree of 2 or higher
filtered_nodes = nodes[nodes['ID'].isin(degree[degree >= 3].index)]

# Filter edges to only include those with both source and target in the filtered nodes
filtered_edges = edges[
    (edges['Source'].isin(filtered_nodes['ID'])) &
    (edges['Target'].isin(filtered_nodes['ID']))
    ]

# Save the filtered data
filtered_nodes.to_csv('filtered_degree3_nodes.csv', index=False, encoding='utf-8')
filtered_edges.to_csv('filtered_degree3_edges.csv', index=False, encoding='utf-8')

# Filter the data according to connection components greater than 1

degree = pd.concat([edges['Source'], edges['Target']]).value_counts()

# Identify nodes with a degree of 1
single_connection_nodes = degree[degree == 1].index

# Create a set for quick lookup
single_connection_nodes_set = set(single_connection_nodes)

# Identify edges where both nodes have a degree of 1
edges_to_remove = edges[
    edges['Source'].isin(single_connection_nodes_set) &
    edges['Target'].isin(single_connection_nodes_set)
    ]

# Filter out these edges and nodes
nodes_to_remove = set(edges_to_remove['Source']).union(set(edges_to_remove['Target']))
filtered_nodes = nodes[~nodes['ID'].isin(nodes_to_remove)]
filtered_edges = edges[~edges['Source'].isin(nodes_to_remove) & ~edges['Target'].isin(nodes_to_remove)]

# Ensure no remaining nodes with degree 0
remaining_nodes_with_edges = set(filtered_edges['Source']).union(set(filtered_edges['Target']))
filtered_nodes = filtered_nodes[filtered_nodes['ID'].isin(remaining_nodes_with_edges)]

# Save the filtered data
filtered_nodes.to_csv('filtered_nodes.csv', index=False, encoding='utf-8')
filtered_edges.to_csv('filtered_edges.csv', index=False, encoding='utf-8')

# Centrality measurements

import pandas as pd

nodes_df = pd.read_csv('Giant_nodes.csv')

# Identify the top centralized artists
degree_top = nodes_df.sort_values(by='Degree', ascending=False).head(10)
closeness_top = nodes_df.sort_values(by='Closeness', ascending=False).head(10)
harmonic_closeness_top = nodes_df.sort_values(by='Harmonic Closeness', ascending=False).head(10)
betweenness_top = nodes_df.sort_values(by='Between', ascending=False).head(10)

# Display the top artists for each centrality measure
print("Top artists by Degree:")
print(degree_top[['ID', 'Followers', 'Genre', 'Degree', 'Closeness', 'Harmonic Closeness', 'Between']])
print("\nTop artists by Closeness:")
print(closeness_top[['Artist', 'Followers', 'Genre', 'Degree', 'Closeness', 'Harmonic Closeness', 'Between']])
print("\nTop artists by Harmonic Closeness:")
print(harmonic_closeness_top[['Artist', 'Followers', 'Genre', 'Degree', 'Closeness', 'Harmonic Closeness', 'Between']])
print("\nTop artists by Betweenness:")
print(betweenness_top[['Artist', 'Followers', 'Genre', 'Degree', 'Closeness', 'Harmonic Closeness', 'Between']])

# ~ Communities

import pandas as pd
import networkx as nx
import community as community_louvain
from networkx.algorithms.community import greedy_modularity_communities, girvan_newman, modularity

# Load data
edges = pd.read_csv('Giant_edges.csv')
nodes = pd.read_csv('Giant_nodes.csv')

# Create graph
G = nx.Graph()

# Add nodes with attributes
for _, row in nodes.iterrows():
    G.add_node(row['ID'], followers=row['Followers'], genre=row['Genre'])

# Add edges with weights
for _, row in edges.iterrows():
    G.add_edge(row['Source'], row['Target'], weight=row['Weight'])

# Algorithm 0 - Greedy Modularity Communities

greedy_communities = list(greedy_modularity_communities(G))
greedy_modularity_score = modularity(G, greedy_communities)
print(f"Greedy Modularity: {round(greedy_modularity_score, 2)}")


# Algorithm 1 - Girvan-Newman based on edge betweenness

def girvan_newman_optimized(G):
    comp = girvan_newman(G)
    max_modularity = -1
    best_communities = None

    for communities in comp:
        current_modularity = modularity(G, communities)
        if current_modularity > max_modularity:
            max_modularity = current_modularity
            best_communities = communities

    return best_communities, max_modularity


gn_communities, gn_modularity = girvan_newman_optimized(G)
print(f"Girvan-Newman Modularity:  {round(gn_modularity, 2)}")

# Algorithm 2 - Louvain
import community as community_louvain


def louvain_communities(G):
    partition = community_louvain.best_partition(G, weight='weight', resolution=1, random_state=140)
    communities = {}
    for node, comm in partition.items():
        if comm not in communities:
            communities[comm] = []
        communities[comm].append(node)
    return list(communities.values())

# Louvain Communities
louvain_communities = louvain_communities(G)

gn_communities, gn_modularity = girvan_newman_optimized(G)
print(f"Girvan-Newman Modularity:  {round(gn_modularity, 2)}")

# Algorithm 2 - Louvain Modularity

print(f"Louvain Modularity:  {round(louvain_modularity, 2)}")


# Algorithm 3 - k_core

def k_core_communities(G):
    max_k = max(dict(G.degree()).values())
    best_k = 0
    max_modularity = -1
    best_communities = None

    for k in range(1, max_k + 1):
        subgraph = nx.k_core(G, k)
        communities = [list(c) for c in nx.connected_components(subgraph)]

        # Ensure there are multiple communities to compare
        if len(communities) > 1:
            current_modularity = modularity(G, communities)
            if current_modularity > max_modularity:
                max_modularity = current_modularity
                best_communities = communities
                best_k = k

    return best_communities, max_modularity, best_k


# K-Core Communities with k optimization
k_core_communities, k_core_modularity, best_k = k_core_communities(G)

# The chosen communities

# Add community information to each node
nx.set_node_attributes(G, community_dict, 'community')

# Create a DataFrame to store community information
community_df = pd.DataFrame.from_dict(community_dict, orient='index', columns=['Community'])
community_df = community_df.reset_index().rename(columns={'index': 'ID'})

# Merge with node attributes
community_df = community_df.merge(nodes, on='ID')











# NLP - songs lyrics

# ~~~~~~~~ Retrieving the lyrics for the songs

import pandas as pd
import lyricsgenius

# Load the dataset
df = pd.read_csv(r"C:\\Users\\avita\\Downloads\\playlist_features_2000-2023.csv",
                 encoding='ISO-8859-1')  # Use raw string, double backslashes, or forward slashes

# Initialize Genius API
genius_token = '1AXg1V6UF5W-tnkoAIC_lFosZZBNfoKjEBOskjb7VLOT_LZHEY9bekZSThhOGlTJ'
genius = lyricsgenius.Genius(genius_token)


# Function to get song lyrics from Genius
def get_lyrics(track_name, artist_name):
    try:
        song = genius.search_song(track_name, artist_name)
        return song.lyrics if song else 'Lyrics not found'
    except Exception as e:
        return f'Error: {e}'


# Add a new column for lyrics
df['lyrics'] = df.head(10).apply(lambda row: get_lyrics(row['title'], ', '.join(eval(row['all_artists']))), axis=1)
a = df['lyrics'][2]
# Save the updated dataset to a new CSV file
df.to_csv('C:\\Users\\avita\\Downloads\\spotify-2000-2023-with-lyrics.csv', index=False)

print("Lyrics added and dataset saved")

# Data Pre-processing

import pandas as pd
import lyricsgenius

df = pd.read_csv("spotify_2000-2023.csv", encoding='ISO-8859-1')
df_no_duplicates = df.drop_duplicates(subset=['title'])
df_no_nulls = df_no_duplicates.dropna()
df_prev = pd.read_csv(r"C:\\Users\\avita\\Downloads\\playlist_features_2000-2023.csv", encoding='ISO-8859-1')
df_filtered = df_no_nulls[df_no_nulls['title'].isin(df_prev['title'])]
df_filtered.shape

duplicates = df[df.duplicated(subset=['title'], keep=False)]
errored_lyrics = df_filtered[
    (df_filtered['lyrics'] == 'Lyrics not found') | (df_filtered['lyrics'].str.startswith('Error:'))]

# Initialize Genius API
genius_token = '1AXg1V6UF5W-tnkoAIC_lFosZZBNfoKjEBOskjb7VLOT_LZHEY9bekZSThhOGlTJ'
genius = lyricsgenius.Genius(genius_token)


# Function to get song lyrics from Genius
def get_lyrics(track_name, artist_name):
    try:
        song = genius.search_song(track_name, artist_name)
        return song.lyrics if song else 'Lyrics not found'
    except Exception as e:
        return f'Error: {e}'


# Find rows with errored lyrics
errored_lyrics = df[(df['lyrics'] == 'Lyrics not found') | (df['lyrics'].str.startswith('Error:'))]

# Retry fetching the lyrics for the errored rows
for index, row in errored_lyrics.iterrows():
    track_name = row['title']
    artist_name = row['all_artists']  # Change this to the correct column name for artist
    new_lyrics = get_lyrics(track_name, artist_name)
    df_filtered.at[index, 'lyrics'] = new_lyrics

# ~~~~~~~~ NLP pre-processing

import pandas as pd
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string
import re

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from wordcloud import WordCloud

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Load dataset
df_spotify = pd.read_csv("playlist_features_2000-2023_lyrics.csv", encoding='ISO-8859-1')
# Lowercase the column name "Lyrics"
df_spotify.rename(columns={'Lyrics': 'lyrics'}, inplace=True)

# Dataset Preview
print(f"Shape of lyrics dataset: {df_spotify.shape}")
df_spotify.head()

# Check null values
df_spotify.info()
df_spotify.isnull().sum()

# Drop all musics without lyric - 117 songs
df_spotify = df_spotify.dropna()

# Drop duplicates
duplicates = df_spotify[df_spotify.duplicated()]
df_spotify_clean = df_spotify.drop_duplicates(subset=['id'], keep='first')
# 775 songs remained
df_spotify_clean.shape

# ~ Preprocess song lyrics

# Initiating preprocess aspects

# Stop words
stop_words = stopwords.words('english')
# Extend stopwords to remove other common stopwords, musical terms and slangs
stop_words.extend([
    'verse', 'chorus', 'i"ll', 'intro', 'outro', 'or', 'm', 'ma', 'ours', 'against', 'nor',
    'wasn', 'hasn', 'my', 'had', 'didn', 'isn', 'did', 'aren', 'those', 'than', 'man'
    "mustn't", "you've", 'to', 'she', 'having', "haven't", 'into', 't', 'll',
    'himself', 'do', "that'll", 'so', 'of', 'on', 'very', 'for', 'out', 'were',
    'should', 'they', 'ain', "should've", 'you', "didn't", 'yours', 'was', 'our',
     'can', 'myself', "shouldn't", 'have', 'up', 'mightn', "you'll", 'any',
    'itself', 'hadn', 'him', 'doesn', 'weren', 'y', 'being', "don't", 'them',
    'are','and', 'that', 'your', 'yourself', 'their', 'some', 'ourselves', 've',
    'doing', 'been', 'shouldn', 'yourselves', "mightn't", 'most', 'because',
     'few', 'wouldn', "you'd", 'through', "you're", 'themselves', 'an', 'if',
     "wouldn't", 'its', 'other', "won't", "wasn't", "she's", 'we', 'shan',
     "weren't",'don',"hadn't", 'this', 'off', 'while', 'a', 'haven', 'her',
    'theirs', 'all', "hasn't", "doesn't", 'about', 'then', 'by','such', 'but',
    'until', 'each', 'there', "aren't", 'with', 'not', "shan't", 'hers', 'it',
    'too', 'i', 'at', 'is', 'as', 'me', 'herself', 's', 'the', 'where', 'am',
    'has', 'over', "couldn't", 'when', 'does', 'mustn','re', 'no', 'in', 'who',
    'd', 'own', 'he', 'be', "isn't", 'his', 'these', 'same', 'whom', 'will',
    'needn','couldn', 'from',  "it's", 'o', 'yeah','ya','na','wan','uh','gon',
    'ima','mm','uhhuh','bout','em','nigga','niggas','got','ta','lil','ol','hey',
    'oooh','ooh','oh','youre','dont','im','youve','ive','theres','ill','yaka',
    'lalalala','la','da','di','yuh', 'shawty','oohooh','shoorah','mmmmmm',
    'ook','bidibambambambam','shh','bro','ho','aint','cant','know','bambam',
    'shitll','tonka'
])
stop_words = set(stop_words)

# Lemmatization
lemmatizer = WordNetLemmatizer()

# Regular expression pattern to identify new line characters
newline_pattern = re.compile(r'\n')

def preprocess_lyrics(lyrics):
    # Convert to lowercase
    lyrics = lyrics.lower()

    # Remove punctuation
    lyrics = lyrics.translate(str.maketrans('', '', string.punctuation))

    # Remove new line character - \n
    lyrics = newline_pattern.sub(' ', str(lyrics))

    # Tokenization
    words = word_tokenize(lyrics)

    # Remove stop words, non-alphabetic words, and lemmatize
    words = [lemmatizer.lemmatize(word) for word in words if word.isalpha() and word not in stop_words]

    return ' '.join(words)

# Apply preprocessing to the 'lyrics' column
df_spotify_clean['lyrics'] = df_spotify_clean['lyrics'].apply(preprocess_lyrics)
df_spotify_clean.to_csv('lyrics.csv' ,index=False, encoding='utf-8')





