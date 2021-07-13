class JsonModel(dict):
    def __init__(self, json: dict = None, **kwargs):
        if json:
            self.update(json)
        if kwargs:
            self.update(kwargs)

    def __getattr__(self, name):
        if '__' not in str(name):
            if name in self:
                if isinstance(self[name], dict):
                    return JsonModel(self[name])
                return self[name]
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if '__' not in str(name):
            if isinstance(value, dict):
                self[name] = JsonModel(value)
            self[name] = value
        super().__setattr__(name, value)
