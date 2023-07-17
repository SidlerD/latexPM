from anytree import NodeMixin

from src.models.Version import Version

class Dependency:
    def __init__(self, id: str, name: str, version: str | dict | Version | None = None):
        self.id = id
        self.name = name
        self.version = version if isinstance(version, Version) else Version(version)

    def __eq__(self, other):
        if type(other) != Dependency:
            return False
        return self.id == other.id and self.version == other.version
    
    def __hash__(self):
        return hash((self.id, self.version))
    
    def __repr__(self):
        return f"{self.name}: {self.version}"
    
class DownloadedDependency(Dependency):
    def __init__(self, dep: Dependency, folder_path: str, download_url: str, files: list[str] = []) -> None:
        super().__init__(dep.id, dep.name, dep.version)
        self.path = folder_path
        self.url = download_url
        self.files = files

    def __repr__(self):
        return f"_{self.name}: {self.version}"
    def __str__(self) -> str:
        return f"{self.name}: {self.version}"
    
class DependencyNode(Dependency, NodeMixin):
    def __init__(self, dep: DownloadedDependency, parent=None, children=None, dependents: list[Dependency] = []):
        super(Dependency, self).__init__()
        self.id = dep.id
        self.dep = dep
        self.parent = parent
        if children:
            self.children = children
        self.dependents = dependents

    def __repr__(self):
        if self.dependents:
            return f" ({self.dep})"
        return str(self.dep)
    

def serialize_dependency(dep: Dependency | DownloadedDependency):
    if not isinstance(dep, Dependency):
        raise TypeError(f"Object of type '{dep.__class__.__name__}' is not JSON serializable")
    if type(dep) == DownloadedDependency:
        return {
            'id': dep.id,
            'name': dep.name, 
            'version': {'date': dep.version.date, 'number': dep.version.number},
            'path': dep.path,
            'url': dep.url,
            'files': dep.files
        }
    if type(dep) == Dependency:
        return {
            'id': dep.id,
            'name': dep.name, 
            'version': {'date': dep.version.date, 'number': dep.version.number},
        }