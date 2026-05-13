import time
import requests
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

_JWKS_CACHE = {"keys": None, "fetched": 0}


def _get_jwks():
    ttl = int(getattr(settings, "CLERK_JWKS_CACHE_TTL", 3600))
    if _JWKS_CACHE["keys"] and time.time() - _JWKS_CACHE["fetched"] < ttl:
        return _JWKS_CACHE["keys"]
    resp = requests.get(settings.CLERK_JWKS_URL, timeout=5)
    resp.raise_for_status()
    jwks = resp.json()
    _JWKS_CACHE.update({"keys": jwks, "fetched": time.time()})
    return jwks


class ClerkAuthMiddleware:
    """Middleware to validate Clerk-issued JWTs and attach/create a user.

    Expects Authorization: Bearer <token> header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
        request.clerk_token = None
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1].strip()
            try:
                jwks = _get_jwks()
                unverified = jwt.get_unverified_header(token)
                kid = unverified.get("kid")
                key = next(k for k in jwks["keys"] if k.get("kid") == kid)
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                decode_kwargs = {
                    "algorithms": ["RS256"],
                    "options": {"verify_exp": True},
                }
                if getattr(settings, "CLERK_AUDIENCE", ""):
                    decode_kwargs["audience"] = settings.CLERK_AUDIENCE
                payload = jwt.decode(
                    token,
                    public_key,
                    **decode_kwargs,
                )
                User = get_user_model()
                clerk_id = payload.get("sub")
                email = payload.get("email") or (payload.get("email_addresses") or [{}])[0].get("email_address")
                if clerk_id:
                    user, created = User.objects.get_or_create(
                        clerk_id=clerk_id,
                        defaults={
                            "email": email or "",
                            "username": email or clerk_id,
                        },
                    )
                    request.user = user
                    request.clerk_token = payload
            except Exception:
                # Silently fail to avoid blocking unauthenticated endpoints
                request.clerk_token = None
        response = self.get_response(request)
        return response
