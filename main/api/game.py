from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from main.utils.db import get_db, User, HousieNumber, TreasureHunt, get_user_by_username, encrypt_answer
from main.utils.websocket_manager import manager
from typing import List
import json
from datetime import datetime

router = APIRouter()

# WebSocket endpoint for real-time updates
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, connection_type: str = "general"):
    await manager.connect(websocket, connection_type)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, connection_type)

# WebSocket endpoint for leaderboard updates
@router.websocket("/ws/leaderboard")
async def websocket_leaderboard(websocket: WebSocket):
    await manager.connect(websocket, "leaderboard")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "leaderboard")

# WebSocket endpoint for board updates
@router.websocket("/ws/board")
async def websocket_board(websocket: WebSocket):
    await manager.connect(websocket, "board")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "board")

# API endpoints for game data
@router.get("/api/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    """Get current leaderboard (excludes admin users and soft-deleted users)"""
    users = db.query(User).filter(User.role != "admin", User.is_deleted == 0).order_by(desc(User.points)).all()
    leaderboard = []
    for i, user in enumerate(users, 1):
        leaderboard.append({
            "rank": i,
            "username": user.username,
            "real_name": user.real_name,
            "profile_photo": user.profile_photo,
            "points": user.points
        })
    return {"leaderboard": leaderboard}

@router.get("/api/board")
async def get_board(db: Session = Depends(get_db)):
    """Get current game board state"""
    # Get all drawn numbers
    drawn_numbers = db.query(HousieNumber).order_by(HousieNumber.id).all()
    numbers = [num.number_drawn for num in drawn_numbers]
    
    # Get current number (last drawn)
    current_number = numbers[-1] if numbers else None
    
    return {
        "current_number": current_number,
        "drawn_numbers": numbers,
        "total_drawn": len(numbers)
    }

@router.post("/api/draw-number")
async def draw_number(request: dict, db: Session = Depends(get_db)):
    """Draw a new number (admin only)"""
    number = request.get("number")
    if not number:
        raise HTTPException(status_code=400, detail="Number is required")
    
    if number < 1 or number > 90:
        raise HTTPException(status_code=400, detail="Number must be between 1 and 90")
    
    # Check if number already drawn
    existing = db.query(HousieNumber).filter(HousieNumber.number_drawn == number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Number already drawn")
    
    # Add new number
    new_number = HousieNumber(number_drawn=number)
    db.add(new_number)
    db.commit()
    db.refresh(new_number)
    
    # Broadcast to all board connections
    await manager.broadcast_board({
        "current_number": number,
        "drawn_numbers": [n.number_drawn for n in db.query(HousieNumber).order_by(HousieNumber.id).all()]
    })
    
    return {"message": f"Number {number} drawn successfully", "number": number}

@router.get("/api/users")
async def get_users(db: Session = Depends(get_db)):
    """Get all users (including admins and soft-deleted users for admin panel)"""
    users = db.query(User).order_by(User.username).all()
    return {"users": [
        {
            "user_id": user.user_id,
            "username": user.username,
            "real_name": user.real_name,
            "profile_photo": user.profile_photo,
            "points": user.points,
            "role": user.role,
            "is_deleted": user.is_deleted
        } for user in users
    ]}

@router.get("/api/users/non-admin")
async def get_non_admin_users(db: Session = Depends(get_db)):
    """Get only non-admin users for points allocation (excludes soft-deleted users)"""
    users = db.query(User).filter(User.role != "admin", User.is_deleted == 0).order_by(User.username).all()
    return {"users": [
        {
            "user_id": user.user_id,
            "username": user.username,
            "real_name": user.real_name,
            "profile_photo": user.profile_photo,
            "points": user.points,
            "role": user.role
        } for user in users
    ]}

@router.post("/api/update-points")
async def update_points(request: dict, db: Session = Depends(get_db)):
    """Update user points (admin only)"""
    user_id = request.get("user_id")
    points = request.get("points")
    
    if not user_id or not points:
        raise HTTPException(status_code=400, detail="user_id and points are required")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent giving points to admin users
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot give points to admin users")
    
    user.points += points
    db.commit()
    
    # Broadcast leaderboard update
    await manager.broadcast_leaderboard(await get_leaderboard_data(db))
    
    return {"message": f"Added {points} points to {user.real_name}", "user": user.real_name, "new_points": user.points}

@router.delete("/api/delete-user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Soft delete user (admin only)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete - mark as deleted instead of removing
    user.is_deleted = 1
    db.commit()
    
    # Broadcast leaderboard update
    await manager.broadcast_leaderboard(await get_leaderboard_data(db))
    
    return {"message": f"User {user.real_name} deleted successfully"}

@router.post("/api/restore-user/{user_id}")
async def restore_user(user_id: int, db: Session = Depends(get_db)):
    """Restore soft-deleted user (admin only)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Restore user - mark as active
    user.is_deleted = 0
    db.commit()
    
    # Broadcast leaderboard update
    await manager.broadcast_leaderboard(await get_leaderboard_data(db))
    
    return {"message": f"User {user.real_name} restored successfully"}

@router.delete("/api/clear-numbers")
async def clear_numbers(db: Session = Depends(get_db)):
    """Clear all drawn numbers (admin only)"""
    db.query(HousieNumber).delete()
    db.commit()
    
    # Broadcast board update
    await manager.broadcast_board({
        "current_number": None,
        "drawn_numbers": []
    })
    
    return {"message": "All numbers cleared successfully"}

@router.post("/api/refresh-avatars")
async def refresh_avatars(db: Session = Depends(get_db)):
    """Refresh all user avatars based on their gender"""
    try:
        from main.utils.db import update_existing_user_avatars
        update_existing_user_avatars()
        return {"message": "Avatars refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing avatars: {str(e)}")

async def get_leaderboard_data(db: Session):
    """Helper function to get leaderboard data (excludes admin users and soft-deleted users)"""
    users = db.query(User).filter(User.role != "admin", User.is_deleted == 0).order_by(desc(User.points)).all()
    leaderboard = []
    for i, user in enumerate(users, 1):
        leaderboard.append({
            "rank": i,
            "username": user.username,
            "real_name": user.real_name,
            "profile_photo": user.profile_photo,
            "points": user.points
        })
    return {"leaderboard": leaderboard}

# Treasure Hunt API endpoints

@router.get("/api/treasure-hunt/current")
async def get_current_question(request: Request, db: Session = Depends(get_db)):
    """Get the current treasure hunt hint that needs to be solved"""
    # Find the next unanswered treasure hunt (answered_by = 0)
    next_treasure = db.query(TreasureHunt).filter(TreasureHunt.answered_by == 0).order_by(TreasureHunt.id).first()
    
    if not next_treasure:
        return {
            "treasure": None,
            "message": "No more treasure hunts available!"
        }
    
    # Encrypt hint on the fly (hints are always shown)
    encrypted_hint = encrypt_answer(next_treasure.hint)
    
    return {
        "treasure": {
            "id": next_treasure.id,
            "hint": next_treasure.hint,
            "encrypted_hint": encrypted_hint,
            "is_answered": next_treasure.answered_by != 0
        }
    }

@router.post("/api/treasure-hunt/submit")
async def submit_treasure_answer(request: Request, db: Session = Depends(get_db)):
    """Submit a treasure hunt answer"""
    # Parse JSON body
    body = await request.json()
    answer = body.get("answer", "").strip()
    if not answer:
        raise HTTPException(status_code=400, detail="Answer is required")
    
    # Remove hyphens/dashes and make case-insensitive
    answer = answer.replace("-", "").replace("_", "").upper()
    
    # Get user from cookie
    username = request.cookies.get('username')
    if not username:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find the next unanswered treasure hunt (answered_by = 0)
    next_treasure = db.query(TreasureHunt).filter(TreasureHunt.answered_by == 0).order_by(TreasureHunt.id).first()
    
    if not next_treasure:
        return {
            "message": "No more treasure hunts available!",
            "is_correct": False,
            "treasure_id": None
        }
    
    # Check if answer matches (already normalized to uppercase)
    is_correct = answer == next_treasure.answer.upper()
    
    if is_correct:
        # Update the treasure hunt with user's answer
        next_treasure.answered_by = user.user_id
        
        # Award points to user
        points_awarded = 10
        user.points += points_awarded
        
        db.commit()
        
        # Broadcast leaderboard update
        await manager.broadcast_leaderboard(await get_leaderboard_data(db))
        
        return {
            "message": f"Correct answer! You earned {points_awarded} points!",
            "is_correct": True,
            "treasure_id": next_treasure.id,
            "points_awarded": points_awarded
        }
    else:
        return {
            "message": "Incorrect answer. Try again!",
            "is_correct": False,
            "treasure_id": next_treasure.id
        }

