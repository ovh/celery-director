# Changelog

## 0.0.4 - 2020-05-11
### Added
- Save the result in database (database upgrade required: `director db upgrade`)
- Limit the number of workflows to return

### Fixed
- Fix a bug when last task raises a Celery error
- Support the progress status
- Properly handle the 404 errors


## 0.0.3 - 2020-02-28
### Added
- Add the workflow relaunch
- Improve the listing of workflows in the CLI
- Add the jsonSchema support for the workflows payload

### Fixed
- Fix the roboto font display in WebUI
- Fix a test


## 0.0.2 - 2020-02-07
### Added
- Add Travis integration.
- Add the user documentation.
- Add the `db` command to offer the features from Flask Migrate.
- Add version info in the CLI when using `--version`.
- Add environment variables and information in the `.env` template.
- Add `DIRECTOR_CONFIG` environment variable to customize `.env` file.
- Make the payload optional when using the `workflow run` command.

### Changed
- Database migration has been overwritten to fix some issues.
- README includes badges, image, logo and link to the documentation.

### Fixed
- Flower command is not using the `DIRECTOR_FLOWER_URL` anymore.
- The `.env` file is optional, the `DIRECTOR_*`can be exported as environment variables.

## 0.0.1 - 2020-01-30
### Added
- Initial release.
