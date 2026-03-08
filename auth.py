from supabase import create_client, Client
from fastapi import HTTPException, status
from jose import jwt, JWTError
from config import SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, JWKS_URL, ISSUER
import requests

supabase: Client = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)

def get_jwk_for_kid(kid: str):
    jwks = requests.get(JWKS_URL).json()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Public key not found for this token",
    )

async def sign_in(email: str, password: str) -> str:
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            return response.session.access_token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {e}",
        )

async def get_current_user(token: str):
    try:
        header = jwt.get_unverified_header(token)
        jwk = get_jwk_for_kid(header["kid"])
        payload = jwt.decode(
            token,
            jwk,
            algorithms=[header["alg"]],
            audience="authenticated",
            issuer=ISSUER
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return payload
    except JWTError as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )