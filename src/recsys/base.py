import ast
from typing import List, Set, Tuple

import streamlit as st
import pandas as pd
from .utils import parse


@st.cache_data
def _load_base(path: str, index_col: str = 'id') -> pd.DataFrame:
    """Загрузка файла CSV в pandas.DataFrame"""
    return pd.read_csv(path, index_col=index_col)


class ContentBaseRecSys:

    def __init__(self, movies_dataset_filepath: str, distance_filepath: str) -> None:
        self.distance = _load_base(distance_filepath, index_col='movie_id')
        self.distance.index = self.distance.index.astype(int)
        self.distance.columns = self.distance.columns.astype(int)
        self._init_movies(movies_dataset_filepath)

    def _init_movies(self, movies_dataset_filepath) -> None:
        self.movies = _load_base(movies_dataset_filepath, index_col='id')
        self.movies.index = self.movies.index.astype(int)
        self.movies['genres'] = self.movies['genres'].apply(parse)
        self.movies['production_countries'] = self.movies['production_countries'].apply(parse)
        self.movies['years'] = pd.DatetimeIndex(self.movies.release_date).year.fillna(0).astype(int)
        self.movies['title_year'] = self.movies['title'] + ' (' + self.movies['years'].astype(str) + ')'

    def get_title(self) -> List[str]:
        return self.movies['title'].values

    def get_genres(self) -> Set[str]:
        genres = [item for sublist in self.movies['genres'].values.tolist() for item in sublist]
        return set(genres)

    def get_countries(self) -> Set[str]:
        countries = [item for sublist in self.movies['production_countries'].values.tolist() for item in sublist]
        return set(countries)

    def filter_movies(self, genre: str = None, countrie: str = None, grade: str = None) -> pd.DataFrame:
        df_movies_filter = self.movies
        if genre:
            df_movies_filter = df_movies_filter.loc[df_movies_filter.genres.apply(lambda x: genre in x)]
        if grade:
            df_movies_filter = df_movies_filter[df_movies_filter['simple_score'] >= 7.5]
        if countrie:
            df_movies_filter = df_movies_filter.loc[
                df_movies_filter.production_countries.apply(lambda x: countrie in x)]

        return df_movies_filter

    def recommendation(self, title: str, genre: str = None, countrie: str = None, grade: str = False, top_k: int = 5) -> \
    Tuple[List[str], List[str], List[str], List[str], List[str]]:
        # Получаем индекс выбранного фильма
        movie_index = self.movies[self.movies['title'] == title].index[0]
        # Отсортированное косинусное расстояние до выбранного фильма (топ к)
        df_distance_movie = self.distance[movie_index].sort_values(ascending=False)
        # Список индексов фильмов
        movie_index_list = df_distance_movie.index.values.tolist()

        df_movies_filter = self.filter_movies(genre, countrie, grade)

        list_movie_filter = df_movies_filter['movie_id'].tolist()

        movie_list = [self.movies.at[i, 'title'] for i in movie_index_list[1:] if (i in list_movie_filter)][0:top_k]
        grades_list = [self.movies.at[i, 'simple_score'] for i in movie_index_list[1:] if (i in list_movie_filter)][
                      0:top_k]
        genres_list = [self.movies.at[i, 'genres'] for i in movie_index_list[1:] if (i in list_movie_filter)][
                      0:top_k]
        countries_list = [self.movies.at[i, 'production_countries'] for i in movie_index_list[1:] if
                          (i in list_movie_filter)][0:top_k]
        year_list = [self.movies.at[i, 'years'] for i in movie_index_list[1:] if (i in list_movie_filter)][0:top_k]

        return movie_list, grades_list, countries_list, genres_list, year_list
