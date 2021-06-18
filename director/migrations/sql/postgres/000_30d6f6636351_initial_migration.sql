-- +migrate Up

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TYPE statustype AS ENUM ('pending', 'progress', 'success', 'error', 'canceled');

CREATE TABLE workflows (
    id UUID NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    project VARCHAR(255) NOT NULL, 
    status statustype NOT NULL, 
    payload JSONB, 
    periodic BOOLEAN, 
    CONSTRAINT pk_workflows PRIMARY KEY (id)
);

CREATE INDEX ix_workflows_created_at ON workflows (created_at);

CREATE TABLE tasks (
    id UUID NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    key VARCHAR(255) NOT NULL, 
    status statustype NOT NULL, 
    previous JSONB, 
    workflow_id UUID NOT NULL, 
    CONSTRAINT pk_tasks PRIMARY KEY (id), 
    CONSTRAINT fk_tasks_workflow_id_workflows FOREIGN KEY(workflow_id) REFERENCES workflows (id)
);

CREATE INDEX ix_tasks_created_at ON tasks (created_at);

INSERT INTO alembic_version (version_num) VALUES ('30d6f6636351');


-- +migrate Down

DROP INDEX ix_tasks_created_at;

DROP TABLE tasks;

DROP INDEX ix_workflows_created_at;

DROP TABLE workflows;

DROP TYPE statustype;

DELETE FROM alembic_version WHERE alembic_version.version_num = '30d6f6636351';

DROP TABLE alembic_version;
