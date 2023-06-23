from anytree import NodeMixin

class Dependency:
    def __init__(self, id, name, version = "", path = ""):
        self.id = id
        self.name = name
        self.version = version
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