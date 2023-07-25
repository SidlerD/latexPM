from anytree import NodeMixin
import logging
from src.models.Version import Version

logger = logging.getLogger("default")

class Dependency:
    def __init__(self, id: str, name: str, version: str | dict | Version | None = None, alias: dict = None):
        self.id = id
        self.name = name
        self.version = version if isinstance(version, Version) else Version(version)
        self.alias = alias if alias else {}

    def __eq__(self, other):
        if type(other) != Dependency:
            return False
        return self.id == other.id and self.version == other.version
    
    def __hash__(self):
        return hash((self.id, self.version))
    
    def __repr__(self):
        if self.alias:
            return f"{self.name}({self.alias['id'] if self.alias['id'] else self.alias['name']}): {self.version}"

        return f"{self.name}: {self.version}"
    
class DownloadedDependency(Dependency):
    def __init__(self, dep: Dependency, folder_path: str, download_url: str, files: list[str] = None) -> None:
        super().__init__(dep.id, dep.name, dep.version, dep.alias)
        self.path = folder_path
        self.url = download_url
        self.files = files if files else [] # Can't do as default param because is mutable: https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments

    def __repr__(self):
        return f"_{self.name}: {self.version}"
    def __str__(self) -> str:
        return f"{self.name}: {self.version}"
    
class DependencyNode(NodeMixin):
    def __init__(self, dep: DownloadedDependency, parent=None, children=None, dependents: list[Dependency] = None):
        # super(Dependency, self).__init__()
        self.id = dep.id
        self.dep = dep
        self.parent = parent
        if children:
            self.children = children
        self.dependents = dependents if dependents else [] # Can't do as default param because is mutable: https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments

    def __repr__(self):
        if self.dependents:
            return f"({self.dep})"
        return str(self.dep)
    

def serialize_dependency(dep: Dependency | DownloadedDependency):
    if not isinstance(dep, Dependency):
        logger.error(f"Object of type '{dep.__class__.__name__}' is not JSON serializable: {str(dep)}. Returning str({dep.__class__.__name__})")
        try:
            return str(dep)
        except:
            raise TypeError(f"Object of type '{dep.__class__.__name__}' is not JSON serializable: {str(dep)}")
        
    if type(dep) == DownloadedDependency:
        return {
            'id': dep.id,
            'name': dep.name, 
            'version': {'date': dep.version.date, 'number': dep.version.number},
            'alias': dep.alias,
            'path': dep.path,
            'url': dep.url,
            'files': dep.files
        }
    if type(dep) == Dependency:
        return {
            'id': dep.id,
            'name': dep.name, 
            'version': {'date': dep.version.date, 'number': dep.version.number},
            'alias': dep.alias
        }