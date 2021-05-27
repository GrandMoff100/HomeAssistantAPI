from .entity import Entity


class SensorEntity(Entity):
    group = "sensor"

    def __repr__(self):
        return "<SensorEntityState %s>" % self.entity_id
