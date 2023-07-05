from datetime import datetime

import pytest
from django.http import HttpResponse
from django.urls import reverse

from news.models import Comment, News

HOME_URL: str = reverse('news:home')


@pytest.mark.django_db
def test_count_news_on_main_page(client, create_news):
    '''Проверяем количество новостей на главной странице.'''
    expected_count: int = 10
    response: HttpResponse = client.get(HOME_URL)
    object_list: list[News] = response.context['object_list']
    news_count: int = len(object_list)
    assert news_count == expected_count


@pytest.mark.django_db
def test_news_sorted(client, create_news):
    '''Проверяем сортировку новостей на главной странице.'''
    response: HttpResponse = client.get(HOME_URL)
    object_list: list[News] = response.context['object_list']
    all_dates: list[datetime] = [news.date for news in object_list]
    sorted_dates: list[datetime] = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
def test_comments_sorted(client, news_pk_for_args, create_comments):
    '''Проверяем сортировку комментариев на странице новости.'''
    response: HttpResponse = client.get(reverse(
        'news:detail',
        args=news_pk_for_args)
    )
    news: News = response.context['news']
    all_comments: list[Comment] = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrize_client, form_status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True)
    ),
)
def test_form_for_users(news_pk_for_args, parametrize_client, form_status):
    '''Проверяем доступна ли форма отправки комментария на странице новости.'''
    url: str = reverse('news:detail', args=news_pk_for_args)
    response: HttpResponse = parametrize_client.get(url)
    assert ('form' in response.context) == form_status
