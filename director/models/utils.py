from sqlalchemy_utils import JSONType

try:
    from sqlalchemy.dialects.postgresql import JSONB

    has_postgres_jsonb = True
except ImportError:
    has_postgres_jsonb = False


class JSONBType(JSONType):
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and has_postgres_jsonb:
            return dialect.type_descriptor(JSONB())
        return super(JSONBType, self).load_dialect_impl(dialect)
