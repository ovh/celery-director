from werkzeug.security import generate_password_hash
from terminaltables import AsciiTable


from director.context import pass_ctx
from director.exceptions import UserNotFound
from director.models.users import User

import click


def _get_users():
    return User.query.all()


@click.group()
def user():
    """Manage the users"""


@user.command(name="list")
@pass_ctx
def list_users(ctx):
    """Display users"""
    data = [["Username"]]
    users = _get_users()

    for user in users:
        data.append([user.username])

    table = AsciiTable(data)
    table.inner_row_border = True
    click.echo(table.table)


@user.command(name="create")
@click.argument("username")
@click.password_option()
@pass_ctx
def create_user(ctx, username, password):
    """Create user"""
    user = User(username=username, password=generate_password_hash(password))
    user.save()


@user.command(name="update")
@click.argument("username")
@click.password_option()
@pass_ctx
def update_user(ctx, username, password):
    """Update user"""
    user = User(username=username, password=generate_password_hash(password))
    try:
        user.update()
    except UserNotFound as e:
        click.echo(str(e))


@user.command(name="delete")
@click.argument("username")
@pass_ctx
def delete_user(ctx, username):
    """delete user"""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f"User {username} not found")
        return

    user.delete()
