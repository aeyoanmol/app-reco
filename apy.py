import streamlit as st
import pickle
import pandas as pd
import requests
import random

OMDB_API_KEY = '6b9b2450'

#Fetch poster + details using OMDb API
def fetch_movie_details(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "poster": data.get("Poster") if data.get("Poster") != "N/A" else "https://via.placeholder.com/500x750?text=No+Poster",
            "rating": data.get("imdbRating", "N/A"),
            "plot": data.get("Plot", "N/A"),
            "year": data.get("Year", "N/A")
        }
    except Exception as e:
        print(f"OMDb fetch error for '{title}':", e)
        return {
            "poster": "https://via.placeholder.com/500x750?text=No+Poster",
            "rating": "N/A",
            "plot": "N/A",
            "year": "N/A"
        }

#  Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

#  Recommendation engine
def recommend(movie_name):
    movie_index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommendations = []
    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        recommendations.append(movie_title)
    return recommendations

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

# Search History using session state
if 'history' not in st.session_state:
    st.session_state.history = []

# 🎛Movie Selection
movie_list = movies['title'].values
selected_movie_name = st.selectbox("Select a movie", movie_list)

# Surprise Me Button
if st.button("🎲 Surprise Me!"):
    selected_movie_name = random.choice(movie_list)
    st.success(f"Random pick: {selected_movie_name}")

#  Recommend Button
if st.button("Recommend"):
    recommendations = recommend(selected_movie_name)
    st.session_state.history.append(selected_movie_name)

    # Layout
    cols = st.columns(5)
    recommended_data = []

    for i, movie_title in enumerate(recommendations):
        details = fetch_movie_details(movie_title)
        recommended_data.append({
            'Title': movie_title,
            'IMDb Rating': details['rating'],
            'Year': details['year'],
            'Plot': details['plot']
        })
        with cols[i]:
            st.image(details['poster'], use_container_width=True)
            st.markdown(f"**{movie_title}**")
            st.markdown(f"⭐ IMDb: {details['rating']}  \n📅 Year: {details['year']}")
            st.caption(details['plot'][:200] + "...")

    #  Download Button
    df_download = pd.DataFrame(recommended_data)
    st.download_button("⬇️ Download Recommendations as CSV", df_download.to_csv(index=False), file_name="recommendations.csv")
