CREATE EXTENSION IF NOT EXISTS postgis;

DROP SCHEMA IF EXISTS schema_a CASCADE;
DROP SCHEMA IF EXISTS schema_b CASCADE;

CREATE SCHEMA schema_a;

-- Create the application user
CREATE USER geoserver_appuser WITH PASSWORD 'geoserver_au';

-- Grant schema access
GRANT USAGE ON SCHEMA schema_a TO geoserver_appuser;

-- Grant default privileges for future objects created by the postgres user
GRANT USAGE ON SCHEMA schema_a TO geoserver_appuser;
ALTER DEFAULT PRIVILEGES FOR ROLE geoserver IN SCHEMA schema_a GRANT SELECT ON TABLES TO geoserver_appuser;
ALTER DEFAULT PRIVILEGES FOR ROLE geoserver IN SCHEMA schema_a GRANT USAGE, SELECT ON SEQUENCES TO geoserver_appuser;
ALTER DEFAULT PRIVILEGES FOR ROLE geoserver IN SCHEMA schema_a GRANT EXECUTE ON FUNCTIONS TO geoserver_appuser;
