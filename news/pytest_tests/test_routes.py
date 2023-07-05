from http import HTTPStatus

import pytest
from django.http import HttpResponse
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, news_object',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args'))
    ),
)
def test_pages_availability_for_anonymous_user(client, page, news_object):
    '''Проверяем доступность страниц для неавторизованных пользователей.'''
    url: str = reverse(page, args=news_object)
    response: HttpResponse = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'page',
    ('news:delete', 'news:edit'),
)
def test_availability_for_author_and_authenticated(
    parametrized_client, page,
    expected_status, comment_pk_for_args
):
    '''
    Проверяем, что редактирование и удаление комментария доступны только
    автору.
    '''
    url: str = reverse(page, args=comment_pk_for_args)
    response: HttpResponse = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'page, comment_object',
    (
        ('news:delete', pytest.lazy_fixture('comment_pk_for_args')),
        ('news:edit', pytest.lazy_fixture('comment_pk_for_args')),
    ),
)
def test_redirects(client, page, comment_object):
    '''
    Проверяем, что неавторизованный пользователь не может редактировать
    и удалять комментарии и перенаправляется на страницу авторизации.
    '''
    login_url: str = reverse('users:login')
    url: str = reverse(page, args=comment_object)
    expected_url: str = f'{login_url}?next={url}'
    response: HttpResponse = client.get(url)
    assertRedirects(response, expected_url)
