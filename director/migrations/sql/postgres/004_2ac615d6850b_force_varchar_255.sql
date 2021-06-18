-- +migrate Up

ALTER TABLE tasks ALTER COLUMN key TYPE VARCHAR(255);

ALTER TABLE users ALTER COLUMN password TYPE VARCHAR(255);

ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(255);

ALTER TABLE workflows ALTER COLUMN name TYPE VARCHAR(255);

ALTER TABLE workflows ALTER COLUMN project TYPE VARCHAR(255);

UPDATE alembic_version SET version_num='2ac615d6850b' WHERE alembic_version.version_num = '063ff371f2da';


-- +migrate Down

ALTER TABLE workflows ALTER COLUMN project TYPE VARCHAR;

ALTER TABLE workflows ALTER COLUMN name TYPE VARCHAR;

ALTER TABLE users ALTER COLUMN username TYPE VARCHAR;

ALTER TABLE users ALTER COLUMN password TYPE VARCHAR;

ALTER TABLE tasks ALTER COLUMN key TYPE VARCHAR;

UPDATE alembic_version SET version_num='063ff371f2da' WHERE alembic_version.version_num = '2ac615d6850b';
