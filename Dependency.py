class Dependency:
    def __init__(self, name, version = "", path = ""):
        self.name = name
        self.version = version
        self.path = path

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version
    
    def __hash__(self):
        return hash((self.name, self.version))
    
    def __repr__(self):
        return f"{self.name}: {self.version}"