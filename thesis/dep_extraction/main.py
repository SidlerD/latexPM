import sys

import pandas as pd

from thesis.dep_extraction import lpm, tlmgr


def get_required_pkgs():
    # Note: Name of bundle added to list because packages in tlmgr can depend on e.g. tools

    # Packages in "required" bundle
    latex_tools = ['tools'] + ["afterpage", "array", "bm", "calc", "dcolumn", "delarray", "enumerate", "fileerr", "fontsmpl", "ftnright", "hhline", "indentfirst", "layout", "longtable", "multicol", "rawfonts", "shellesc", "showkeys", "somedefs", "tabularx", "theorem", "trace", "varioref", "verbatim", "xr", "xspace"]
    latex_graphics = ['graphics'] + ["color", "graphics", "graphicx", "trig", "epsfig", "keyval", "lscape"]
    amslatex = ['amsmath', 'amscls']

    # .sty/.cls files in latex-base package at https://mirror.init7.net/ctan/systems/texlive/tlnet/archive/latex.tar.xz
    latex_base = ['latex'] + ['alltt', 'article', 'article', 'atbegshi-ltx', 'atveryend-ltx', 'bezier', 'book', 'book', 'doc-2016-02-15', 'doc-2021-06-01', 'doc', 'exscale', 'fix-cm', 'fixltx2e', 'flafter', 'fleqn', 'fltrace', 'fontenc', 'graphpap', 'ifthen', 'inputenc', 'latexrelease', 'latexsym', 'leqno', 'letter', 'letter', 'ltnews', 'ltxdoc', 'ltxguide', 'makeidx', 'minimal', 'newlfont', 'oldlfont', 'openbib', 'proc', 'proc', 'report', 'report', 'shortvrb', 'showidx', 'slides', 'slides', 'source2edoc', 'structuredlog', 'syntonly', 't1enc', 'textcomp-2018-08-11', 'textcomp', 'tracefnt']

    # Packages mentioned at https://www.ctan.org/tex-archive/macros/latex/base
    latex_base_add = ['l3kernel','expl3',  'l3backend', 'unicode-data', 'unicode-data', 'latex-firstaid']

    return latex_tools + latex_graphics + amslatex + latex_base + latex_base_add


def get_diff(df: pd.DataFrame, name: str, pkg_deps_lpm: list[str], pkg_deps_tlmgr: list[str]) -> None:
    required_pkgs = set(get_required_pkgs())

    lpm = set(pkg_deps_lpm) 
    tlmgr = set(pkg_deps_tlmgr)

    # Build sets for statistics
    identical = lpm.intersection(tlmgr)
    lpm_over = (lpm - tlmgr) - required_pkgs
    lpm_under = tlmgr - lpm

    # Add stats to dataframe
    df.loc[len(df)] = {
        'name': name,
        'lpm_deps': '; '.join(sorted(lpm)),
        'tlmgr_deps': '; '.join(sorted(tlmgr)),
        'identical': len(identical),
        'lpm_over': len(lpm_over),
        'lpm_over_names': len(lpm_over),
        'lpm_under': len(lpm_under), 
        'lpm_under_names': len(lpm_under), 
    }


def compare_deps(tlmgr_pkgs, lpm_pkgs):
    df = pd.DataFrame(
        {
            'name': [],
            'lpm_deps': [],
            'tlmgr_deps': [],
            'identical': [],
            'lpm_over': [],
            'lpm_over_names': [],
            'lpm_under': [],
            'lpm_under_names': [], 
        }
    )

    # Iterate over lpm_pkgs because it is a subset of tlmgr_deps
    for pkg in lpm_pkgs:
        pkg_name = pkg['name']

        # Get packages that lpm extracted for that pkg
        pkg_deps_lpm = pkg['depends']

        # Get packages that tlmgr specified as deps, if available
        pkg_tlmgr = next((item for item in tlmgr_pkgs if item["name"] == pkg_name), None)
        if not pkg_deps_tlmgr:
            continue
        pkg_deps_tlmgr = pkg_tlmgr['depends']

        # Calculate statistics and add to dataframe
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
        print("Please provide at least one package to measure")
        exit

    res = measure_accuracy(pkgs)
    
    # Not sure if the context manager is actually needed
    with pd.option_context("max_colwidth", 1000):
        res_short = res.drop(['lpm_deps', 'tlmgr_deps', 'lpm_over_names', 'lpm_under_names'], axis=1)
        print(res_short)

        options = {
            'hrules': True,
        }

        # Export short and full dataframe as LaTeX table
        res.style.format(escape='latex').to_latex('dep_comparison.tex', **options)
        res_short.style.format(escape='latex').to_latex('dep_comparison.short.tex', **options)