import json
import os
import subprocess

file_name = 'tlmgr_deps_of_files_output.json'


def get_pkgs_with_deps():
    if os.path.exists(file_name):
        print("Taking data from " + file_name)
        with open(file_name, 'r') as f:
            data = json.load(f)
        
        return data
    
    # Call tlmgr to get dependency info of all packages, capture output
    fields = ["name", "cat-version", "cat-date", "depends"]
    command = f'tlmgr --data "{",".join(fields)}" info'

    try:
        output = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Error running tlmgr:", e)
        return None
    
    output_lines = output.split('\n')

    # Make dict with pkg:dependencies[] pairs
    res = []
    for output_line in output_lines:
        if output_line.endswith(','): # Has no depends attr
            continue
        try:
            pkg = {}
            # Write fields from output to dict
            for field in fields: 
                pkg[field] = output_line.split(',')[fields.index(field)]
            
            # Split dependencies into a list
            pkg['depends'] = pkg['depends'].split(':')

            # Don't add if pkg is a collection
            if 'name' in pkg and pkg['name'].startswith('collection'):
                continue
            
            res.append(pkg)
        except Exception as e:
            print(f"{str(e)}, output_line = {output_line}")
    return res

if __name__ == '__main__':
    res = get_pkgs_with_deps()

    if input('Should I write result to json file?').lower() == 'y':
        with open(file_name, 'w') as f:
            json.dump(res, f, indent=2)
    else:
        print(json.dumps(res, indent=2))

