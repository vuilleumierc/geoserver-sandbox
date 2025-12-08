import subprocess
from geoservercloud import GeoServerCloud
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from models.address import Base, get_address_model


engine = create_engine(
    "postgresql+psycopg2://geoserver:geoserver@localhost:5432/geoserver"
)

# Create address table in schema_a and schema_b
AddressA = get_address_model("schema_a")
AddressB = get_address_model("schema_b")
Base.metadata.create_all(engine)

# Load sample data for schema_a.t_address
with open("sample-data/sample-addresses-a.json") as f:
    sample_addresses_a = json.load(f)["addresses"]

# Load sample data for schema_b.t_address
with open("sample-data/sample-addresses-b.json") as f:
    sample_addresses_b = json.load(f)["addresses"]

with Session(engine) as session:
    for addr in sample_addresses_a:
        address = AddressA(**addr)
        session.merge(address)  # Upsert: insert if new, update if exists
    for addr in sample_addresses_b:
        address = AddressB(**addr)
        session.merge(address)
    session.commit()

gs = GeoServerCloud(
    url="http://localhost:8080/geoserver",
    user="admin",
    password="geoserver",
)

content, status = gs.create_workspace("test")
print(f"Workspace created: {status}")

content, status = gs.create_jndi_datastore(
    workspace_name="test",
    datastore_name="postgis",
    jndi_reference="java:comp/env/jdbc/postgis",
    pg_schema="schema_a",
)
print(f"Datastore created: {status}")

content, status = gs.create_feature_type(
    layer_name="t_address",
    workspace_name="test",
    datastore_name="postgis",
    epsg=2056,
)
print(f"Feature type created: {status}")

content, status = gs.create_style_from_file(
    style_name="house_number",
    file="resources/house_number.sld",
    workspace_name="test",
)
print(f"Style created: {status}")

content, status = gs.set_default_layer_style(
    layer_name="t_address",
    workspace_name="test",
    style="house_number",
)
print(f"Default style set: {status}")

content, status = gs.publish_gwc_layer(
    layer="t_address",
    workspace_name="test",
    epsg=2056,
)
print(f"GWC layer published: {status}")

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

# Rotate the DB schemas
with engine.begin() as conn:
    conn.execute(text("DROP SCHEMA IF EXISTS schema_a CASCADE;"))
    conn.execute(text("ALTER SCHEMA schema_b RENAME TO schema_a;"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_b;"))

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
subprocess.run(["docker", "compose", "down", "geoserver"], check=True)
subprocess.run(["docker", "compose", "up", "-d", "--wait", "geoserver"], check=True)

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

content, status = gs.delete_workspace("test")
print(f"Workspace deleted: {status}")
