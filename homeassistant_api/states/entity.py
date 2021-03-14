from ..models.base import JsonModel


class BaseEntity(JsonModel):
    def __init__(self, *args, **kwargs):
        self.attributes = None
        self.context = None
        self.entity_id = None
        self.last_changed = None
        self.last_updated = None
        self.state = None
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<EntityState {self.entity_id}>'


class Entity(BaseEntity):
    group = None

    def __init__(self, json):
        super().__init__(json)
        group, name = self.entity_id.split('.')
        self.name = ' '.join([x.capitalize() for x in name.split('_')])
        if self.group != group and type(self) != Entity:
            raise ValueError('Cannot assign a "{}" entity to "{}"'.format(group, type(self).__name__))
        elif type(self) == Entity:
            self.group = group

    def __str__(self):
        return self.name
