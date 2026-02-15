# Changelog
All notable changes to this project will be documented in this file.

<p>The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).<br/>
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).</p>

## [TODO]

## [Unreleased]

## [1.3.0] - 2026-02-15
- An option to discard notes that are not defined in the drum map.
- Changed "force percussion" option to affect notes that were not defined in the drum map.
- Fixed a problem with circular imports.
- Log notes as they are discarded.
- Log notes as they are forced into percussion channel.

## [1.2.0] - 2026-02-15
- Changed maximum line length to 100 (based on PEP 8).
- Refactored to use AppConfig and MIDIHandler classes.

## [1.1.0] - 2026-02-04
- Remove duplicate MIDI notes.

## [1.0.2] - 2026-02-01
- Include default drum mapping CSV file with the package.

## [1.0.1] - 2026-02-01
- Default drum mapping file path is now resolved using main script path. This
  fixes a problem when trying to run the script from any other directory than
  the script path.
- Updated the README.

## [1.0.0] - 2026-01-31
- Initial version.
