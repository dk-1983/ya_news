from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model: AbstractBaseUser):
    '''Создаем пользователя с именем Автор.'''
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author: AbstractBaseUser, client):
    '''Авторизуем пользователя с именем Автор и возвращаем клиент.'''
    client.force_login(author)
    return client


@pytest.fixture
def news():
    '''Создаем объект новости.'''
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )


@pytest.fixture
def create_news(news):
    '''Создаем несколько новостей для проверки сортировки и
    количества новостей на главной странице.'''
    all_news: list = []
    today: datetime = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news: News = News(
            title=f'Новость {index}',
            text='Очень информативный текст',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    '''Создаем комментарий.'''
    return Comment.objects.create(
        text='Текст комментария',
        news=news,
        author=author
    )


@pytest.fixture
def create_comments(author, news):
    '''Создаем несколько комментариев для проверки сортировки.'''
    for index in range(2):
        comment: Comment = Comment.objects.create(
            text=f'Текст комментария {index}',
            news=news,
            author=author
        )
        comment.created: datetime = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def news_pk_for_args(news):
    '''Возвращаем pk новости для использования в аргументах.'''
    return news.pk,


@pytest.fixture
def comment_pk_for_args(comment):
    '''Возвращаем pk комментария для использования в аргументах.'''
    return comment.pk,


@pytest.fixture
def form_data():
    '''Возвращаем данные для формы нового комментария.'''
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст комментария',
        'slug': 'new-slug',
    }


@pytest.fixture
def url_to_comments(comment, news_pk_for_args):
    '''Формируем URL адрес перехода к комментариям.'''
    return reverse('news:detail', args=news_pk_for_args) + '#comments'


@pytest.fixture
def delete_comment_url(comment, news_pk_for_args):
    '''Формируем URL адрес удаления комментария.'''
    return reverse('news:delete', args=news_pk_for_args)


@pytest.fixture
def edit_comment_url(news_pk_for_args):
    '''Формируем URL адрес редактирования комментария.'''
    return reverse('news:edit', args=news_pk_for_args)
