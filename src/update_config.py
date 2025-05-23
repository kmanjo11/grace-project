"""
Update all Grace components to use the centralized configuration system.

This script updates all existing Grace components to use the new
centralized configuration system instead of hardcoded values,
environment variables, or inconsistent configuration loading.
"""

import os
import re
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ConfigUpdater")


class ConfigUpdater:
    """
    Updates Grace components to use the centralized configuration system.
    """

    def __init__(self, src_dir: str):
        """
        Initialize the updater.

        Args:
            src_dir: Source directory containing Grace components
        """
        self.src_dir = src_dir
        logger.info(f"Initializing ConfigUpdater for {src_dir}")

    def find_python_files(self) -> List[str]:
        """
        Find all Python files in the source directory.

        Returns:
            List[str]: List of Python file paths
        """
        python_files = []

        for root, _, files in os.walk(self.src_dir):
            for file in files:
                if file.endswith(".py") and file != "config.py":
                    python_files.append(os.path.join(root, file))

        logger.info(f"Found {len(python_files)} Python files to update")
        return python_files

    def update_file(self, file_path: str) -> bool:
        """
        Update a single Python file to use the centralized configuration.

        Args:
            file_path: Path to Python file

        Returns:
            bool: Success status
        """
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Check if file already imports config
            if "from src.config import" in content:
                logger.info(f"File {file_path} already uses centralized config")
                return True

            # Add import statement
            import_statement = "from src.config import get_config\n"

            # Add import after other imports
            import_section_end = re.search(
                r"(^import.*?\n+|^from.*?\n+)+", content, re.MULTILINE
            )
            if import_section_end:
                position = import_section_end.end()
                content = content[:position] + import_statement + content[position:]
            else:
                # If no imports found, add at the beginning after docstring
                docstring_end = re.search(
                    r'^""".*?"""\n+', content, re.MULTILINE | re.DOTALL
                )
                if docstring_end:
                    position = docstring_end.end()
                    content = content[:position] + import_statement + content[position:]
                else:
                    # If no docstring, add at the beginning
                    content = import_statement + content

            # Replace hardcoded configuration values
            replacements = {
                r'data_dir\s*=\s*[\'"].*?[\'"]': 'data_dir = get_config().get("data_dir")',
                r'encryption_key\s*=\s*[\'"].*?[\'"]': 'encryption_key = get_config().get("encryption_key")',
                r'solana_rpc_url\s*=\s*[\'"].*?[\'"]': 'solana_rpc_url = get_config().get("solana_rpc_url")',
                r'solana_network\s*=\s*[\'"].*?[\'"]': 'solana_network = get_config().get("solana_network")',
                r'nitter_instance\s*=\s*[\'"].*?[\'"]': 'nitter_instance = get_config().get("nitter_instance")',
                r'gmgn_router_endpoint\s*=\s*[\'"].*?[\'"]': 'gmgn_router_endpoint = get_config().get("gmgn_router_endpoint")',
                r'gmgn_price_endpoint\s*=\s*[\'"].*?[\'"]': 'gmgn_price_endpoint = get_config().get("gmgn_price_endpoint")',
                r'authorized_admin_email\s*=\s*[\'"].*?[\'"]': 'authorized_admin_email = get_config().get("authorized_admin_email")',
                r'os\.environ\.get\([\'"]SOLANA_RPC_URL[\'"].*?\)': 'get_config().get("solana_rpc_url")',
                r'os\.environ\.get\([\'"]SOLANA_NETWORK[\'"].*?\)': 'get_config().get("solana_network")',
                r'os\.environ\.get\([\'"]NITTER_INSTANCE[\'"].*?\)': 'get_config().get("nitter_instance")',
                r'os\.environ\.get\([\'"]GMGN_ROUTER_ENDPOINT[\'"].*?\)': 'get_config().get("gmgn_router_endpoint")',
                r'os\.environ\.get\([\'"]GMGN_PRICE_ENDPOINT[\'"].*?\)': 'get_config().get("gmgn_price_endpoint")',
                r'os\.environ\.get\([\'"]AUTHORIZED_ADMIN_EMAIL[\'"].*?\)': 'get_config().get("authorized_admin_email")',
            }

            for pattern, replacement in replacements.items():
                content = re.sub(pattern, replacement, content)

            # Update class initializers to use config
            class_init_pattern = r"def __init__\(self,\s*([^)]*)\):"
            class_init_matches = re.finditer(class_init_pattern, content, re.MULTILINE)

            for match in class_init_matches:
                init_params = match.group(1)

                # Check for config parameters
                config_params = [
                    "data_dir",
                    "encryption_key",
                    "solana_rpc_url",
                    "solana_network",
                    "nitter_instance",
                    "gmgn_router_endpoint",
                    "gmgn_price_endpoint",
                    "authorized_admin_email",
                ]

                for param in config_params:
                    # If parameter exists with default value
                    param_pattern = rf'{param}\s*:\s*\w+\s*=\s*[\'"].*?[\'"]'
                    if re.search(param_pattern, init_params):
                        # Replace with None default and get from config
                        init_params = re.sub(
                            param_pattern, f"{param}: str = None", init_params
                        )

                        # Add config retrieval in method body
                        method_body_pattern = rf"def __init__\(self,\s*{re.escape(match.group(1))}\):(.*?)(?=\n\s*def|\Z)"
                        method_body_match = re.search(
                            method_body_pattern, content, re.MULTILINE | re.DOTALL
                        )

                        if method_body_match:
                            method_body = method_body_match.group(1)
                            config_line = f'\n        self.{param} = {param} or get_config().get("{param}")'

                            # Check if parameter is already being set
                            param_set_pattern = rf"self\.{param}\s*="
                            if re.search(param_set_pattern, method_body):
                                # Replace existing assignment
                                method_body = re.sub(
                                    rf"self\.{param}\s*=\s*.*?\n",
                                    f'self.{param} = {param} or get_config().get("{param}")\n',
                                    method_body,
                                )
                            else:
                                # Add new assignment after first line
                                first_line_end = method_body.find("\n")
                                if first_line_end != -1:
                                    method_body = (
                                        method_body[: first_line_end + 1]
                                        + config_line
                                        + method_body[first_line_end + 1 :]
                                    )
                                else:
                                    method_body += config_line

                            # Update method body in content
                            content = re.sub(
                                method_body_pattern,
                                f"def __init__(self, {init_params}):{method_body}",
                                content,
                                flags=re.MULTILINE | re.DOTALL,
                            )

                # Update content with modified init params
                content = re.sub(
                    class_init_pattern,
                    f"def __init__(self, {init_params}):",
                    content,
                    count=1,
                )

            # Write updated content back to file
            with open(file_path, "w") as f:
                f.write(content)

            logger.info(f"Updated {file_path} to use centralized config")
            return True

        except Exception as e:
            logger.error(f"Error updating {file_path}: {str(e)}")
            return False

    def update_all_files(self) -> Dict[str, Any]:
        """
        Update all Python files to use the centralized configuration.

        Returns:
            Dict[str, Any]: Update results
        """
        python_files = self.find_python_files()
        success_count = 0
        failed_files = []

        for file_path in python_files:
            if self.update_file(file_path):
                success_count += 1
            else:
                failed_files.append(file_path)

        results = {
            "total_files": len(python_files),
            "success_count": success_count,
            "failed_count": len(failed_files),
            "failed_files": failed_files,
        }

        logger.info(
            f"Updated {success_count}/{len(python_files)} files to use centralized config"
        )

        if failed_files:
            logger.warning(
                f"Failed to update {len(failed_files)} files: {failed_files}"
            )

        return results


# Run updater if script is executed directly
if __name__ == "__main__":
    updater = ConfigUpdater("/home/ubuntu/grace_project/src")
    results = updater.update_all_files()

    print(f"Configuration update complete!")
    print(f"Updated {results['success_count']}/{results['total_files']} files")

    if results["failed_count"] > 0:
        print(f"Failed to update {results['failed_count']} files:")
        for file in results["failed_files"]:
            print(f"  - {file}")
