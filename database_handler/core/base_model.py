"""Base model class with common functionality."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict, field


@dataclass
class BaseModel(ABC):
    """Abstract base class for all database models."""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
            
        return data
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary."""
        # Handle datetime conversion
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseModel':
        """Create model instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update a single metadata field."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata field value."""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def validate(self) -> None:
        """Validate model data. Override in subclasses."""
        pass
    
    @abstractmethod
    def get_table_name(self) -> str:
        """Get the database table name for this model."""
        pass
    
    @abstractmethod
    def get_insert_fields(self) -> List[str]:
        """Get list of fields to include in INSERT statements."""
        pass
    
    @abstractmethod
    def get_update_fields(self) -> List[str]:
        """Get list of fields to include in UPDATE statements."""
        pass
    
    def get_insert_values(self) -> Dict[str, Any]:
        """Get values for INSERT statement."""
        data = self.to_dict()
        fields = self.get_insert_fields()
        return {field: data.get(field) for field in fields if field in data}
    
    def get_update_values(self) -> Dict[str, Any]:
        """Get values for UPDATE statement."""
        data = self.to_dict()
        fields = self.get_update_fields()
        return {field: data.get(field) for field in fields if field in data}
    
    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        if self.id:
            return f"<{class_name}(id={self.id})>"
        return f"<{class_name}(new)>"
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID if both have IDs."""
        if not isinstance(other, self.__class__):
            return False
        if self.id is not None and other.id is not None:
            return self.id == other.id
        return super().__eq__(other)
    
    def __hash__(self) -> int:
        """Hash based on ID if available."""
        if self.id is not None:
            return hash((self.__class__, self.id))
        return super().__hash__()