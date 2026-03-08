from typing import List
from fastmcp import FastMCP
from pydantic import BaseModel
from fastapi import HTTPException, status
from auth import sign_in, get_current_user, supabase
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

class Session(BaseModel):
    session_id: str

class CartItem(BaseModel):
    item: str
    quantity: int

class Cart(BaseModel):
    session_id: str
    items: List[CartItem]

@app.tool
def create_cart() -> Session:
    """
    Creates a new persistent shopping session in Supabase and returns a session ID.
    """
    try:
        response = supabase.table("sessions").insert({"state": {"items": []}}).execute()
        
        if response.data:
            session_id = response.data[0]['id']
            print(f"New cart session created in Supabase: {session_id}")
            return Session(session_id=session_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to create the session in the database.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.tool
def add_to_cart(session_id: str, item: str, quantity: int) -> Cart:
    """
    Adds an item to a shopping cart, updating the state in Supabase.
    """
    try:
        response = supabase.table("sessions").select("state").eq("id", session_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found.")
        
        current_state = response.data[0]['state']
        cart_items = current_state.get("items", [])
        
        found = False
        for cart_item in cart_items:
            if cart_item["item"] == item:
                cart_item["quantity"] += quantity
                found = True
                break
        if not found:
            cart_items.append({"item": item, "quantity": quantity})
            
        new_state = {"items": cart_items}
        update_response = supabase.table("sessions").update({"state": new_state}).eq("id", session_id).execute()

        if not update_response.data:
            raise HTTPException(status_code=500, detail="Failed to update the cart in the database.")

        print(f"Item added to cart {session_id}: {quantity}x {item}")
        return Cart(session_id=session_id, items=[CartItem(**i) for i in cart_items])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.tool
def view_cart(session_id: str) -> Cart:
    """
    Returns the contents of a cart by querying its state in Supabase.
    """
    try:
        response = supabase.table("sessions").select("state").eq("id", session_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found.")
            
        current_state = response.data[0]['state']
        cart_items = current_state.get("items", [])
        print(f"Viewing cart {session_id} from Supabase")
        return Cart(session_id=session_id, items=[CartItem(**i) for i in cart_items])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


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