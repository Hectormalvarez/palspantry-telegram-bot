import pytest
from persistence.in_memory_persistence import InMemoryPersistence


@pytest.mark.asyncio
async def test_in_memory_persistence_initial_state():
    """Test the initial state of InMemoryPersistence."""
    persistence = InMemoryPersistence()
    assert (
        await persistence.get_bot_owner() is None
    ), "Initially, bot owner should be None"
    assert (
        not await persistence.is_owner_set()
    ), "Initially, is_owner_set should be False"


@pytest.mark.asyncio
async def test_in_memory_persistence_set_owner_first_time():
    """Test setting the bot owner for the first time."""
    persistence = InMemoryPersistence()
    user_id = 12345

    # Set owner for the first time
    success = await persistence.set_bot_owner(user_id)
    assert success is True, "set_bot_owner should return True on first successful set"
    assert (
        await persistence.get_bot_owner() == user_id
    ), "get_bot_owner should return the new owner_id"
    assert (
        await persistence.is_owner_set() is True
    ), "is_owner_set should be True after setting an owner"


@pytest.mark.asyncio
async def test_in_memory_persistence_set_owner_when_already_set():
    """Test attempting to set the bot owner when one is already set."""
    persistence = InMemoryPersistence()
    initial_owner_id = 12345
    second_user_id = 67890

    # Set initial owner
    await persistence.set_bot_owner(initial_owner_id)
    assert await persistence.get_bot_owner() == initial_owner_id  # Verify initial set

    # Attempt to set owner again with a different ID
    success = await persistence.set_bot_owner(second_user_id)
    assert success is False, "set_bot_owner should return False if owner is already set"
    assert (
        await persistence.get_bot_owner() == initial_owner_id
    ), "Bot owner should remain the initial owner"
    assert await persistence.is_owner_set() is True, "is_owner_set should still be True"


@pytest.mark.asyncio
async def test_in_memory_persistence_set_owner_with_same_id_when_already_set():
    """Test attempting to set the bot owner with the same ID when one is already set."""
    persistence = InMemoryPersistence()
    owner_id = 12345

    # Set initial owner
    await persistence.set_bot_owner(owner_id)
    assert await persistence.get_bot_owner() == owner_id  # Verify initial set

    # Attempt to set owner again with the same ID
    success = await persistence.set_bot_owner(owner_id)
    assert (
        success is False
    ), "set_bot_owner should return False even if setting with the same ID again"
    assert (
        await persistence.get_bot_owner() == owner_id
    ), "Bot owner should remain the initial owner"


@pytest.mark.asyncio
async def test_in_memory_persistence_is_owner_set_transitions():
    """Test the is_owner_set method transitions correctly."""
    persistence = InMemoryPersistence()
    assert not await persistence.is_owner_set(), "is_owner_set is False initially"

    await persistence.set_bot_owner(123)
    assert await persistence.is_owner_set(), "is_owner_set is True after setting owner"


@pytest.mark.asyncio
async def test_in_memory_persistence_get_bot_owner_transitions():
    """Test the get_bot_owner method transitions correctly."""
    persistence = InMemoryPersistence()
    assert await persistence.get_bot_owner() is None, "get_bot_owner is None initially"

    owner_id = 987
    await persistence.set_bot_owner(owner_id)
    assert (
        await persistence.get_bot_owner() == owner_id
    ), "get_bot_owner returns correct ID after setting owner"
