from datetime import date, datetime
from anytree import NodeMixin
import logging
from src.models.Version import Version

logger = logging.getLogger("default")

class Dependency:
    """A class for modeling a package or dependency

    Attributes:
            id (str): Id of the package
            name (str): Name of the package
            version (Version): Version of the package
            alias (dict): Dict with "name" and "id" of alias that package is available on CTAN under
    """
    def __init__(self, id: str, name: str, version: str | dict | Version | None = None, alias: dict = None):
        """A class for modeling a package or dependency

        Args:
            id (str): Id of the package
            name (str): Name of the package
            version (str | dict | Version | None, optional): Version of the package
            alias (dict, optional):  Dict with "name" and "id" of alias that package is available on CTAN under
        """
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
        repr = [self.name]
        if self.alias:
            repr.append(f"({self.alias['id'] if self.alias['id'] else self.alias['name']})")
        if self.version != None:
            repr.append(': ' + str(self.version))
        return ''.join(repr)


class DownloadedDependency(Dependency):
    """Class for modeling a downloaded package or dependency. Inherits from Dependency

    Attributes:
        id (str): Id of the package
        name (str): Name of the package
        version (str | dict | Version | None, optional): Version of the package
        alias (dict, optional):  Dict with "name" and "id" of alias that package is available on CTAN under
        path (str): Path to folder package is installed in
        url (str): Url used for downloading the package
        ctan_path (str): Path of package on CTAN
    """
    def __init__(self, dep: Dependency, folder_path: str, download_url: str, ctan_path: str) -> None:
        """Class for modeling a downloaded package or dependency. Inherits from Dependency

        Args:
            dep (Dependency): Package that this Object is based on
            folder_path (str): Path to folder package is installed in
            download_url (str): Url used for downloading the package
            ctan_path (str): Path of package on CTAN
        """
        super().__init__(dep.id, dep.name, dep.version, dep.alias)
        self.path = folder_path
        self.url = download_url
        self.ctan_path = ctan_path

    def __str__(self) -> str:
        return f"{self.name}{self.version}"

    def __repr__(self) -> str:
        return f"_{self.name}{self.version}"

class DependencyNode(NodeMixin):
    """ Class for a node representing a package in the dependency tree
    
    Attributes:
        id (str): Id of node, which is equal to dep.id
        dep (DownloadedDependency): Package that node represents
        parent (DependencyNode|Node, optional): Parent of package in tree
        children (DependencyNode|Node, optional): Children of package in tree (i.e. its dependencies)
        dependents (list[str], optional): Other packages that depend on this package
    """
    def __init__(self, dep: DownloadedDependency, parent, children=None, dependents: list[str] = None):
        """ Adds a node to the tree representign the passed package

        Args:
            dep (DownloadedDependency):Package to include in tree
            parent (DependencyNode|Node, optional): Parent of package in tree
            children (DependencyNode|Node, optional): Children of package in tree (i.e. its dependencies)
            dependents (list[str], optional): Other packages that depend on this package
        """
        # super(Dependency, self).__init__()
        self.id = dep.id
        self.dep = dep
        self.parent = parent
        if children:
            self.children = children
        self.dependents = dependents if dependents else []  # Can't do as default param because is mutable: https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments

    def __repr__(self):
        if self.dependents:
            return f"{self.dep}"
        return str(self.dep)

    @property
    def ppath(self):
        """Pretty path, use for printing path to node\n
        Example: acro:  --> translations:  --> (pdftexcmds: )"""
        return ' > '.join([str(node) if hasattr(node, 'id') else node.name for node in self.path][1:])
    
    def add_dependent(self, node_id: str):
        "Adds node_id to self.dependents if not already in self.dependents"
        if node_id not in self.dependents:
            self.dependents.append(node_id)


def serialize_dependency(elem: any):
    if isinstance(elem, date):
        return str(elem)
    if isinstance(elem, datetime):
        return str(elem.date())
    if type(elem) == DownloadedDependency:
        return {
            'id': elem.id,
            'name': elem.name,
            'version': {'date': elem.version.date, 'number': elem.version.number},
            'alias': elem.alias,
            'path': elem.path,
            'url': elem.url,
            'ctan_path': elem.ctan_path
        }
    if type(elem) == Dependency:
        return {
            'id': elem.id,
            'name': elem.name,
            'version': {'date': elem.version.date, 'number': elem.version.number},
            'alias': elem.alias
        }
    logger.warning(f"Object of type '{elem.__class__.__name__}' is not JSON serializable: {str(elem)}. Attempting to return str({elem.__class__.__name__})")
    try:
        return str(elem)
    except Exception:
        raise TypeError(f"Object of type '{elem.__class__.__name__}' is not JSON serializable")
