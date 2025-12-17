#     Column     |         Type          | Collation | Nullable | Default
# ---------------+-----------------------+-----------+----------+---------
#  id            | bigint                |           |          |
#  street_name   | character varying     |           |          |
#  street_number | character varying     |           |          |
#  postal_code   | bigint                |           |          |
#  town_name     | character varying     |           |          |
#  canton        | character varying     |           |          |
#  label         | character varying     |           |          |
#  geometry      | geometry(Point,4326)  |           |          |

from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import DeclarativeBase
from geoalchemy2 import Geometry


class Base(DeclarativeBase):
    pass


def get_address_model(schema_name: str = "public"):
    """
    Create an Address model with a dynamic schema.

    Args:
        schema_name: The PostgreSQL schema name (default: "public")

    Returns:
        Address model class configured for the specified schema
    """

    class Address(Base):
        __tablename__ = "t_address"
        __table_args__ = {"schema": schema_name}

        id = Column(BigInteger, primary_key=True)
        street_name = Column(String)
        street_number = Column(String)
        postal_code = Column(BigInteger)
        town_name = Column(String)
        canton = Column(String)
        label = Column(String)
        geometry = Column(Geometry(geometry_type="POINT", srid=4326))

    return Address
