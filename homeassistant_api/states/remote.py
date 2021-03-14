from .entity import Entity
    
class RemoteEntity(Entity):
    group = "remote"
        
    def __repr__(self):
        return "<RemoteEntityState %s>" % self.entity_id
