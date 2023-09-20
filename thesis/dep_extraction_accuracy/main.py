import sys
from thesis.dep_extraction_accuracy import lpm
from thesis.dep_extraction_accuracy import tlmgr
import pandas as pd


def get_required_pkgs():
    latex_tools = ["afterpage", "array", "bm", "calc", "dcolumn", "delarray", "enumerate", "fileerr", "fontsmpl", "ftnright", "hhline", "indentfirst", "layout", "longtable", "multicol", "rawfonts", "shellesc", "showkeys", "somedefs", "tabularx", "theorem", "trace", "varioref", "verbatim", "xr", "xspace"]
    latex_graphics = ["color", "graphics", "graphicx", "trig", "epsfig", "keyval", "lscape"]
    amslatex = ['amsmath', 'amscls']

    return latex_tools + latex_graphics + amslatex

def get_diff(df: pd.DataFrame, name: str, pkg_deps_lpm: list[str], pkg_deps_tlmgr: list[str]) -> None:
    required_pkgs = set(get_required_pkgs())

    # Remove packages that are in bundle "required" since they can be assumed to be present
    lpm = set(pkg_deps_lpm) - required_pkgs
    tlmgr = set(pkg_deps_tlmgr) - required_pkgs

    identical = lpm.intersection(tlmgr)
    lpm_over = lpm - tlmgr
    lpm_under = tlmgr - lpm

    df.loc[len(df)] = {
        'name': name,
        'lpm_deps': ';'.join(lpm),
        'tlmgr_deps': ';'.join(tlmgr),
        'identical': len(identical),
        'lpm_over': len(lpm_over),
        'lpm_under': len(lpm_under)
    }

def compare_deps(tlmgr_pkgs, lpm_pkgs):

    df = pd.DataFrame(
        {
            'name': [],
            'lpm_deps': [],
            'tlmgr_deps': [],
            'identical': [],
            'lpm_over': [],
            'lpm_under': []
        }
    )
    # df.set_index('name', inplace=True)
   
    df.head()

    # Iterate over lpm_deps because it is a subset of tlmgr_deps
    for pkg in lpm_pkgs:
        pkg_name = pkg['name']
        # Get packages that lpm extracted
        pkg_deps_lpm = pkg['depends']

        # Get packages that tlmgr specified as deps, if available
        pkg_tlmgr = next((item for item in tlmgr_pkgs if item["name"] == pkg_name), None)
        pkg_deps_tlmgr = pkg_tlmgr['depends'] if pkg_tlmgr else None

        get_diff(df, pkg_name, pkg_deps_lpm, pkg_deps_tlmgr)

    return df

def measure_accuracy(pkgs: list[str] = None):
    tlmgr_pkgs = tlmgr.get_pkgs_with_deps()
    if pkgs:
        tlmgr_pkgs = [pkg for pkg in tlmgr_pkgs if pkg['name'] in pkgs]
    lpm_pkgs = lpm.get_deps_of_pkgs(tlmgr_pkgs)

    return compare_deps(tlmgr_pkgs, lpm_pkgs)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pkgs = sys.argv[1:]
    else:
        # Build for packages that are included in texlive-latex-recommended: https://tex.stackexchange.com/a/504566/293514
        pkgs = ["anysize", "beamer", "booktabs", "breqn", "caption", "cite", "cmap", "crop", "ctable", "eso-pic", "euenc", "euler", "etoolbox", "extsizes", "fancybox", "fancyref", "fancyvrb", "filehook", "float", "fontspec", "fp", "index", "jknapltx", "koma-script", "latexbug", "l3experimental", "l3kernel", "l3packages", "lineno", "listings", "lwarp", "mathspec", "mathtools", "mdwtools", "memoir", "metalogo", "microtype", "ms", "ntgclass", "parskip", "pdfpages", "polyglossia", "powerdot", "psfrag", "rcs", "sansmath", "section", "seminar", "sepnum", "setspace", "subfig", "textcase", "thumbpdf", "translator", "typehtml", "ucharcat", "underscore", "unicode-math", "xcolor", "xkeyval", "xltxtra", "xunicode"]
    
    res = measure_accuracy(pkgs)

    
    # Not sure if the context manager is actually needed
    with pd.option_context("max_colwidth", 1000):
        res_short = res.drop(['lpm_deps', 'tlmgr_deps'], axis=1)
        print(res_short)

        # res.to_csv('dep_comparison.csv', index=False)
        res.style.to_latex('dep_comparison.tex')
        res_short.style.to_latex('dep_comparison.short.tex')