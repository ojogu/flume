from fastapi import APIRouter

public_route = APIRouter(tags=["public"])

# Future 3rd-party API endpoints go here.
# All routes in this router will appear in the public OpenAPI spec.
