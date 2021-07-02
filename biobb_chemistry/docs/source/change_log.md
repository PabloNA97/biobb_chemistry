# Biobb Chemistry changelog

## What's new in version [3.6.0](https://github.com/bioexcel/biobb_chemistry/releases/tag/v3.6.0)?
In version 3.6.0 the dependency biobb_common has been updated to 3.6.0 version. 

### New features

* Update to biobb_common 3.6.0 (general)

## What's new in version [3.5.0](https://github.com/bioexcel/biobb_chemistry/releases/tag/v3.5.0)?
In version 3.5.0 the dependency biobb_common has been updated to 3.5.1 version. Also, there has been implemented the new version of docstrings, therefore the JSON Schemas have been modified.

### New features

* Update to biobb_common 3.5.1 (general)
* New extended and improved JSON schemas (Galaxy and CWL-compliant) (general)

### Other changes

* New docstrings

## What's new in version [3.0.2](https://github.com/bioexcel/biobb_chemistry/releases/tag/v3.0.2)?
In version 3.0.2 the dependency biobb_common has been updated to 3.0.1 version.

### New features

* Update to biobb_common 3.0.1

## What's new in version [3.0.1](https://github.com/bioexcel/biobb_chemistry/releases/tag/v3.0.1)?
In version 3.0.1 Ambertools has been updated from 19.10 to 20.0. Openbabel has been downgraded and fixed to 2.4.1. A new conda installation recipe has been introduced.

### New features

* Update to Ambertools 20.0 (ambertools module)
* Fixed to Openbabel 2.4.1 (babelm module)

### Bug fixes

* Fixed bugs in unittests for .itp, .lib and .prmtop files (unittests)

## What's new in version [3.0.0](https://github.com/bioexcel/biobb_chemistry/releases/tag/v3.0.0)?
In version 3.0.0 Python has been updated to version 3.7. Big changes in the documentation style and content. Finally a new conda installation recipe has been introduced.

### New features

* Update to Python 3.7 (general)
* New conda installer (installation)
* Adding type hinting for easier usage (API)
* Deprecating os.path in favour of pathlib.path (modules)
* New command line documentation (documentation)

### Other changes

* New documentation styles (documentation)