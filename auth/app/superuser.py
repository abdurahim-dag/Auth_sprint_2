import click
from flask import Blueprint

from app.models import Role
from app.services.db import insert_model
from app.services.db import set_role
from app.services.db import user_add
from app.services.db import user_get_by_email


superuser = Blueprint('superuser', __name__)

# Define the command to add a superuser
@superuser.cli.command('create')
@click.option('--username', prompt=True, help='Superuser username')
@click.option('--email', prompt=True, help='Superuser email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Superuser password')
def create_superuser(username, email, password):
    # Check if the user already exists
    user = user_get_by_email(email)
    if user:
        click.echo('Superuser already exists')
        return

    # Create the new user with admin privileges
    user_id = user_add(username, email, password, status = True).id
    role_id = insert_model({'name': 'admin'}, Role).id

    set_role(user_id, role_id)
    click.echo('Superuser and role admin created successfully')
