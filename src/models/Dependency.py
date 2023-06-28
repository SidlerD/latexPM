from anytree import NodeMixin

from src.models.Version import Version

class Dependency:
    def __init__(self, id: str, name: str, version: str | dict | None, path = ""):
        self.id = id
        self.name = name
        self.version: Version = Version(version)
        self.path = path

    def __eq__(self, other):
        return self.id == other.id and self.version == other.version
    
    def __hash__(self):
        return hash((self.id, self.version))
    
    def __repr__(self):
        return f"{self.name}: {self.version}"
    

class DependencyNode(Dependency, NodeMixin):
    def __init__(self, dep: Dependency, parent=None, children=None, already_satisfied=""):
        super(Dependency, self).__init__()
        self.id = dep.id
        self.dep = dep
        self.parent = parent
        if children:
            self.children = children
        self.already_satisfied = already_satisfied

    def __repr__(self):
        if self.already_satisfied:
            return f" ( {self.dep} ): {self.already_satisfied}"
        return str(self.dep)
    

def serialize_dependency(dep: Dependency):
    if not isinstance(dep, Dependency):
        raise TypeError(f"Object of type '{dep.__class__.__name__}' is not JSON serializable")
    return {'id': dep.id, 'name': dep.name, 'version': {'date': dep.version.date, 'number': dep.version.number}, 'path': dep.path}