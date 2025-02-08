.. currentmodule:: IPTpy

IPTpy User Guide
================
IPTpy is a Python-based tool designed to process input data for the `Community Earth System Model (CESM) <https://www.cesm.ucar.edu/>`_. It serves as a partial replacement for the `NCL-based Input Processing Tool (IPT) for MUSICA <https://github.com/NCAR/IPT/tree/master>`_, which is no longer maintained or updated by `NSF National Center for Atmospheric Research (NCAR) <https://ncar.ucar.edu/>`_. 

.. grid:: 1 1 2 2
    :margin: 4 4 0 0
    :gutter: 2

    .. grid-item-card:: Getting Started
        :class-title: custom-title
        :class-body: custom-body
        :link: notebooks/getting-started
        :link-type: doc
        :text-align: left

        A good place to start for new users

        .. image:: _static/images/icons/tips.svg
            :height: 30px
            :width: 30px

    .. grid-item-card::  Examples
        :class-title: custom-title
        :class-body: custom-body
        :link: examples
        :link-type: doc

        A gallery of examples using IPTpy

        .. image:: _static/images/icons/science.svg
            :height: 30px
            :width: 30px

    .. grid-item-card::  Installation
        :class-title: custom-title
        :class-body: custom-body
        :link: notebooks/installation
        :link-type: doc

        Installation instructions for IPTpy

        .. image:: _static/images/icons/download.svg
            :height: 30px
            :width: 30px

    .. grid-item-card::  Development
        :class-title: custom-title
        :class-body: custom-body
        :link: development
        :link-type: doc

        Future development for IPTpy

        .. image:: _static/images/icons/code.svg
            :height: 30px
            :width: 30px

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: For Users
   
   Getting Start <notebooks/getting-started.md>
   Installation <notebooks/installation.md>
   Source Data Download <notebooks/source-data-download.md>
   User API Reference <api.rst>
   Understand the Process <notebooks/understand.md>
   Usage Examples <examples.rst> 
   Cite IPTpy <notebooks/citation.md>

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: For Developers

   Development <development.rst>

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting Support

   Support <notebooks/support.md>
   GitHub Issues <https://github.com/envdes/IPTpy/issues>   