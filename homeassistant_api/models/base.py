class JsonModel(dict):
    def __init__(self, json=None, **kwargs):
        if json:
            for k, v in json.items():
                self[k] = v
        else:
            for k, v in kwargs.items():
                self[k] = v
    
    def __getattribute__(self, name):
        if '__' not in str(name):
            if name in self:
                if isinstance(self[name], dict):
                    return JsonModel(self[name])
                return self[name]
        return super().__getattribute__(name)


class DictAttrs:
    def __init__(self, json: dict):
        self.__attrs__ = json
        for k, v in json.items():
            if not k.startswith('_'):
                setattr(self, k, v)

    def __repr__(self):
        return f'<DictAttrs {list(self)}>'

    def __iter__(self):
        return iter(self.__attrs__)
    
    def __getitem__(self, item):
        return self.__attrs__.get(item, None)
    
    def __setitem__(self, item, value):
        self.__attrs__[item] = value
    
