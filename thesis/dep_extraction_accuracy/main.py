from thesis.dep_extraction_accuracy import lpm
import tlmgr

def get_required_pkgs():
    latex_tools = ["afterpage", "array", "bm", "calc", "dcolumn", "delarray", "enumerate", "fileerr", "fontsmpl", "ftnright", "hhline", "indentfirst", "layout", "longtable", "multicol", "rawfonts", "shellesc", "showkeys", "somedefs", "tabularx", "theorem", "trace", "varioref", "verbatim", "xr", "xspace"]
    latex_graphics = ["color", "graphics", "graphicx", "trig", "epsfig", "keyval", "lscape"]
    amslatex = ['amsmath', 'amscls']

    return latex_tools + latex_graphics + amslatex

def compare_deps(tlmgr_pkgs, lpm_pkgs):
    required_pkgs = get_required_pkgs()

    # Iterate over lpm_deps because it is a subset of tlmgr_deps
    for pkg in lpm_pkgs:
        pkg_name = pkg['name']
        # Get packages that lpm extracted
        pkg_deps_lpm = pkg['depends']

        # Get packages that tlmgr specified as deps, if available
        pkg_tlmgr = next((item for item in tlmgr_pkgs if item["name"] == pkg_name), None)
        pkg_deps_tlmgr = pkg_tlmgr['depends'] if pkg_tlmgr else None

        


def measure_accuracy():
    tlmgr_pkgs = tlmgr.get_pkgs_with_deps()
    lpm_pkgs = lpm.get_deps_of_pkgs(tlmgr_pkgs)

    compare_deps(tlmgr_pkgs, lpm_pkgs)


if __name__ == "__main__":
    measure_accuracy()