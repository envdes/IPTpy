# Docs

## Preparation

- Create a Conda virtual environment

```bash
conda create --name testingenv python=3.11
conda activate testingenv

conda env remove --name testingenv
```

- Install packages
  - sphinx-book-theme: template
  - recommonmark: for markdown 
  - sphinx: for docs build 
  - myst-nb: for markdown as well
  - sphinx_design: for rst grid layout

```bash
conda install sphinx-book-theme recommonmark sphinx myst-nb
pip install sphinx_design

conda install -c conda-forge esmpy
```

- Install IPTpy locally

```bash
pip install -e /Users/user/Desktop/envdes/IPTpy

# verify installation
conda list iptpy
```

## Building the webpage

```bash
conda activate testingenv
```

**Install Sphinx and Create Documentation**

```bash
cd /Users/user/Desktop/envdes/IPTpy/docs/
sphinx-quickstart

> Separate source and build directories (y/n) [n]:
> Project name: IPTpy
> Author name(s): Yuan Sun, Zhonghua Zheng
> Project release []: 'v0.0.0'
> Project language [en]:
```

**Build HTML Files Locally**

```bash
cd /Users/user/Desktop/envdes/IPTpy
sphinx-build -b html docs/ docs/_build

# open the html
open /Users/user/Desktop/envdes/IPTpy/docs/_build/index.html
```

### Errors from building

**error1**: Extension error (sphinx.ext.autosummary):
Handler <function process_generate_options at 0x1092b19e0> for event 'builder-inited' threw an exception (exception: no module named iptpy.anthro_emission.FV)

**solved** should be iptpy.anthro_emission.fv.FV.

- If the code is modified, the API might be outdated. Need to create a new virtual environment and install IPTpy again based on the new code.

**error2**: 

WARNING: while setting up extension myst_nb: role 'sub-ref' is already registered, it will be overridden [app.add_role]
WARNING: while setting up extension myst_nb: directive 'figure-md' is already registered, it will be overridden [app.add_directive]

Exception occurred:
  File "/Users/user/miniconda3/envs/testingenv/lib/python3.11/site-packages/myst_parser/sphinx_ext/main.py", line 49, in setup_sphinx
    app.registry.transforms.remove(SphinxUnreferencedFootnotesDetector)
ValueError: list.remove(x): x not in list

**note**: myst-nb and myst-parser are both trying to define the same elements, and the ValueError about SphinxUnreferencedFootnotesDetector suggests an issue with the internal Sphinx registry. [ref](https://github.com/executablebooks/MyST-Parser/issues/962)

**error3**:

Extension error:
source_suffix '.md' is already registered

**note**: recommonmark conflicts with myst_parser. Use myst_parser instead of recommonmark + myst_nb to render latex math in markdown.

## Publish

- [ReadTheDocs](https://app.readthedocs.org/), log in with the author's Github account. It keeps updating webpages with the GitHub commit. 
- GitHub pages. 
  - Add a .github/workflows/docs.yml to build webpage automatically.
  - enable Read and write permissions for `secrets.GITHUB_TOKEN` in `Action`.


## Reference

- [PyDDA](https://github.com/openradar/PyDDA)
- [geocat-viz](https://github.com/NCAR/geocat-viz)

# GitHub Management

- For GitHub, enable **Discussions** and add **issue templates** in **Settings**.
- Add GitHub Repo description

```
Python-based Input Processing Tools for the Community Earth System Model (CESM)
```



# [pypi](https://pypi.org)

- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

```bash
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m build
```



# [conda-forge]()



# [Zenodo](https://zenodo.org)