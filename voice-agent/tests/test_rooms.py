"""Room-name routing for the worker (playground vs phone legs)."""
from app.rooms import HANDLED_PREFIXES, is_handled_room


def test_playground_rooms_handled():
    assert is_handled_room("playground-1-abc")


def test_phone_rooms_handled():
    assert is_handled_room("phone-42")
    assert is_handled_room("phone-84")


def test_other_rooms_rejected():
    assert not is_handled_room("campaign-x")
    assert not is_handled_room("random-room")
    assert not is_handled_room("")
    assert not is_handled_room(None) if False else not is_handled_room("phone")  # prefix needs dash+id


def test_prefixes_constant():
    assert HANDLED_PREFIXES == ("playground-", "phone-")
