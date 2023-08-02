import os

import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox
from dotenv import load_dotenv

from api.omdb import OMDBApi
from recsys import ContentBaseRecSys

from PIL import Image

st.set_page_config(
    page_title="Movie Recommender Service",
    page_icon=":cinema:",
    layout="wide",
    initial_sidebar_state="expanded",
)

TOP_K = 5
load_dotenv()

API_KEY = os.getenv("API_KEY")
MOVIES = os.getenv("MOVIES")
DISTANCE = os.getenv("DISTANCE")

omdbapi = OMDBApi(API_KEY)

recsys = ContentBaseRecSys(
    movies_dataset_filepath=MOVIES,
    distance_filepath=DISTANCE,
)

st.sidebar.markdown(
    "<h1 style='text-align: center; color: black;'>Movie Recommender Service</h1>",
    unsafe_allow_html=True
)

# image = Image.open('C:/Users/perev/DS/DS14-1-master/src/assets/13vlyj.jpg')
# st.image(image, use_column_width=True)

with st.sidebar:
    selected_movie = st.selectbox(
        "Type or select a movie you like :",
        recsys.get_title()
    )

    selected_genres = selectbox(
        "Type or select a genres you like :",
        recsys.get_genres(),
        no_selection_label=" "
    )

    selected_countries = selectbox(
        "Type or select a production countries :",
        recsys.get_countries(),
        no_selection_label=" "
    )

    selected_grade = st.checkbox("Show movies with high ratings (>= 7.5).")

if st.sidebar.button('Show Recommendation'):
    st.write("Recommended Movies:")
    recom_names, recom_grade, recom_countrie, recom_genres, recom_year = recsys.recommendation(selected_movie, selected_genres,
                                                                             selected_countries, selected_grade,
                                                                             top_k=TOP_K)
    recom_posters = omdbapi.get_posters(recom_names)
    if len(recom_names) == 0:
        st.write("Movies not found. Try changing filters.")
    else:
        if len(recom_names) < TOP_K:
            movies_col = st.columns(len(recom_names))
        else:
            movies_col = st.columns(TOP_K)
        for index, col in enumerate(movies_col):
            with col:
                st.subheader(recom_names[index])
                st.write(recom_year[index])
                st.write(f"Rating {recom_grade[index]}")
                st.write(*recom_genres[index], sep=', ')
                st.write(*recom_countrie[index], sep=', ')
                st.image(recom_posters[index])

