import json
from Dependency import Dependency

from helpers import download_file, extract_dependencies

with open("requirements.json", 'r') as file:
    requirements = json.load(file)

# Build dependency graph
stack: list[Dependency] = []
tmp_deps = requirements["dependencies"]
for key in tmp_deps:
    stack.append(Dependency(key, tmp_deps[key]))

dependencies: list[Dependency] = []
failed_deps: list[dict[Dependency: str]] = []

while len(stack) != 0:
    dep = stack.pop()
    
    try:
        folder_path = download_file(dep)
        dep.path = folder_path # Points to the folder of all files of the package
        dependencies.append(dep)

        satisfied_deps, unsatisfied_deps = extract_dependencies(dep)

        #TODO: Check if this makes sense
        stack.extend([dep for dep in unsatisfied_deps if dep not in dependencies])
        # dependencies.extend(satisfied_deps)
    except (ValueError, NotImplementedError) as e :
        print(e)
        failed_deps.append({dep: str(e)})

for fail in failed_deps:
    print(fail)
