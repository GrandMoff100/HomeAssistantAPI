from .entity import Entity


class SunEntity(Entity):
    group = "sun"

    def __repr__(self):
        return "<SunEntityState %s>" % self.entity_id
