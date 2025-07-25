from fastapi import FastAPI, HTTPException, Depends, Header
from db import user_collection, redis_client
from models import UserRegister, UserLogin, UserOut
from auth import hash_password, verify_password, create_session_id
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/register")
def register(user: UserRegister):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_data = user.dict()
    user_data["password"] = hash_password(user_data["password"])
    user_collection.insert_one(user_data)
    return {"message": "Registration successful"}

@app.post("/login")
def login(data: UserLogin):
    user = user_collection.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_id = create_session_id()
    redis_client.setex(f"session:{session_id}", 3600, user["email"])
    return {"message": "Login successful", "session_id": session_id}

def get_current_email(session_id: str = Header(...)):
    email = redis_client.get(f"session:{session_id}")
    if not email:
        raise HTTPException(status_code=403, detail="Invalid or expired session")
    return email

@app.get("/profile", response_model=UserOut)
def profile(email: str = Depends(get_current_email)):
    cached = redis_client.get(f"profile:{email}")
    if cached:
        return json.loads(cached)
    
    user = user_collection.find_one({"email": email}, {"_id": 0, "name": 1, "email": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    redis_client.setex(f"profile:{email}", 60, json.dumps(user))
    return user
