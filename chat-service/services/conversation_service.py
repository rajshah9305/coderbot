from typing import List, Dict, Optional
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "coding_assistant")
        
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            self.db = self.client[db_name]
            self.conversations = self.db.conversations
            logger.info(f"Connected to MongoDB at {mongo_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def create_conversation(self, user_id: str) -> str:
        """Create a new conversation for a user and return its ID"""
        try:
            conversation = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "title": "New Conversation",
                "messages": []
            }
            result = self.conversations.insert_one(conversation)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict]:
        """Get a conversation by ID and user ID"""
        try:
            obj_id = ObjectId(conversation_id)
            conversation = self.conversations.find_one({"_id": obj_id, "user_id": user_id})
            if conversation:
                conversation["_id"] = str(conversation["_id"])  # Convert ObjectId to string
            return conversation
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return None

    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        try:
            conversations = list(self.conversations.find(
                {"user_id": user_id},
                {"messages": 0}  # Exclude messages for performance
            ).sort("updated_at", -1))  # Sort by most recent
            
            # Convert ObjectId to string
            for conv in conversations:
                conv["_id"] = str(conv["_id"])
            
            return conversations
        except Exception as e:
            logger.error(f"Error retrieving user conversations: {str(e)}")
            return []

    def add_message(self, conversation_id: str, user_id: Optional[str], message: Dict) -> bool:
        """Add a message to a conversation"""
        try:
            obj_id = ObjectId(conversation_id)
            message_with_meta = {
                **message,
                "timestamp": datetime.now(),
                "is_user": user_id is not None
            }
            result = self.conversations.update_one(
                {"_id": obj_id},
                {
                    "$push": {"messages": message_with_meta},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            # Update conversation title if it's the first user message
            if user_id and message.get("role") == "user":
                conversation = self.conversations.find_one({"_id": obj_id})
                if conversation and len(conversation.get("messages", [])) <= 1:
                    title = message.get("content", "")[:30]
                    if len(title) == 30:
                        title += "..."
                    self.conversations.update_one(
                        {"_id": obj_id},
                        {"$set": {"title": title}}
                    )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return False

    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update the title of a conversation"""
        try:
            obj_id = ObjectId(conversation_id)
            result = self.conversations.update_one(
                {"_id": obj_id},
                {"$set": {"title": title}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating conversation title: {str(e)}")
            return False

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        try:
            obj_id = ObjectId(conversation_id)
            result = self.conversations.delete_one({"_id": obj_id, "user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False