"""
Chat Application Implementation

Tests: Client-server architecture, sockets, state management, message routing

A simple chat application demonstrating:
- Client-server communication patterns
- Message broadcasting and routing
- Connection management
- Thread-safe state management
"""

from typing import Dict, List, Set, Optional
import threading
import queue
import time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Represents a chat message."""
    sender: str
    content: str
    timestamp: float
    room: str = "general"
    message_type: str = "text"  # text, system, private
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp,
            'room': self.room,
            'type': self.message_type
        }


class ChatRoom:
    """Represents a chat room with multiple participants."""
    
    def __init__(self, name: str):
        """
        Initialize chat room.
        
        Args:
            name: Room name
        """
        self.name = name
        self.participants: Set[str] = set()
        self.messages: List[Message] = []
        self.lock = threading.Lock()
    
    def add_participant(self, user_id: str):
        """Add a participant to the room."""
        with self.lock:
            self.participants.add(user_id)
    
    def remove_participant(self, user_id: str):
        """Remove a participant from the room."""
        with self.lock:
            self.participants.discard(user_id)
    
    def add_message(self, message: Message):
        """Add a message to the room history."""
        with self.lock:
            self.messages.append(message)
    
    def get_recent_messages(self, count: int = 50) -> List[Message]:
        """Get recent messages from the room."""
        with self.lock:
            return self.messages[-count:]
    
    def get_participant_count(self) -> int:
        """Get number of participants in the room."""
        with self.lock:
            return len(self.participants)


class ChatServer:
    """
    Chat server managing multiple rooms and clients.
    
    Features:
    - Multi-room support
    - Message broadcasting
    - Private messaging
    - Connection management
    - Message history
    """
    
    def __init__(self):
        """Initialize chat server."""
        self.rooms: Dict[str, ChatRoom] = {}
        self.clients: Dict[str, 'ChatClient'] = {}
        self.message_queue: queue.Queue = queue.Queue()
        self.lock = threading.Lock()
        self.running = False
        
        # Create default room
        self.create_room("general")
    
    def start(self):
        """Start the chat server."""
        self.running = True
        
        # Start message processor thread
        processor = threading.Thread(target=self._process_messages)
        processor.daemon = True
        processor.start()
    
    def stop(self):
        """Stop the chat server."""
        self.running = False
    
    def create_room(self, room_name: str) -> ChatRoom:
        """
        Create a new chat room.
        
        Args:
            room_name: Name of the room
            
        Returns:
            Created ChatRoom instance
        """
        with self.lock:
            if room_name not in self.rooms:
                self.rooms[room_name] = ChatRoom(room_name)
            return self.rooms[room_name]
    
    def register_client(self, client: 'ChatClient'):
        """Register a new client with the server."""
        with self.lock:
            self.clients[client.user_id] = client
            
        # Add to default room
        self.join_room(client.user_id, "general")
        
        # Send system message
        self.broadcast_message(
            Message(
                sender="system",
                content=f"{client.user_id} joined the chat",
                timestamp=time.time(),
                room="general",
                message_type="system"
            )
        )
    
    def unregister_client(self, user_id: str):
        """Unregister a client from the server."""
        with self.lock:
            if user_id in self.clients:
                # Remove from all rooms
                for room in self.rooms.values():
                    room.remove_participant(user_id)
                
                del self.clients[user_id]
        
        # Send system message
        self.broadcast_message(
            Message(
                sender="system",
                content=f"{user_id} left the chat",
                timestamp=time.time(),
                room="general",
                message_type="system"
            )
        )
    
    def join_room(self, user_id: str, room_name: str):
        """Add user to a chat room."""
        room = self.create_room(room_name)
        room.add_participant(user_id)
    
    def leave_room(self, user_id: str, room_name: str):
        """Remove user from a chat room."""
        with self.lock:
            if room_name in self.rooms:
                self.rooms[room_name].remove_participant(user_id)
    
    def send_message(self, message: Message):
        """Queue a message for processing."""
        self.message_queue.put(message)
    
    def broadcast_message(self, message: Message):
        """
        Broadcast message to all participants in a room.
        
        Args:
            message: Message to broadcast
        """
        with self.lock:
            if message.room in self.rooms:
                room = self.rooms[message.room]
                room.add_message(message)
                
                # Send to all participants in the room
                for user_id in room.participants:
                    if user_id in self.clients:
                        self.clients[user_id].receive_message(message)
    
    def send_private_message(self, sender: str, recipient: str, content: str):
        """
        Send a private message between two users.
        
        Args:
            sender: Sender user ID
            recipient: Recipient user ID
            content: Message content
        """
        message = Message(
            sender=sender,
            content=content,
            timestamp=time.time(),
            room=f"private-{sender}-{recipient}",
            message_type="private"
        )
        
        with self.lock:
            # Send to recipient if online
            if recipient in self.clients:
                self.clients[recipient].receive_message(message)
            
            # Send to sender (for confirmation)
            if sender in self.clients:
                self.clients[sender].receive_message(message)
    
    def _process_messages(self):
        """Background thread to process queued messages."""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1.0)
                
                if message.message_type == "private":
                    # Handle private message
                    pass
                else:
                    # Broadcast to room
                    self.broadcast_message(message)
                
            except queue.Empty:
                continue
    
    def get_room_list(self) -> List[dict]:
        """Get list of all chat rooms."""
        with self.lock:
            return [
                {
                    'name': name,
                    'participants': room.get_participant_count()
                }
                for name, room in self.rooms.items()
            ]


class ChatClient:
    """
    Chat client for connecting to chat server.
    
    Features:
    - Send and receive messages
    - Join/leave rooms
    - Private messaging
    - Local message buffer
    """
    
    def __init__(self, user_id: str, server: ChatServer):
        """
        Initialize chat client.
        
        Args:
            user_id: Unique user identifier
            server: ChatServer instance to connect to
        """
        self.user_id = user_id
        self.server = server
        self.inbox: queue.Queue = queue.Queue()
        self.current_room = "general"
        
        # Register with server
        self.server.register_client(self)
    
    def send_message(self, content: str, room: Optional[str] = None):
        """
        Send a message to a room.
        
        Args:
            content: Message content
            room: Room name (defaults to current room)
        """
        message = Message(
            sender=self.user_id,
            content=content,
            timestamp=time.time(),
            room=room or self.current_room
        )
        self.server.send_message(message)
    
    def send_private_message(self, recipient: str, content: str):
        """
        Send a private message to another user.
        
        Args:
            recipient: Recipient user ID
            content: Message content
        """
        self.server.send_private_message(self.user_id, recipient, content)
    
    def receive_message(self, message: Message):
        """
        Receive a message from the server.
        
        Args:
            message: Received message
        """
        self.inbox.put(message)
    
    def get_messages(self, timeout: float = 0.1) -> List[Message]:
        """
        Get received messages from inbox.
        
        Args:
            timeout: Timeout for waiting for messages
            
        Returns:
            List of received messages
        """
        messages = []
        try:
            while True:
                message = self.inbox.get(timeout=timeout)
                messages.append(message)
        except queue.Empty:
            pass
        return messages
    
    def join_room(self, room_name: str):
        """Join a chat room."""
        self.server.join_room(self.user_id, room_name)
        self.current_room = room_name
    
    def leave_room(self, room_name: str):
        """Leave a chat room."""
        self.server.leave_room(self.user_id, room_name)
    
    def disconnect(self):
        """Disconnect from the server."""
        self.server.unregister_client(self.user_id)


if __name__ == "__main__":
    print("Chat Application Example")
    print("=" * 60)
    
    # Create server
    server = ChatServer()
    server.start()
    
    # Create clients
    alice = ChatClient("Alice", server)
    bob = ChatClient("Bob", server)
    charlie = ChatClient("Charlie", server)
    
    # Wait for system messages to be processed
    time.sleep(0.1)
    
    # Send messages
    alice.send_message("Hello everyone!")
    bob.send_message("Hi Alice!")
    charlie.send_message("Hey there!")
    
    # Wait for messages to be processed
    time.sleep(0.1)
    
    # Retrieve messages
    print("\nAlice's inbox:")
    for msg in alice.get_messages():
        print(f"  [{msg.sender}]: {msg.content}")
    
    print("\nBob's inbox:")
    for msg in bob.get_messages():
        print(f"  [{msg.sender}]: {msg.content}")
    
    # Private message
    alice.send_private_message("Bob", "Hey Bob, this is private!")
    time.sleep(0.1)
    
    print("\nBob's private messages:")
    for msg in bob.get_messages():
        if msg.message_type == "private":
            print(f"  [Private from {msg.sender}]: {msg.content}")
    
    # Show room info
    print("\nChat rooms:")
    for room in server.get_room_list():
        print(f"  {room['name']}: {room['participants']} participants")
    
    # Cleanup
    server.stop()
