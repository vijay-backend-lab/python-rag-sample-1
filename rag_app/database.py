from sqlalchemy import create_engine, event


def create_read_only_mysql_engine(mysql_url: str):
    """Create a pooled engine whose MySQL sessions reject data-changing transactions.

    A database account granted only SELECT remains the primary security boundary;
    the session setting is defense in depth.
    """
    engine = create_engine(mysql_url, pool_pre_ping=True)
    if engine.dialect.name == "mysql":
        @event.listens_for(engine, "connect")
        def set_read_only(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SET SESSION TRANSACTION READ ONLY")
            finally:
                cursor.close()
    return engine
