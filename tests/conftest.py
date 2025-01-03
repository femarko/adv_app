import datetime

import pytest
import sqlalchemy

import app.pass_hashing
from app import adv, models


@pytest.fixture(scope="session")
def engine():
    return sqlalchemy.create_engine(models.POSTGRES_DSN)


@pytest.fixture
def session_maker(engine):
    return sqlalchemy.orm.sessionmaker(bind=engine)


@pytest.fixture(scope="session")
def drop_all_create_all(engine):
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)


@pytest.fixture
def test_client():
    return adv.test_client()


@pytest.fixture
def app_context():
    from app import adv
    return adv.app_context()


@pytest.fixture
def access_token(session_maker, app_context, test_client, create_test_users_and_advs) -> dict[str, str]:
    access_token_dict = {}
    for i in range(1000, 1002):
        login_response = test_client.post(
            "http://127.0.0.1:5000/login/", json={"email": f"test_filter_{i}@email.com",
                                                  "password": f"test_filter_{i}_pass"}
        )
        login_response_json = login_response.json
        access_token_dict[f"user_{i}"] = login_response_json.get("access_token")
    return access_token_dict


@pytest.fixture
def test_date():
    return datetime.datetime(1900, 1, 1)


# @pytest.fixture
# def create_test_date_users(session_maker, test_date):
#     session = session_maker
#     with session() as sess:
#         for i in range(1000, 1002):
#             user = {"id": i,
#                     "name": f"test_filter_{i}",
#                     "email": f"test_filter_{i}@email.com",
#                     "password": f"test_filter_{i}_pass"}
#             sess.execute(sqlalchemy.text('INSERT INTO "user" (id, name, email, password, creation_date) '
#                                          'VALUES (:id, :name, :email, :password, :creation_date)'),
#                          dict(id=user["id"],
#                               name=user["name"],
#                               email=user["email"],
#                               password=user["email"],
#                               creation_date=test_date))
#             sess.commit()
#
#     yield
#
#     with session() as sess:
#         for i in range(1, 3):
#             sess.execute(sqlalchemy.text('DELETE FROM "user" WHERE (creation_date = :test_creation_date)'),
#                          dict(test_creation_date=test_date))
#             sess.commit()


@pytest.fixture
def create_test_users_and_advs(session_maker, test_date):
    session = session_maker
    with session() as sess:
        for i in range(1000, 1002):
            sess.execute(sqlalchemy.text('INSERT INTO "user" (id, name, email, password, creation_date) '
                                         'VALUES (:id, :name, :email, :password, :creation_date)'),
                         dict(id=i,
                              name=f"test_filter_{i}",
                              email=f"test_filter_{i}@email.com",
                              password=app.pass_hashing.hash_password(f"test_filter_{i}_pass"),
                              creation_date=test_date))
            sess.execute(sqlalchemy.text('INSERT INTO "adv" (id, title, description, creation_date, user_id) '
                                         'VALUES (:id, :title, :description, :creation_date, :user_id)'),
                         dict(id=i,
                              title=f"test_filter_{i}",
                              description=f"test_filter_{i}",
                              creation_date=test_date,
                              user_id=i))
            sess.execute(sqlalchemy.text('INSERT INTO "adv" (id, title, description, creation_date, user_id) '
                                         'VALUES (:id, :title, :description, :creation_date, :user_id)'),
                         dict(id=i+3,
                              title=f"test_filter_{i+3}",
                              description=f"test_filter_{i+3}",
                              creation_date=test_date,
                              user_id=i))
            sess.commit()
    yield
    with session() as sess:
        sess.execute(sqlalchemy.text('DELETE FROM "adv" WHERE (creation_date = :creation_date)'),
                     dict(creation_date=test_date))
        sess.execute(sqlalchemy.text('DELETE FROM "user" WHERE (creation_date = :creation_date)'),
                     dict(creation_date=test_date))
        sess.commit()
