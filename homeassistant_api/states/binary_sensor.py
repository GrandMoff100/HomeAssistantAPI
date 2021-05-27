from .entity import Entity


class BinarySensorEntity(Entity):
    group = "binary_sensor"

    def __repr__(self):
        return "<BinarySensorEntityState %s>" % self.entity_id
