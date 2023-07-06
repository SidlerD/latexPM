from anytree import NodeMixin

from src.models.Version import Version

class Dependency:
    def __init__(self, id: str, name: str, version: str | dict | Version | None = None):
        self.id = id
        self.name = name
        self.version = version if isinstance(version, Version) else Version(version)

    def __eq__(self, other):
        return self.id == other.id and self.version == other.version
    
    def __hash__(self):
        return hash((self.id, self.version))
    
    def __repr__(self):
        return f"{self.name}: {self.version}"
    
class DownloadedDependency(Dependency):
    def __init__(self, dep: Dependency, folder_path: str, download_url: str) -> None:
        super().__init__(dep.id, dep.name, dep.version)
        self.path = folder_path
        self.url = download_url

class DependencyNode(Dependency, NodeMixin):
    def __init__(self, dep: Dependency, parent=None, children=None, dependents: list[Dependency] = []):
        super(Dependency, self).__init__()
        self.id = dep.id
        self.dep = dep
        self.parent = parent
        if children:
            self.children = children
        self.dependents = dependents

    def __repr__(self):
        if self.dependents:
            return f" ( {self.dep} ): {self.dependents}"
        return str(self.dep)
    

def serialize_dependency(dep: Dependency | DownloadedDependency):
    if not isinstance(dep, Dependency):
        raise TypeError(f"Object of type '{dep.__class__.__name__}' is not JSON serializable")
    if type(dep) is DownloadedDependency:
        return {
            'id': dep.id,
            'name': dep.name, 
            'version': {'date': dep.version.date, 'number': dep.version.number},
            'path': dep.path,
            'url': dep.url
        }
    if type(dep) is Dependency:
        return {
            'id': dep.id,
            'name': dep.name, 
            'version': {'date': dep.version.date, 'number': dep.version.number},
        }