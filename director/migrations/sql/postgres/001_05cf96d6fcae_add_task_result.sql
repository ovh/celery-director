-- +migrate Up

ALTER TABLE tasks ADD COLUMN result BYTEA;

UPDATE alembic_version SET version_num='05cf96d6fcae' WHERE alembic_version.version_num = '30d6f6636351';


-- +migrate Down

ALTER TABLE tasks DROP COLUMN result;

UPDATE alembic_version SET version_num='30d6f6636351' WHERE alembic_version.version_num = '05cf96d6fcae';
