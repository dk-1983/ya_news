from http import HTTPStatus

import pytest
from django.http import HttpResponse
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrize_client, exp_comments_count',
    (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('admin_client'), 1)
    ),
)
def test_send_comment(
        parametrize_client, exp_comments_count,
        news_pk_for_args, form_data
):
    '''
    Проверяем, что отправка комментария доступна авторизованному
    пользователю и недоступна неавторизованному пользователю.
    '''
    target_url: str = reverse('news:detail', args=news_pk_for_args)
    parametrize_client.post(target_url, data=form_data)
    comments_count: int = Comment.objects.count()
    assert comments_count == exp_comments_count


def test_check_stop_words(admin_client, news_pk_for_args):
    '''
    Проверяем, что при использовании стоп-слов в комментариях возбуждается
    ошибка отправки формы.
    '''
    bad_words_data: dict = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    }
    url: str = reverse('news:detail', args=news_pk_for_args)
    response: HttpResponse = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_availability: bool = Comment.objects.exists()
    assert not comments_availability


def test_auth_user_can_delete_your_comments(
    author_client, url_to_comments, delete_comment_url
):
    '''
    Проверяем, что автор комментария может удалить свой комментарий.
    '''
    response: HttpResponse = author_client.delete(delete_comment_url)
    assertRedirects(response, url_to_comments)
    comments_availability: bool = Comment.objects.exists()
    assert not comments_availability


def test_user_cant_delete_comment_of_another_user(
    admin_client, delete_comment_url
):
    '''
    Проверяем, что авторизованный пользователь не может удалить чужой
    комментарий.
    '''
    response: HttpResponse = admin_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count: int = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, comment, form_data, edit_comment_url, url_to_comments
):
    '''
    Проверяем, что автор комментария может редактировать свой комментарий.
    '''
    response: HttpResponse = author_client.post(
        edit_comment_url,
        data=form_data
    )
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    admin_client, edit_comment_url, form_data, comment
):
    '''
    Проверяем, что авторизованный пользователь не может редактировать чужой
    комментарий.
    '''
    response: HttpResponse = admin_client.post(
        edit_comment_url,
        data=form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    old_comment_text: str = comment.text
    comment.refresh_from_db()
    assert comment.text == old_comment_text
