from .entity import Entity
    
class PersonEntity(Entity):
    group = "person"
        
    def __repr__(self):
        return "<PersonEntityState %s>" % self.entity_id
