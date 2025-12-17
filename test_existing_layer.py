import subprocess
from geoservercloud import GeoServerCloud
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from models.address import Base, get_address_model


engine = create_engine(
    "postgresql+psycopg2://geoserver:geoserver@localhost:5432/postgis"
)

gs = GeoServerCloud(
    url="http://localhost:8080/",
    user="admin",
    password="geoserver",
)


def create_table_and_insert_data(conn, schema_name):
    """
    Create table and insert data within a given connection/transaction.

    Args:
        conn: SQLAlchemy connection (from engine.begin())
        schema_name: Schema name to create the table in
    """
    # Create table in the specified schema
    Address = get_address_model(schema_name)
    Base.metadata.create_all(conn)

    # Insert data using a session bound to this connection
    with Session(bind=conn) as session:
        with open(f"sample-data/sample-addresses-{schema_name}.json") as f:
            sample_addresses = json.load(f)["addresses"]

        for addr in sample_addresses:
            address = Address(**addr)
            session.merge(address)  # Upsert: insert if new, update if exists
        session.flush()  # Flush to ensure data is written in this transaction


# Create address table in schema_a
with engine.begin() as conn:
    create_table_and_insert_data(conn, "schema_a")

response = gs.get_tile(
    layer="test:t_address",
    format="image/png",
    tile_matrix_set="EPSG:4326",
    tile_matrix="EPSG:4326:15",  # Zoom level 15
    row=7836,
    column=34122,
)
print(f"GetTile response status: {response._response.status_code}")
with open("generated/t_address_tile_0.png", "wb") as f:
    f.write(response._response.content)

# Rotate the DB schemas - all in one transaction
with engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_b;"))

    # Create table and insert data in schema_b
    create_table_and_insert_data(conn, "schema_b")

    # Rotate schemas
    conn.execute(text("DROP SCHEMA IF EXISTS schema_a CASCADE;"))
    conn.execute(text("ALTER SCHEMA schema_b RENAME TO schema_a;"))
    conn.execute(text("GRANT USAGE ON SCHEMA schema_a TO geoserver_appuser;"))
    conn.execute(
        text("GRANT SELECT ON ALL TABLES IN SCHEMA schema_a TO geoserver_appuser;")
    )

response = gs.get_tile(
    layer="test:t_address",
    format="image/png",
    tile_matrix_set="EPSG:4326",
    tile_matrix="EPSG:4326:16",  # Zoom level 16
    row=15673,
    column=68244,
)
print(f"GetTile response status: {response._response.status_code}")
with open("generated/t_address_tile_1.png", "wb") as f:
    f.write(response._response.content)

# Restart GeoServer
subprocess.run(["docker", "compose", "down", "gwc"], check=True)
subprocess.run(["docker", "compose", "up", "-d", "--wait"], check=True)

response = gs.get_tile(
    layer="test:t_address",
    format="image/png",
    tile_matrix_set="EPSG:4326",
    tile_matrix="EPSG:4326:14",  # Zoom level 14
    row=3918,
    column=17061,
)
print(f"GetTile response status: {response._response.status_code}")
with open("generated/t_address_tile_2.png", "wb") as f:
    f.write(response._response.content)
