# Docs

## Preparation

- Create a Conda virtual environment

```bash
conda create --name testingenv python=3.11
conda activate testingenv
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

## Publish

- [ReadTheDocs](https://app.readthedocs.org/), log in with the author's Github account. It keeps updating webpages with the GitHub commit. 
- GitHub pages. Choose **/docs**

## Reference

- [PyDDA](https://github.com/openradar/PyDDA)
- [geocat-viz](https://github.com/NCAR/geocat-viz)

# GitHub Management

- For GitHub, enable **Discussions** and add **issue templates** in **Settings**.
- Add GitHub Repo description

```
Python-based Input Processing Tools for CESM
```



# [pypi](https://pypi.org)



# [Zenodo](https://zenodo.org)