"""
Migrate initial users and roles.

https://docs.djangoproject.com/en/3.0/topics/migrations/

This one migration should be run on the 'postgres' database alias.
> python manage.py migrate --database=postgres  registry 0000
All subsequent migrations should be run on the 'migration'
> python manage.py migrate --database=migration
"""
import sys

from django.db import migrations
from django.conf import settings
import wellregistry.pgsql_utils as pgsql

env = settings.ENVIRONMENT


class Migration(migrations.Migration):
    """
    SQL to create the database user roles.

    This creates a new database and schema owner in PG for an application specific name.
    The "postgres" database and password is Already created during database install.

    instance (daemon)
        postgres database
            'postgres' admin user name and password
                loosely like the Oracle 'sys' schema
        application database
        app db owner(roles)
            a postgres role granted logon and DDL
            with optional schemas, 'public' default
        read-only user(roles)
            (typical but not the registry)
            a postgres role granted logon and SELECT only access
        client user(roles)
            (aka agency or provider) connection to postgres for all django client actions
            a postgres role granted logon and SELECT access and CRUD/DML on limited tables
            all client logins will be authenticated with login.gov
        admin user(roles)
            (aka superuser) connection to postgres for all django admin actions
            a postgres role granted logon and all CRUD/DML access
            first authenticated with login.gov
                then authenticated with django admin login
    """

    initial = False

    dependencies = []
    # We have an option here. we can use the empty dependencies or the following 'postgres' migration dependency.
    # dependencies = [('postgres', '0001_create_db_users')]
    # However, when a dependency is used then the executions must be in he django_migrations table.
    # In order for this metadata to be correct in the application database requires that the migration
    # for postgres entries to be run in fake mode for the application database. This prevents them from
    # running twice and causing errors. In an attempt to make them idempotent, the roles are dropped first.
    # It turns out that if the roles have dependencies then they cannot be dropped. This drop was done
    # because there is no CREATE ROLE IF NOT EXISTS in postgres. Also, there is no clean way for Django to
    # check if an object exists like we have for the yaml based liquibase changelogs.
    # python -m manage migrate --fake postgres

    if 'test' in sys.argv:
        operations = []
    else:
        operations = [

            # create a application specific schema within the database the connection is made
            migrations.RunSQL(
                sql=f"""CREATE SCHEMA IF NOT EXISTS {env['APP_SCHEMA_NAME']}
                        AUTHORIZATION {env['APP_SCHEMA_OWNER_USERNAME']};""",
                reverse_sql=f"DROP SCHEMA IF EXISTS {env['APP_SCHEMA_NAME']};"),

            migrations.RunSQL(
                sql=f"ALTER DATABASE {env['APP_DATABASE_NAME']} SET search_path = {env['APP_SCHEMA_NAME']}, public;",
                reverse_sql=f"ALTER DATABASE {env['APP_DATABASE_NAME']} RESET search_path;"),

            # create a login user that will used by the Django admin process to manage entries
            migrations.RunSQL(
                sql=pgsql.create_login_role(env['APP_ADMIN_USERNAME'], env['APP_ADMIN_PASSWORD']),
                reverse_sql=pgsql.drop_role(env['APP_ADMIN_USERNAME'])),

            # grant CRUD to admin user
            migrations.RunSQL(
                sql=pgsql.grant_default(env['APP_SCHEMA_NAME'], 'CRUD', env['APP_ADMIN_USERNAME']),
                reverse_sql=pgsql.revoke_default(env['APP_SCHEMA_NAME'], 'CRUD', env['APP_ADMIN_USERNAME'])),

            # create a login user that will used by the app users to manage entries
            migrations.RunSQL(
                sql=pgsql.create_login_role(env['APP_CLIENT_USERNAME'], env['APP_CLIENT_PASSWORD']),
                reverse_sql=pgsql.drop_role(env['APP_CLIENT_USERNAME'])),

            # grant select to client user
            migrations.RunSQL(
                sql=pgsql.grant_default(env['APP_SCHEMA_NAME'], 'SELECT', env['APP_CLIENT_USERNAME']),
                reverse_sql=pgsql.revoke_default(env['APP_SCHEMA_NAME'], 'SELECT', env['APP_CLIENT_USERNAME'])),

            # grant CRUD to app user -- after 0001_initial, this cannot be granted until the tables is created
        ]
