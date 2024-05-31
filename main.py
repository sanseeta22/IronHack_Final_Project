import base64
import pickle
import streamlit as st
import requests
import os
from pathlib import Path

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .main {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-attachment: local;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('netflix2.png')


# Custom header with white font color
st.markdown('<h1 style="color:white;">Netflix Movie/Tv Shows Recommender</h1>', unsafe_allow_html=True)

movies = pickle.load(open('netflix_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl','rb'))
  
movie_list = movies['title'].values

# Custom CSS for the entire app
st.markdown(
    """
    <style>
    .stSelectbox label {
        color: white !important;
    }
    .stSelectbox [data-baseweb="select"] {
        background-color: transparent !important;
    }
    .stSelectbox [data-baseweb="select"] span {
        color: white !important;
    }
    .stButton button {
        background-color: #4CAF50; /* Green */
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

selected_movie = st.selectbox(
    "Select a Movie or a Tv Show from the dropdown",
    movie_list
)

def fetch_poster(movie_title, omdb_api_key):
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': omdb_api_key,
        't': movie_title
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200 and data.get('Response') == 'True':
        poster_url = data.get('Poster')
        return poster_url
    else:
        print("Failed to fetch poster for", movie_title)
        return None

def recommend(movie, omdb_api_key, movies, similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        recommended_movie_title = movies.iloc[i[0]].title
        poster_url = fetch_poster(recommended_movie_title, omdb_api_key)
        if poster_url:
            recommended_movie_posters.append(poster_url)
        else:
            # Use a placeholder image if poster is not available
            recommended_movie_posters.append('no_poster_image.png')
        recommended_movie_names.append(recommended_movie_title)

    return recommended_movie_names, recommended_movie_posters

omdb_api_key = '3ca24c50'

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie, omdb_api_key, movies, similarity)
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    for i in range(5):
        with columns[i]:
            st.markdown(f'<p style="color:white;">{recommended_movie_names[i]}</p>', unsafe_allow_html=True)
            if recommended_movie_posters[i]:
                st.image(recommended_movie_posters[i])

