from .entity import Entity
    
class ZoneEntity(Entity):
    group = "zone"
        
    def __repr__(self):
        return "<ZoneEntityState %s>" % self.entity_id
