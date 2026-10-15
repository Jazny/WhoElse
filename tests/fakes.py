"""Test helpers shared by several test files."""

from types import SimpleNamespace


class FakeClient:
    """Stands in for anthropic.Anthropic: mimics client.messages.create and
    records every call, so tests never touch the network."""

    def __init__(self, reply="Rats, stranger.", error=None):
        self.calls = []
        self.reply = reply
        self.error = error
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        content = [SimpleNamespace(type="text", text=self.reply)] if self.reply else []
        return SimpleNamespace(content=content)
