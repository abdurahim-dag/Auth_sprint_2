CREATE SCHEMA if not exists auth;

SET search_path TO auth,public;
ALTER ROLE app SET search_path TO auth,public;
