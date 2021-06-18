-- +migrate Up

CREATE TABLE users (
    id UUID NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    username VARCHAR(255) NOT NULL, 
    password VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_users PRIMARY KEY (id), 
    CONSTRAINT uq_users_username UNIQUE (username)
);

CREATE INDEX ix_users_created_at ON users (created_at);

UPDATE alembic_version SET version_num='3f8466b16023' WHERE alembic_version.version_num = '05cf96d6fcae';


-- +migrate Down

DROP INDEX ix_users_created_at;

DROP TABLE users;

UPDATE alembic_version SET version_num='05cf96d6fcae' WHERE alembic_version.version_num = '3f8466b16023';
