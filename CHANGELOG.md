# Changelog

## 0.3.1 - 2020-12-08
### Changed
- Upgrade Celery and Kombu packages for bug fixes (celery 4.4.0 to 4.4.7, kombu 4.6.7 to 4.6.11)

## 0.3.0 - 2020-11-18
### Fixed
- Roll back the session when an unhandled exception occurred during the request

### Added
- Add the support of celery crontab scheduler
- Add auto refresh workflows list in director home page


## 0.2.2 - 2020-10-16
### Fixed
- Add type deletion during downgrade
- Fix mysql string column length (database upgrade required: `director db upgrade`)

### Added
- Add an example about a group of tasks
- Add index on workflow_id field in tasks table

### Changed
- Rename default workflow to example.ETL


## 0.2.1 - 2020-08-20
### Fixed
- Fix issue with icons when using the `DIRECTOR_ENABLE_CDN=false` and  `director dlassets` command


## 0.2.0 - 2020-08-20
### Added
- Add Sentry error reporting (use `DIRECTOR_ENTRY_DSN` setting)
- Add GitHub link in the Web UI header

### Fixed
- Fix WebUI workflow table.
- Fix WebUI task color status for `progress`

### Changed
- Limit search placeholder on dates and IDs

## 0.1.0 - 2020-08-10
### Fixed
- Handle the default pagination setting

### Changed
- New interface based on d3.js
- Support the mode history in permalinks


## 0.0.6 - 2020-07-27
### Fixed
- Fix issue in transactions with periodic tasks and Celery queues
- Fix bad comma in documentation markdown


## 0.0.5 - 2020-07-22
### Added
- Handle user authentication (database upgrade required: `director db upgrade`)
- Support the Celery queues
- Add permalink for workflows

### Changed
- Remove HTTP code from description


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
