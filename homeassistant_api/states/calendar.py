from .entity import Entity
    
class CalendarEntity(Entity):
    group = "calendar"
        
    def __repr__(self):
        return "<CalendarEntityState %s>" % self.entity_id
