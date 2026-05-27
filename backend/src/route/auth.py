from fastapi import APIRouter, Depends, Request
from src.service.user import UserService
from src.service.google import google_service
from src.core.dependency import get_user_service
from src.utils.response import success
from src.utils.log import get_logger

logger = get_logger(__name__)

auth_route = APIRouter(prefix="/auth")


@auth_route.get("/login")
async def oauth_login():
    url = google_service.login_with_google()
    return success(data={"url": url})


@auth_route.get("/callback")
async def oauth(request: Request, user_service: UserService = Depends(get_user_service)):
    params = dict(request.query_params)
    logger.info(f"query_params; {params}")
    data = google_service.handle_callback(request)
    user_data = google_service.verify_id(data["id_token"])
    user_info = {
        "google_id": user_data["sub"],
        "refresh_token": data["refresh_token"],
        "access_token": data["access_token"],
        "email": user_data["email"],
        "oauth_verified": True,
        "onboarded": True,
        "email_verified": user_data["email_verified"],
        "name": user_data["name"],
        "picture": user_data.get("picture"),
        "first_name": user_data.get("given_name"),
        "last_name": user_data.get("family_name"),
    }
    logger.info(f"user_data: {user_info}")

    existing_user = await user_service.get_user_by_email(email=user_info["email"])

    if existing_user:
        if existing_user.get("email") == user_info["email"]:
            updated_user = await user_service.update_user(
                email=existing_user["email"], update_data=user_info
            )
            logger.info(f"user updated: {updated_user}")
            return success(message="user_updated", data=updated_user)
        else:
            logger.warning("Email mismatch for existing user.")
            return success(message="email_mismatch")
    else:
        new_user = await user_service.create_user(**user_info)
        logger.info(f"new_user: {new_user}")
        return success(message="user_created", data=new_user)
