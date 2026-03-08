from fastmcp import FastMCP
from pydantic import BaseModel
from fastapi import HTTPException, status
from auth import sign_in, get_current_user
from fastmcp.server.dependencies import get_http_headers

app = FastMCP("My Advanced Tool Catalog")

class UserProfile(BaseModel):
  """Represents a structured user profile."""
  user_id: str
  username: str
  email: str
  is_active: bool

class Token(BaseModel):
   access_token: str
   token_type: str

@app.tool()
async def start_session(email: str, password: str) -> Token:
    """Start a session and return an access token."""
    token_str = await sign_in(email, password)
    return Token(access_token=token_str, token_type="bearer")

@app.tool()
def search_news(query: str, limit: int = 10):
  """Searches for news about a specific topic.

  Args:
    query: The topic to search for.
    limit: The maximum number of results to return.
    """
  print(f"Searching for {limit} news articles about '{query}'...")
  return [f"News {i+1} about {query}" for i in range(limit)]

@app.tool()
async def get_user_profile() -> UserProfile:
    """Get the authenticated user's profile by reading the token from the header."""

    auth_header = get_http_headers().get("auth")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header with Bearer token",
        )

    token = auth_header.split(" ")[1]
    current_user = await get_current_user(token)

    user_id = current_user.get("sub")
    email = current_user.get("email", f"{user_id}@example.com")

    return UserProfile(
        user_id=user_id,
        username=f"user_{user_id[:6]}",
        email=email,
        is_active=True,
    )

@app.tool()
def divide(a: float, b: float) -> float:
  """Divides two numbers. Fails if the divisor is zero."""
  print(f"Attempting to divide {a} / {b}...")
  if b == 0:
      raise ValueError("Cannot divide by zero.")
  return a / b

if __name__ == "__main__":
    # app.run()
    app.run(transport="http", host="127.0.0.1", port=8000)