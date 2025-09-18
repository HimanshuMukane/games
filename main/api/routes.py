from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from main.utils.db import get_db, get_user_by_username, create_user, verify_admin_access
from main.utils.config import settings
import secrets

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get current user from cookie"""
    username = request.cookies.get('username')
    if not username:
        return None
    
    user = get_user_by_username(db, username)
    return user

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Home page - treasure hunt"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request, db: Session = Depends(get_db)):
    """Leaderboard page"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("leaderboard.html", {"request": request, "user": user})

@router.get("/board", response_class=HTMLResponse)
async def board(request: Request, db: Session = Depends(get_db)):
    """Game board page"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("board.html", {"request": request, "user": user})

@router.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db)):
    """Admin panel"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not verify_admin_access(db, user.username):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/api/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """Handle login/registration"""
    form_data = await request.form()
    username = form_data.get("username", "").strip()
    real_name = form_data.get("real_name", "").strip()
    gender = form_data.get("gender", "male").strip().lower()
    
    if not username:
        return RedirectResponse(url="/login?error=missing_username", status_code=302)
    
    # Validate gender
    if gender not in ["male", "female"]:
        gender = "male"
    
    # If real_name is not provided, use username as real_name
    if not real_name:
        real_name = username
    
    # Check if user exists
    user = get_user_by_username(db, username)
    if not user:
        # Check if new registrations are allowed
        if not settings.ALLOW_NEW_REGISTRATIONS:
            return RedirectResponse(url="/login?error=registration_disabled", status_code=302)
        
        # Create new user with role="user" and gender
        user = create_user(db, username, real_name, gender, "user")
    else:
        # Update existing user's real_name and gender if provided
        if real_name and real_name != user.real_name:
            user.real_name = real_name
        if gender != user.gender:
            user.gender = gender
        db.commit()
        db.refresh(user)
    
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # Create response with redirect
    response = RedirectResponse(url="/", status_code=302)
    
    # Set cookies
    response.set_cookie(
        key="username", 
        value=user.username, 
        max_age=86400,  # 24 hours
        httponly=False,  # Allow JavaScript access
        secure=False,    # For development
        samesite="lax"
    )
    response.set_cookie(
        key="user_role", 
        value=user.role, 
        max_age=86400,
        httponly=False,
        secure=False,
        samesite="lax"
    )
    response.set_cookie(
        key="real_name", 
        value=user.real_name, 
        max_age=86400,
        httponly=False,
        secure=False,
        samesite="lax"
    )
    response.set_cookie(
        key="session_token", 
        value=session_token, 
        max_age=86400,
        httponly=False,
        secure=False,
        samesite="lax"
    )
    
    return response

@router.post("/api/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(url="/login", status_code=302)
    
    # Clear cookies
    response.delete_cookie("username")
    response.delete_cookie("user_role")
    response.delete_cookie("real_name")
    response.delete_cookie("session_token")
    
    return response
