
import factory.fuzzy
from fast_zero.models import Todo, TodoState
import pytest


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1 

def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft'
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
    }

@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    sessiontest, client, user, token
):
    expected_todos = 5
    sessiontest.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await sessiontest.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos

@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    sessiontest, user, client, token
):
    expected_todos = 2
    sessiontest.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await sessiontest.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos

@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    sessiontest, user, client, token
):
    expected_todos = 5
    sessiontest.add_all(
        TodoFactory.create_batch(5, user_id=user.id,
        title='Test todo 1')
    )
    await sessiontest.commit()

    response = client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos

@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    sessiontest, user, client, token
):
    expected_todos = 5
    sessiontest.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description='description')
    )
    await sessiontest.commit()

    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos

@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    sessiontest, user, client, token
):
    expected_todos = 5
    sessiontest.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    )
    await sessiontest.commit()

    response = client.get(
        f'/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos

@pytest.mark.asyncio
async def test_list_todos_no_filter_return_all(
    sessiontest, user, client, token
):
    expected_todos = 10
    sessiontest.add_all(
        TodoFactory.create_batch(10, user_id=user.id, state=TodoState.draft)
    )
    await sessiontest.commit()

    response = client.get(
        f'/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos

@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    sessiontest, user, client, token
):
    expected_todos = 5
    sessiontest.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    sessiontest.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )

    await sessiontest.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos