#!/usr/bin/env python
"""
Initialize data directory for Grace application
This script ensures the data directory exists and has the right structure
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceInit")

def init_data_directory(data_dir):
    """Initialize the data directory structure"""
    try:
        # Create main data directory
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"Created main data directory: {data_dir}")
        
        # Create ChromaDB directory
        chroma_dir = os.path.join(data_dir, 'chromadb')
        os.makedirs(chroma_dir, exist_ok=True)
        logger.info(f"Created ChromaDB directory: {chroma_dir}")
        
        # Create users directory
        users_dir = os.path.join(data_dir, 'users')
        os.makedirs(users_dir, exist_ok=True)
        logger.info(f"Created users directory: {users_dir}")
        
        # Create empty profiles.json if it doesn't exist
        profiles_file = os.path.join(data_dir, 'profiles.json')
        if not os.path.exists(profiles_file):
            with open(profiles_file, 'w') as f:
                f.write('{}')
            logger.info(f"Created empty profiles.json file: {profiles_file}")
            
        logger.info("Data directory initialization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing data directory: {str(e)}")
        return False

if __name__ == "__main__":
    # Get data directory from command line or use default
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    
    # Initialize data directory
    success = init_data_directory(data_dir)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
