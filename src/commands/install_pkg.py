import json
import logging
import os
from src.models.Dependency import Dependency, DependencyNode
from anytree import Node, RenderTree, findall, AsciiStyle

from helpers import download_file, extract_dependencies

def _handle_dep(dep: Dependency, parent: DependencyNode | Node, root: Node):
    # FIXME: Check Assumption: If dep.version is None and we have some version of it installed, then that satisfies dep
    filter = lambda node: (
        type(node) == DependencyNode 
        and (
            node.dep == dep or # Is  the same dependency
            (node.dep.id == dep.id and dep.version == None) # Need version None => Any version is fine 
        )
    )
    prev_occurences = findall(root, filter_= filter)
    if prev_occurences:
        # TODO: If the current dep needs version None, and package is already installed in some version, it shouldn't be installed again
        # Dependency already satisfied, don't go further down
        # if(len(prev_occurences) != 1):
        #     raise RuntimeWarning(f"There are {len(prev_occurences)} versions of {dep.id} installed!!")
        prev_version = prev_occurences[0].dep.version
        node = DependencyNode(dep, parent=parent, already_satisfied=str(prev_version))
        return
    
    try:
        folder_path = download_file(dep)
        dep.path = folder_path # Points to the folder of all files of the package
        node = DependencyNode(dep, parent=parent)

        _, unsatisfied_deps = extract_dependencies(dep)
        for child_dep in unsatisfied_deps:
            try:
                _handle_dep(child_dep, node, root)
            except (ValueError, NotImplementedError) as e :
                print(e)
    
    except (ValueError, NotImplementedError) as e :
        print(f"Problem while installing {dep.id} {dep.version if dep.version else 'None'}: {str(e)}")


def install_pkg(pkg_id: str):
    """Installs one specific package and all its dependencies\n
    Returns json to add to requirements-file, describing installed package and dependencies"""
    #TODO: Figure out how to pass existing dependency tree here, otherwise packages might be installed twice
    rootNode = get_dependency_tree()
    
    try:
        dep = Dependency(pkg_id, API.CTAN.get_name_from_id(pkg_id), version="")
        _handle_dep(dep, rootNode) 
        #TODO: Return json to add to requirements-file, describing installed package and dependencies
    except Exception as e:
        logging.exception(e)