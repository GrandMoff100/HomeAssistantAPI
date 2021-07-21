from ...models import State


class AsyncState(State):
    """A class representing a state of an entity."""

    def __repr__(self):
        return f'<AsyncEntityState "{self.state}">'
