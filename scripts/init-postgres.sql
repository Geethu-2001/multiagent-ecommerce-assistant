-- This file runs as the database owner during first-time Docker initialization.
-- The application connects as agent_reader; only schema/seed scripts use app_user.
CREATE ROLE agent_reader LOGIN PASSWORD 'reader_change_me';
GRANT CONNECT ON DATABASE ecommerce_db TO agent_reader;
GRANT USAGE ON SCHEMA public TO agent_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE app_user IN SCHEMA public GRANT SELECT ON TABLES TO agent_reader;
