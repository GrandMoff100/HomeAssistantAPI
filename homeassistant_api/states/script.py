from .entity import Entity


class ScriptEntity(Entity):
    group = "script"

    def __repr__(self):
        return "<ScriptEntityState %s>" % self.entity_id
