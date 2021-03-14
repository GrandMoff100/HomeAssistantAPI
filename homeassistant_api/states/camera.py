from .entity import Entity
    
class CameraEntity(Entity):
    group = "camera"
        
    def __repr__(self):
        return "<CameraEntityState %s>" % self.entity_id
