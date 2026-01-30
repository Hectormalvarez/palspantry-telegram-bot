import pytest
from unittest.mock import Mock
from handlers.utils import schedule_deletion


def test_schedule_deletion():
    # 1. Mocks `context` and `context.job_queue`.
    context = Mock()
    context.job_queue = Mock()

    # 2. Calls `schedule_deletion(context, chat_id=123, message_id=456, delay=3.0)`
    schedule_deletion(context, chat_id=123, message_id=456, delay=3.0)

    # 3. Asserts that `context.job_queue.run_once` was called exactly once.
    context.job_queue.run_once.assert_called_once()

    # 4. Asserts that the first argument passed to `run_once` is a callable (the callback).
    call_args = context.job_queue.run_once.call_args
    assert callable(call_args[0][0])

    # 5. Asserts that the second argument is `3.0`.
    assert call_args[0][1] == 3.0

    # 6. Asserts that the `data` keyword argument is `(123, 456)`.
    assert call_args[1]["data"] == (123, 456)
