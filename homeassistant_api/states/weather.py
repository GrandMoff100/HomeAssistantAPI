from .entity import Entity
    
class WeatherEntity(Entity):
    group = "weather"
        
    def __repr__(self):
        return "<WeatherEntityState %s>" % self.entity_id
