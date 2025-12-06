# Changelog

All notable changes to GeoSnap will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-12-06

### Added
- Word report generation in reverse mode (Excel → KMZ + Word)
- Comprehensive test suite (68 tests, 47% coverage)
- GitHub issue templates for bug reports and feature requests
- SECURITY.md for vulnerability reporting
- CHANGELOG.md for version tracking

### Changed
- Photos in reverse mode now sorted by Nº column instead of Excel row order
- Updated CONTRIBUTING.md with Ruff linting instructions
- Improved README with correct repository URLs

### Fixed
- Word report photo ordering based on sequence number
- EXIF rotation correction in Word reports

## [2.1.0] - 2025-12-05

### Added
- "Generar informe Word" checkbox in reverse mode
- Word reports with landscape A4 layout, 4 photos per page
- Caption styling: bold "Figura X.-" prefix

### Changed
- Removed "Incluir fotos sin GPS" checkbox (now always True)
- Word checkbox moved to top-right corner of UI

## [2.0.0] - 2025-11-26

### Added
- Reverse mode: Excel → KMZ generation
- Batch processing support
- Settings dialog with customizable parameters
- Profile management for saving configurations

### Changed
- Complete UI redesign with ttkbootstrap
- Multi-threaded photo processing
- Improved progress feedback

## [1.0.0] - 2025-11-21

### Added
- Initial release
- Photos → KMZ + Excel generation
- GPS metadata extraction from EXIF
- Thumbnail generation for KMZ
- Basic GUI interface
