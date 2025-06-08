"""
Import wrapper for the conversation management system.
This allows src modules to import from the root directory.
"""

import sys
import importlib.util
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Add project root to path if needed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Inside Docker, the file might be in different locations. Try multiple approaches.
try:
    # First try normal import from src
    from src.conversation_management import (
        ConversationManager,
        ConversationContext,
        TopicDetector,
        EntityExtractor,
        BackgroundTaskManager,
        create_conversation_management_system,
    )

    logger.info("Successfully imported conversation_management using standard import")
except ImportError:
    logger.warning("Standard import failed, trying alternative methods")

    # Try to locate the module file
    potential_paths = [
        # Root project directory
        project_root / "conversation_management.py",
        # Same directory as wrapper
        Path(__file__).parent / "conversation_management.py",
        # In src directory
        Path(__file__).parent / "conversation_management.py",
        # For Docker environment
        Path("/app/conversation_management.py"),
        Path("/app/src/conversation_management.py"),
    ]

    module_path = None
    for path in potential_paths:
        if path.exists():
            module_path = path
            logger.info(f"Found conversation_management at: {module_path}")
            break

    if module_path:
        # Load the module directly from file
        spec = importlib.util.spec_from_file_location(
            "conversation_management", module_path
        )
        conversation_management = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conversation_management)

        # Extract needed components
        ConversationManager = conversation_management.ConversationManager
        ConversationContext = conversation_management.ConversationContext
        TopicDetector = conversation_management.TopicDetector
        EntityExtractor = conversation_management.EntityExtractor
        BackgroundTaskManager = conversation_management.BackgroundTaskManager
        create_conversation_management_system = (
            conversation_management.create_conversation_management_system
        )

        logger.info("Successfully imported conversation_management from file")
    else:
        logger.error("Could not find conversation_management module in any location")
        raise ImportError(
            "Could not locate conversation_management.py in any expected location"
        )

__all__ = [
    "ConversationManager",
    "ConversationContext",
    "TopicDetector",
    "EntityExtractor",
    "BackgroundTaskManager",
    "create_conversation_management_system",
]
