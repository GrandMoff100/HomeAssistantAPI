from .entity import Entity
    
class SceneEntity(Entity):
    group = "scene"
        
    def __repr__(self):
        return "<SceneEntityState %s>" % self.entity_id
