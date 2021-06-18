-- +migrate Up

CREATE INDEX ix_tasks_workflow_id ON tasks (workflow_id);

UPDATE alembic_version SET version_num='063ff371f2da' WHERE alembic_version.version_num = '3f8466b16023';


-- +migrate Down

DROP INDEX ix_tasks_workflow_id;

UPDATE alembic_version SET version_num='3f8466b16023' WHERE alembic_version.version_num = '063ff371f2da';
