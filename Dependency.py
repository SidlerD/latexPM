from anytree import NodeMixin

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
    

class DependencyNode(Dependency, NodeMixin):
    def __init__(self, name, dep: Dependency, parent=None, children=None, already_satisfied=""):
        super(Dependency, self).__init__()
        self.name = name
        self.dep = dep
        self.parent = parent
        if children:
            self.children = children
        self.already_satisfied = already_satisfied

    def __repr__(self):
        if self.already_satisfied:
            return f" ( {self.dep} ): {self.already_satisfied}"
        return str(self.dep)