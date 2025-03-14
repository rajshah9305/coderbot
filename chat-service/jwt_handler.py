import os
import jwt
from datetime import datetime, timedelta

class JWTHandler:
    @staticmethod
    def create_token(user_id, username, role):
        payload = {
            "id": user_id,
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}