from werkzeug.security import generate_password_hash, check_password_hash

from director.models.users import User


def test_crud(app, client, no_worker):
    # Create user
    user = User(username="test_user", password=generate_password_hash("root_test1"))
    user.save()

    # Read user
    user = User.query.filter_by(username="test_user").first()
    assert user.username == "test_user"
    assert check_password_hash(user.password, "root_test1")

    # Update user
    user.password = generate_password_hash("root_test2")
    user.update()

    user = User.query.filter_by(username="test_user").first()
    assert check_password_hash(user.password, "root_test2")

    # Delete user
    user.delete()

    user = User.query.filter_by(username="test_user").first()
    assert user == None
