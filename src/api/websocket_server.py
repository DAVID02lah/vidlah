"""
WebSocket Server for Real-time Communication with Frontend
"""

import logging
import asyncio
import json
from typing import Set, Dict, Any
import websockets
from websockets.server import WebSocketServerProtocol

from ..config.settings import Settings

class WebSocketServer:
    """WebSocket server for real-time communication"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Connected clients
        self.clients: Set[WebSocketServerProtocol] = set()
        
        # Server instance
        self.server = None
        
    async def start(self):
        """Start WebSocket server"""
        try:
            self.server = await websockets.serve(
                self.handle_client,
                "localhost",
                self.settings.WEBSOCKET_PORT
            )
            
            self.logger.info(f"WebSocket server started on port {self.settings.WEBSOCKET_PORT}")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def stop(self):
        """Stop WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("WebSocket server stopped")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        self.clients.add(websocket)
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        self.logger.info(f"Client connected from {client_ip} (total: {len(self.clients)})")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'welcome',
                'message': 'Connected to AI Trading Overlay System'
            }))
            
            # Handle incoming messages
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client {client_ip} disconnected")
        except Exception as e:
            self.logger.error(f"Client handler error: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))
            
            elif message_type == 'set_capture_region':
                # Handle capture region update
                region = data.get('region', {})
                await self.handle_capture_region_update(region)
            
            elif message_type == 'request_analysis':
                # Handle analysis request
                await self.handle_analysis_request(websocket, data)
            
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON received from client")
        except Exception as e:
            self.logger.error(f"Message handling error: {e}")
    
    async def handle_capture_region_update(self, region: Dict):
        """Handle capture region update from frontend"""
        self.logger.info(f"Updating capture region: {region}")
        # This would update the screen capture settings
        # Implementation depends on how you want to handle this
    
    async def handle_analysis_request(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle analysis request from client"""
        try:
            # Send immediate response
            await websocket.send(json.dumps({
                'type': 'analysis_response',
                'status': 'processing',
                'message': 'Analysis request received'
            }))
            
        except Exception as e:
            self.logger.error(f"Analysis request error: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        # Remove disconnected clients
        disconnected = set()
        
        for client in self.clients.copy():
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                self.logger.error(f"Broadcast error to client: {e}")
                disconnected.add(client)
        
        # Clean up disconnected clients
        self.clients -= disconnected
        
        if disconnected:
            self.logger.info(f"Removed {len(disconnected)} disconnected clients")
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
        except Exception as e:
            self.logger.error(f"Send to client error: {e}")
    
    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.clients)
