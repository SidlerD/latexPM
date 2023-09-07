import json
import os
import shutil
import timeit
import tempfile


old_cwd = os.getcwd()
# # tmpdir = tempfile.mkdtemp()
# # os.rmdir(tmpdir)


# def setup() -> str:
#     from src.core import LockFile
#     LockFile._root = None
#     tmpdir = tempfile.mkdtemp()
#     os.chdir(tmpdir)
#     # shutil.rmtree(tmpdir)
#     # os.mkdir(tmpdir)
#     # lpm_inst = lpm()
#     # lpm_inst.init(docker_image="registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-20-small")

#     return tmpdir


# def tearDown(dir: str):
#     os.chdir(old_cwd)
#     shutil.rmtree(dir)


# def time_function(func, n: int, *args):
#     for i in range(n):
#         dir = setup()
#         start = timeit.default_timer()
#         func(*args)
#         end = timeit.default_timer()

#         print(f"{func.__name__}({', '.join([str(a) for a in args])}) took {end - start} seconds to execute")

#         tearDown(dir)


# if __name__ == '__main__':
#     from src.commands.install_pkg import install_pkg
#     time_function(install_pkg, 5, 'amsmath')

#     # timeit.repeat(
#     #     stmt='import os;import shutil;from src.core.lpm import lpm;from test.timing.TimeCommandExecution import tmpdir, old_cwd;os.mkdir(tmpdir);os.chdir(tmpdir);lpm_inst = lpm();lpm_inst.install_pkg("amsmath");os.chdir(old_cwd); shutil.rmtree(tmpdir)', number=1, repeat=2
#     #     )
#     # timeit.timeit(stmt='from test.timing.TimeCommandExecution import x;print(x);x.append("sdf")', number=5)
#     # print(x)

# # for i in range(3):
# #     tmpdir = tempfile.mkdtemp()
# #     os.chdir(tmpdir)
# #     from src.core.lpm import lpm
# #     from src.core import LockFile
# #     LockFile._root = None
# #     lpminst = lpm()
# #     lpminst.install_pkg('amsmath')

def time_function(func_to_call_on_lpm: str):
    res = timeit.repeat(
        setup='\
            \nfrom src.commands.install_pkg import install_pkg\
            \nfrom src.core.lpm import lpm\
            \nimport tempfile\
            \nimport os\
            \ntmpdir = tempfile.mkdtemp()\
            \nos.rmdir(tmpdir)\
            \nimport shutil',
        stmt=f'\
            \nos.mkdir(tmpdir)\
            \nos.chdir(tmpdir)\
            \nfrom src.core import LockFile\
            \nLockFile._root = None\
            \nlpminst = lpm()\
            \nlpminst.{func_to_call_on_lpm}\
            \nos.chdir(r"{old_cwd}")\
            \nshutil.rmtree(tmpdir)',
        repeat=2,
        number=1
    )

    return {
        'min': min(res),
        'max': max(res),
        'avg': sum(res) / len(res),
        'all': res
    }


print(json.dumps(time_function('install_pkg("listings", accept_prompts=True)'), indent=2))
