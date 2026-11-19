import pytest
from pydantic import ValidationError
from app.schemas.chat import SendMessageRequest

def test_valid_message():
    data = SendMessageRequest(prompt="Hello", tone="casual")
    assert data.prompt == "Hello"
    assert data.tone == "casual"

def test_invalid_tone_rejected():
    with pytest.raises(ValidationError):
        SendMessageRequest(prompt="Hello", tone="angry")

def test_empty_prompt_rejected():
    with pytest.raises(ValidationError):
        SendMessageRequest(prompt="", tone="professional")
