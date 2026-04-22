FROM postgres:16-alpine

COPY init/01_schema.sql /docker-entrypoint-initdb.d/01_schema.sql

EXPOSE 5432