from fastapi import WebSocket
from typing import List
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        # Store leaderboard connections separately
        self.leaderboard_connections: List[WebSocket] = []
        # Store board connections separately  
        self.board_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, connection_type: str = "general"):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if connection_type == "leaderboard":
            self.leaderboard_connections.append(websocket)
        elif connection_type == "board":
            self.board_connections.append(websocket)
            
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, connection_type: str = "general"):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.leaderboard_connections:
            self.leaderboard_connections.remove(websocket)
        if websocket in self.board_connections:
            self.board_connections.remove(websocket)
            
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast_leaderboard(self, data: dict):
        """Broadcast leaderboard updates to all leaderboard connections"""
        if not self.leaderboard_connections:
            return
            
        message = json.dumps({
            "type": "leaderboard_update",
            "data": data
        })
        
        # Send to all leaderboard connections
        disconnected = []
        for connection in self.leaderboard_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to leaderboard connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn, "leaderboard")

    async def broadcast_board(self, data: dict):
        """Broadcast board updates to all board connections"""
        if not self.board_connections:
            return
            
        message = json.dumps({
            "type": "board_update", 
            "data": data
        })
        
        # Send to all board connections
        disconnected = []
        for connection in self.board_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to board connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn, "board")

    async def broadcast_to_all(self, data: dict):
        """Broadcast to all active connections"""
        if not self.active_connections:
            return
            
        message = json.dumps(data)
        
        # Send to all connections
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

# Global connection manager instance
manager = ConnectionManager()
