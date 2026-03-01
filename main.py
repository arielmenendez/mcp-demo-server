from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Literal

app = FastMCP("My Advanced Tool Catalog")

class UserProfile(BaseModel):
  """Represents a structured user profile."""
  user_id: str
  username: str
  email: str
  is_active: bool

@app.tool
def search_news(query: str, limit: int = 10):
  """Searches for news about a specific topic.

  Args:
    query: The topic to search for.
    limit: The maximum number of results to return.
    """
  print(f"Searching for {limit} news articles about '{query}'...")
  return [f"News {i+1} about {query}" for i in range(limit)]

@app.tool
def get_user_profile(user_id: str) -> UserProfile:
  """Retrieves a user's profile based on their ID."""
  print(f"Retrieving profile for user '{user_id}'...")
  return UserProfile(
    user_id=user_id,
    username=f"user_{user_id}",
    email=f"{user_id}@example.com",
    is_active=True
  )

@app.tool
def divide(a: float, b: float) -> float:
  """Divides two numbers. Fails if the divisor is zero."""
  print(f"Attempting to divide {a} / {b}...")
  if b == 0:
      raise ValueError("Cannot divide by zero.")
  return a / b

if __name__ == "__main__":
    app.run()