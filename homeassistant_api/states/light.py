from .entity import Entity


class LightEntity(Entity):
    group = "light"

    def __repr__(self):
        return "<LightEntityState %s>" % self.entity_id
