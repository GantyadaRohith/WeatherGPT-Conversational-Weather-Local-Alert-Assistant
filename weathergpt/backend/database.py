"""
database.py
Unified Database Layer for WeatherGPT supporting:
1. MongoDB Atlas / Local MongoDB via Motor (AsyncIOMotorClient)
2. Zero-dependency Persistent JSON Document Store Fallback (weathergpt_db.json)

Ensures zero crashes when MongoDB is offline or credentials are not yet supplied.
Stores:
- saved_locations: Pinned hub locations with meteorological thresholds & subscriber contacts
- alert_dispatches: Audit trail of WhatsApp & Twilio SMS disaster notifications
- subscribers: Registered users for proactive weather & hazard dispatch
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Try importing motor
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False


DB_FILE_PATH = Path(__file__).parent.parent / "weathergpt_db.json"


class JSONDocumentStore:
    """Persistent local JSON document store mimicking MongoDB async collection queries."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._lock = asyncio.Lock()
        self._data: Dict[str, List[Dict[str, Any]]] = {
            "saved_locations": [],
            "alert_dispatches": [],
            "subscribers": []
        }
        self._load()

    def _load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                    for col in ["saved_locations", "alert_dispatches", "subscribers"]:
                        if col not in self._data:
                            self._data[col] = []
            except Exception as e:
                print(f"[JSONDocumentStore] Error reading {self.file_path}: {e}")

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, default=str)
        except Exception as e:
            print(f"[JSONDocumentStore] Error saving {self.file_path}: {e}")

    async def find(self, collection: str, filter_query: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        async with self._lock:
            docs = self._data.get(collection, [])
            if not filter_query:
                return list(reversed(docs))[:limit]
            
            filtered = []
            for doc in docs:
                match = True
                for k, v in filter_query.items():
                    if isinstance(v, str) and isinstance(doc.get(k), str):
                        if doc.get(k).lower() != v.lower():
                            match = False
                            break
                    elif doc.get(k) != v:
                        match = False
                        break
                if match:
                    filtered.append(doc)
            return list(reversed(filtered))[:limit]

    async def insert_one(self, collection: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            if collection not in self._data:
                self._data[collection] = []
            item = dict(doc)
            if "_id" not in item:
                item["_id"] = f"{collection}_{int(datetime.now().timestamp()*1000)}"
            if "created_at" not in item:
                item["created_at"] = datetime.now().isoformat()
            self._data[collection].append(item)
            self._save()
            return item

    async def update_one(self, collection: str, filter_query: Dict[str, Any], update_data: Dict[str, Any], upsert: bool = False) -> bool:
        async with self._lock:
            docs = self._data.get(collection, [])
            for doc in docs:
                match = True
                for k, v in filter_query.items():
                    if isinstance(v, str) and isinstance(doc.get(k), str):
                        if doc.get(k).lower() != v.lower():
                            match = False
                            break
                    elif doc.get(k) != v:
                        match = False
                        break
                if match:
                    doc.update(update_data)
                    self._save()
                    return True

            if upsert:
                new_doc = {**filter_query, **update_data}
                if "_id" not in new_doc:
                    new_doc["_id"] = f"{collection}_{int(datetime.now().timestamp()*1000)}"
                new_doc["created_at"] = datetime.now().isoformat()
                docs.append(new_doc)
                self._save()
                return True
            return False

    async def delete_one(self, collection: str, filter_query: Dict[str, Any]) -> bool:
        async with self._lock:
            docs = self._data.get(collection, [])
            for i, doc in enumerate(docs):
                match = True
                for k, v in filter_query.items():
                    if isinstance(v, str) and isinstance(doc.get(k), str):
                        if doc.get(k).lower() != v.lower():
                            match = False
                            break
                    elif doc.get(k) != v:
                        match = False
                        break
                if match:
                    docs.pop(i)
                    self._save()
                    return True
            return False

    async def count_documents(self, collection: str) -> int:
        async with self._lock:
            return len(self._data.get(collection, []))


class DatabaseManager:
    """Unified Database adapter with automatic MongoDB connection and JSON store fallback."""

    def __init__(self):
        self.mongodb_uri: Optional[str] = os.getenv("MONGODB_URI")
        self.db_name: str = os.getenv("MONGODB_DB", "weathergpt")
        self.motor_client = None
        self.mongo_db = None
        self.engine_type: str = "json_document_store"
        self.json_store = JSONDocumentStore(DB_FILE_PATH)
        self.is_connected: bool = False

    async def initialize(self):
        """Initializes database connection or selects fallback."""
        if MOTOR_AVAILABLE and self.mongodb_uri and (self.mongodb_uri.startswith("mongodb://") or self.mongodb_uri.startswith("mongodb+srv://")):
            try:
                # 2 second timeout for connection check
                self.motor_client = AsyncIOMotorClient(self.mongodb_uri, serverSelectionTimeoutMS=2000)
                await self.motor_client.admin.command('ping')
                self.mongo_db = self.motor_client[self.db_name]
                self.engine_type = "mongodb"
                self.is_connected = True
                print(f"[DatabaseManager] Connected to MongoDB Atlas/Instance ({self.db_name})")
                return
            except Exception as e:
                print(f"[DatabaseManager] MongoDB connection failed ({e}). Falling back to Persistent JSON Store.")
                self.engine_type = "json_document_store"
                self.is_connected = False
        else:
            self.engine_type = "json_document_store"
            self.is_connected = False

    async def get_status(self) -> Dict[str, Any]:
        """Returns database engine telemetry and document statistics."""
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            try:
                saved_count = await self.mongo_db["saved_locations"].count_documents({})
                dispatch_count = await self.mongo_db["alert_dispatches"].count_documents({})
                subscribers_count = await self.mongo_db["subscribers"].count_documents({})
                return {
                    "engine": "mongodb",
                    "status": "connected",
                    "database": self.db_name,
                    "counts": {
                        "saved_locations": saved_count,
                        "alert_dispatches": dispatch_count,
                        "subscribers": subscribers_count
                    }
                }
            except Exception:
                pass
        
        # Fallback stats
        saved_count = await self.json_store.count_documents("saved_locations")
        dispatch_count = await self.json_store.count_documents("alert_dispatches")
        subscribers_count = await self.json_store.count_documents("subscribers")
        return {
            "engine": "json_document_store",
            "status": "active (persistent)",
            "file": str(DB_FILE_PATH.name),
            "counts": {
                "saved_locations": saved_count,
                "alert_dispatches": dispatch_count,
                "subscribers": subscribers_count
            }
        }

    # --- Saved Locations ---
    async def get_saved_locations(self) -> List[Dict[str, Any]]:
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            cursor = self.mongo_db["saved_locations"].find({})
            return [
                {k: (str(v) if k == "_id" else v) for k, v in doc.items()}
                async for doc in cursor
            ]
        return await self.json_store.find("saved_locations")

    async def add_saved_location(
        self,
        location: str,
        threshold_rain_mm: float = 25.0,
        notify_heatwave: bool = True,
        phone: Optional[str] = None,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        doc = {
            "location": location.title(),
            "threshold_rain_mm": threshold_rain_mm,
            "notify_heatwave": notify_heatwave,
            "phone": phone or "",
            "channel": channel.lower(),
            "last_alerted": None,
            "created_at": datetime.now().isoformat()
        }
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            await self.mongo_db["saved_locations"].update_one(
                {"location": location.title()},
                {"$set": doc},
                upsert=True
            )
            return doc
        
        await self.json_store.update_one("saved_locations", {"location": location.title()}, doc, upsert=True)
        return doc

    async def delete_saved_location(self, location: str) -> bool:
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            res = await self.mongo_db["saved_locations"].delete_one({"location": location.title()})
            return res.deleted_count > 0
        return await self.json_store.delete_one("saved_locations", {"location": location.title()})

    async def update_location_alert_time(self, location: str):
        now_str = datetime.now().isoformat()
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            await self.mongo_db["saved_locations"].update_one(
                {"location": location.title()},
                {"$set": {"last_alerted": now_str}}
            )
        else:
            await self.json_store.update_one("saved_locations", {"location": location.title()}, {"last_alerted": now_str})

    # --- Alert Dispatches ---
    async def log_alert_dispatch(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Logs a notification dispatch event into MongoDB / JSON Document Store."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "location": record.get("location", "Unknown"),
            "severity": record.get("severity", "YELLOW"),
            "type": record.get("type", "Weather Alert"),
            "message": record.get("message", ""),
            "action": record.get("action", ""),
            "recipient": record.get("recipient", ""),
            "channel": record.get("channel", "whatsapp"),
            "status": record.get("status", "delivered"),
            "provider": record.get("provider", "simulation"),
            "message_id": record.get("message_id", f"disp_{int(datetime.now().timestamp())}")
        }
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            res = await self.mongo_db["alert_dispatches"].insert_one(entry)
            entry["_id"] = str(res.inserted_id)
            return entry
        
        return await self.json_store.insert_one("alert_dispatches", entry)

    async def get_alert_dispatches(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            cursor = self.mongo_db["alert_dispatches"].find({}).sort("timestamp", -1).limit(limit)
            return [
                {k: (str(v) if k == "_id" else v) for k, v in doc.items()}
                async for doc in cursor
            ]
        return await self.json_store.find("alert_dispatches", limit=limit)

    # --- Subscribers ---
    async def add_subscriber(
        self,
        name: str,
        phone: str,
        location: str,
        channel: str = "whatsapp"
    ) -> Dict[str, Any]:
        sub = {
            "name": name,
            "phone": phone,
            "location": location.title(),
            "channel": channel.lower(),
            "created_at": datetime.now().isoformat()
        }
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            await self.mongo_db["subscribers"].update_one(
                {"phone": phone},
                {"$set": sub},
                upsert=True
            )
            return sub
        
        await self.json_store.update_one("subscribers", {"phone": phone}, sub, upsert=True)
        return sub

    async def get_subscribers(self) -> List[Dict[str, Any]]:
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            cursor = self.mongo_db["subscribers"].find({})
            return [
                {k: (str(v) if k == "_id" else v) for k, v in doc.items()}
                async for doc in cursor
            ]
        return await self.json_store.find("subscribers")

    async def delete_subscriber(self, phone: str) -> bool:
        if self.engine_type == "mongodb" and self.mongo_db is not None:
            res = await self.mongo_db["subscribers"].delete_one({"phone": phone})
            return res.deleted_count > 0
        return await self.json_store.delete_one("subscribers", {"phone": phone})


# Global singleton instance
db_manager = DatabaseManager()
