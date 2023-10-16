import sys

from thesis.timing import m_init, m_install_amsmath, m_install_with_deps, m_build

def main(n):
    m_install_amsmath.measure(n)
    m_build.measure(n)
    m_install_with_deps.measure(n)
    m_init.measure(n)
    

if __name__ == '__main__':
    n = sys.argv[1] if len(sys.argv) == 2 else 30
    
    main(n)
    