import logging
import os
import shutil
import docker

docker_image = 'camilstaps/texlive:minimal'

tex_file_format = '\n'.join([
    r"\documentclass{article}",
    r"\usepackage{%s}",
    r"\begin{document}",
    r"text",
    r"\end{document}",
])

client = docker.from_env()

def validate_dependencies(pkg_to_test: str, pkg_deps_lpm: list[str], pkg_deps_tlmgr: list[str]) -> tuple[bool, bool]:
    tmp_dir = 'tmp_host'
    os.mkdir(tmp_dir)
    try:
        file_content = tex_file_format % pkg_to_test
        with open(os.path.join(os.path.abspath(tmp_dir), 'test.tex'), 'w') as f:
            f.write(file_content)
        
        vol_path = f"{os.path.abspath(tmp_dir)}:/usr/tmp/lpm2"

        args =['echo hello'] +  ['tlmgr install ' + pkg for pkg in pkg_deps_tlmgr]

        args.append('pdflatex test.tex')


        container = client.containers.create(
            image=docker_image, 
            # detach=True,
            volumes=[vol_path], # Make files in project dir available to container, put output there too
            # environment={'TEXINPUTS': '.:/root/lpm/packages//'}, # Set TEXINPUTS to include volume path
            working_dir='/usr/tmp/lpm2'
            # user='root'
            # remove=True # Delete container when build is over
        )

        container.start()
        exit_code, logs = container.exec_run(
            cmd=args, # Execute passed arguments in cmd
        )

        print(exit_code, logs)


    except Exception as e:
        logging.exception(e)
    finally: 
        shutil.rmtree(tmp_dir)
        print('over')

if __name__ == '__main__':
    validate_dependencies('minted', 
        pkg_deps_lpm=[], 
        pkg_deps_tlmgr=[
            "catchfile",
            "etoolbox",
            "float",
            "framed",
            "fvextra",
            "graphics",
            "ifplatform",
            "kvoptions",
            "lineno",
            "newfloat",
            "pdftexcmds",
            "tools",
            "xcolor",
            "xstring"
        ]
    )