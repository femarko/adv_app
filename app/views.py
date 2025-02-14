from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required

import app.errors
import app.repository.filtering
from app import adv, models, pass_hashing, validation, service_layer, authentication
from app.error_handlers import HttpError

from app.unit_of_work import UnitOfWork


@adv.route("/users/<int:user_id>/", methods=["GET"])
@jwt_required()
def get_user_data(user_id: int) -> tuple[Response, int]:
    try:
        user_data: dict = service_layer.get_user_data(
            user_id=user_id, check_current_user_func=authentication.check_current_user, uow=UnitOfWork()
        )
        return jsonify(user_data), 200
    except app.errors.CurrentUserError as e:
        raise HttpError(status_code=403, description=e.message)
    except app.errors.NotFoundError as e:
        raise HttpError(status_code=404, description=e.message)


@adv.route("/users/", methods=["POST"])
def create_user():
    try:
        new_user_id: int = service_layer.create_user(
            user_data=request.json, validate_func=validation.validate_data_for_user_creation,
            hash_pass_func=pass_hashing.hash_password, uow=UnitOfWork()
        )
        return jsonify({"user_id": new_user_id}), 201
    except app.errors.ValidationError as e:
        raise HttpError(status_code=400, description=str(e))
    except app.errors.AlreadyExistsError as e:
        raise HttpError(status_code=409, description=f"A user {e.message}")


@adv.route("/users/<int:user_id>/", methods=["PATCH"])
@jwt_required()
def update_user(user_id: int):
    try:
        updated_user_data: dict = service_layer.update_user(
            user_id=user_id, check_current_user_func=authentication.check_current_user,
            validate_func=validation.validate_data_for_user_updating, hash_pass_func=pass_hashing.hash_password,
            new_data=request.json, uow=UnitOfWork()
        )
        return jsonify({"modified_data": updated_user_data}), 200
    except app.errors.CurrentUserError as e:
        raise HttpError(status_code=403, description=e.message)
    except app.errors.ValidationError as e:
        raise HttpError(status_code=400, description=str(e))


@adv.route("/users/<int:user_id>/advertisements", methods=["GET"])
@jwt_required()
def get_related_advs(user_id: int):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    try:
        result = service_layer.get_related_advs(
            authenticated_user_id=user_id,  # todo: why I called this param "authenticated_user_id"?
            check_current_user_func=authentication.check_current_user,
            page=page,
            per_page=per_page,
            uow=UnitOfWork()
        )
        return result, 200
    except app.errors.CurrentUserError:
        raise HttpError(status_code=403, description="Unavailable operation.")
    except app.errors.ValidationError as e:
        raise HttpError(status_code=400, description=str(e))
    except app.errors.NotFoundError as e:
        raise HttpError(status_code=404, description=e.message)


@adv.route("/users/<int:user_id>/", methods=["DELETE"])
@jwt_required()
def delete_user(user_id: int):
    try:
        deleted_user_params: dict[str, str | int] = service_layer.delete_user(
            user_id=user_id, check_current_user_func=authentication.check_current_user, uow=UnitOfWork()
        )
        return jsonify({"deleted_user_params": deleted_user_params}), 200
    except app.errors.CurrentUserError:
        raise HttpError(status_code=403, description="Unavailable operation.")


@adv.route("/advertisements/<int:adv_id>/", methods=["GET"])
@jwt_required()
def get_adv_params(adv_id: int):
    try:
        adv_params: dict[str, str | int] = service_layer.get_adv_params(
            adv_id=adv_id, check_current_user_func=authentication.check_current_user, uow=UnitOfWork()
        )
        return adv_params, 200
    except app.errors.CurrentUserError as e:
        raise HttpError(status_code=403, description=e.message)
    except app.errors.NotFoundError as e:
        raise HttpError(status_code=404, description=e.message)


@adv.route("/advertisements/", methods=["POST"])
@jwt_required()
def create_adv():
    try:
        new_adv_id: int = service_layer.create_adv(
            get_auth_user_id_func=authentication.get_authenticated_user_identity,
            validate_func=validation.validate_data_for_adv_creation, adv_params=request.json, uow=UnitOfWork()
        )
        return jsonify({'new_advertisement_id': new_adv_id}), 201
    except app.errors.CurrentUserError as e:
        raise HttpError(status_code=403, description=e.message)
    except app.errors.ValidationError as e:
        raise HttpError(status_code=400, description=str(e))


@adv.route("/advertisements/<int:adv_id>/", methods=["PATCH"])
@jwt_required()
def update_adv(adv_id: int):
    try:
        updated_adv_params: dict [str, str | int] = service_layer.update_adv(
            adv_id=adv_id, new_params=request.json, check_current_user_func=authentication.check_current_user,
            validate_func=validation.validate_data_for_adv_updating, uow=UnitOfWork())
    except app.errors.NotFoundError as e:
        raise HttpError(status_code=404, description=e.message)
    except app.errors.CurrentUserError as e:
        raise HttpError(status_code=403, description=e.message)
    except app.errors.ValidationError as e:
        raise HttpError(status_code=400, description=str(e))
    return {"updated_adv_params": updated_adv_params}, 200


@adv.route("/advertisements", methods=["GET"])
def search_advs_by_text():
    try:
        paginated_result: dict[str, str | int] = service_layer.search_advs_by_text(
            column=request.args.get("column"),
            column_value=request.args.get("column_value"),
            uow=UnitOfWork(),
            page=request.args.get("page"),
            per_page=request.args.get("per_page")
        )
    except app.errors.ValidationError as e:
        raise HttpError(status_code=400, description=str(e.message))
    return paginated_result, 200


@adv.route("/advertisements/<int:adv_id>/", methods=["DELETE"])
@jwt_required()
def delete_adv(adv_id: int):
    try:
        deleted_adv_params: dict[str, str | int] = service_layer.delete_adv(
            adv_id=adv_id, get_auth_user_id_func=authentication.get_authenticated_user_identity, uow=UnitOfWork()
        )
    except app.errors.CurrentUserError as e:
        raise HttpError(status_code=403, description=e.message)
    except app.errors.NotFoundError as e:
        raise HttpError(status_code=404, description=e.message)
    return {"deleted_advertisement_params": deleted_adv_params}, 200


@adv.route("/login/", methods=["POST"])
def login():
    try:
        access_token = service_layer.jwt_auth(validate_func=validation.validate_login_credentials,
                                              check_pass_func=pass_hashing.check_password,
                                              grant_access_func=authentication.get_access_token,
                                              credentials=request.json,
                                              uow=UnitOfWork())
        return jsonify({"access_token": access_token}), 200
    except app.errors.AccessDeniedError as e:
        raise HttpError(status_code=401, description=e.message)
    except app.errors.ValidationError as e:
        raise HttpError(status_code=400, description=str(e))
