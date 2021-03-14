from .entity import Entity
    
class AutomationEntity(Entity):
    group = "automation"
        
    def __repr__(self):
        return "<AutomationEntityState %s>" % self.entity_id
