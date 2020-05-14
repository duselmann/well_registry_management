"""
Migrate initial users and roles.
https://docs.djangoproject.com/en/3.0/topics/migrations/

This one migration should be run on the 'postgres' database alias.
> python manage.py migrate --database=postgres  registry 0000
All subsequent migrations should be run on the 'migration'
> python manage.py migrate --database=migration

"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from django.db import migrations

from wellregistry.settings import DATABASE_NAME
from wellregistry.settings import DATABASE_USERNAME
from wellregistry.settings import DATABASE_PASSWORD
from wellregistry.settings import DATABASE_HOST
from wellregistry.settings import DATABASE_PORT
from wellregistry.settings import APP_DATABASE_NAME


from wellregistry.settings import APP_SCHEMA_NAME
from wellregistry.settings import APP_ADMIN_USERNAME
from wellregistry.settings import APP_CLIENT_USERNAME


def revoke_default(schema, defaults, target):
    if defaults == 'CRUD':
        defaults = "INSERT, SELECT, UPDATE, DELETE"

    return f"""
        ALTER DEFAULT PRIVILEGES 
        IN SCHEMA {schema} 
        REVOKE {defaults} 
        ON TABLES FROM {target}
    """


class Migration(migrations.Migration):
    """
    Proxy migration for creating the application database.

    Django connections cannot 'create database' because of transactions.
    the method will create its own connection to create the database.

    """

    initial = True

    dependencies = []

    operations = [
        # migrations.RunSQL(
        #     sql=revoke_default('public', 'CRUD', APP_ADMIN_USERNAME),
        #     reverse_sql=revoke_default(APP_SCHEMA_NAME, 'CRUD', APP_ADMIN_USERNAME)),
        # migrations.RunSQL(
        #     sql=revoke_default('public', 'SELECT', APP_CLIENT_USERNAME),
        #     reverse_sql=revoke_default(APP_SCHEMA_NAME, 'SELECT', APP_CLIENT_USERNAME)),
    ]

    def __init__(self, type1=None, type2=None):
        super().__init__(type1, type2)
        create_database()


def create_database():
    """
    Creates the application database.

    This creates its own connection because Django connections
    cannot execute postgres 'create database'

    Notice that it runs two SQL commands.
    The first checks the database existence.
    While the second creates the database if it is needed.

    """
    with psycopg2.connect(database=DATABASE_NAME, user=DATABASE_USERNAME, password=DATABASE_PASSWORD,
                          host=DATABASE_HOST, port=DATABASE_PORT) as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        sql_database_not_exists = f"""
            SELECT 1 as needed
            WHERE NOT EXISTS 
            (SELECT FROM pg_database 
            WHERE datname = '{APP_DATABASE_NAME}');
        """
        sql_create_db = f"CREATE DATABASE {APP_DATABASE_NAME};"

        cursor.execute(sql_database_not_exists)
        rows = cursor.fetchall()

        if len(rows) == 0:
            print(f"'{APP_DATABASE_NAME}' database exists!")
        else:
            print(f"'{APP_DATABASE_NAME}' database needed.")

        for row in rows:
            if row[0] == 1:
                cursor.execute(sql_create_db)
                print(f"'{APP_DATABASE_NAME}' database created.")