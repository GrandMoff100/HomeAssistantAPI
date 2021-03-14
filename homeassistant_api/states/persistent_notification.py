from .entity import Entity
    
class PersistentNotificationEntity(Entity):
    group = "persistent_notification"
        
    def __repr__(self):
        return "<PersistentNotificationEntityState %s>" % self.entity_id
