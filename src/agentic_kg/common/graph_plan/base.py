"""
Base classes for the graph plan module.

This module contains the base classes that are used throughout the graph plan system.
"""

import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BasePlan(BaseModel):
    """
    Base class for all plan elements in the graph plan.
    
    Attributes:
        id: Unique identifier for the plan element
        name: Name of the plan element
        description: Description of what this plan element represents
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
