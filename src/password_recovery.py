"""
Password Recovery System for Grace - A crypto trading application based on Open Interpreter

This module implements a simple email-based password recovery system.
"""

import json
import os
import uuid
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Local imports - commented out to avoid import errors in standalone mode
# from src.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("GracePasswordRecovery")


class PasswordRecoverySystem:
    """
    Handles password recovery through email or SMS.
    """

    def __init__(
        self,
        recovery_tokens_file: str = "recovery_tokens.json",
        token_expiry_hours: int = 24,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """
        Initialize the password recovery system.

        Args:
            recovery_tokens_file: File to store recovery tokens
            token_expiry_hours: Hours until recovery tokens expire
            smtp_host: SMTP server host for sending emails
            smtp_port: SMTP server port
            smtp_username: SMTP server username
            smtp_password: SMTP server password
            from_email: Email address to send recovery emails from
        """
        self.recovery_tokens_file = recovery_tokens_file
        self.token_expiry_hours = token_expiry_hours
        self.smtp_host = smtp_host or os.environ.get("SMTP_HOST", "smtp.gmail.com")

        # Ensure SMTP port is an integer
        try:
            self.smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))
        except ValueError:
            logger.warning("Invalid SMTP_PORT value, defaulting to 587")
            self.smtp_port = 587

        self.smtp_username = smtp_username or os.environ.get("SMTP_USERNAME", "")
        self.smtp_password = smtp_password or os.environ.get("SMTP_PASSWORD", "")
        self.from_email = from_email or os.environ.get(
            "FROM_EMAIL", "noreply@grace.app"
        )

        # Validate SMTP configuration
        self.smtp_configured = bool(self.smtp_host and self.smtp_port)
        if not self.smtp_configured:
            logger.warning("SMTP not fully configured. Email recovery will not work.")
        elif not (self.smtp_username and self.smtp_password):
            logger.warning("SMTP credentials not provided. Authentication may fail.")

        # Create recovery tokens file if it doesn't exist
        if not os.path.exists(recovery_tokens_file):
            with open(recovery_tokens_file, "w", encoding="utf-8") as f:
                f.write("{}")

    def _load_tokens(self) -> Dict[str, Any]:
        """
        Load recovery tokens from file.

        Returns:
            Dict: Recovery tokens
        """
        try:
            with open(self.recovery_tokens_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_tokens(self, tokens: Dict[str, Any]) -> None:
        """
        Save recovery tokens to file.

        Args:
            tokens: Recovery tokens to save
        """
        with open(self.recovery_tokens_file, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2)

    def _clean_expired_tokens(self) -> None:
        """
        Remove expired recovery tokens.
        """
        tokens = self._load_tokens()
        current_time = datetime.now().timestamp()

        # Filter out expired tokens
        valid_tokens = {}
        for token, token_data in tokens.items():
            if token_data.get("expires_at", 0) > current_time:
                valid_tokens[token] = token_data

        self._save_tokens(valid_tokens)

    def generate_recovery_token(self, user_id: str, email: str) -> str:
        """
        Generate a password recovery token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            str: Recovery token
        """
        # Clean expired tokens first
        self._clean_expired_tokens()

        # Generate a new token
        token = str(uuid.uuid4())

        # Calculate expiry time
        expires_at = (
            datetime.now() + timedelta(hours=self.token_expiry_hours)
        ).timestamp()

        # Store token
        tokens = self._load_tokens()
        tokens[token] = {
            "user_id": user_id,
            "email": email,
            "created_at": datetime.now().timestamp(),
            "expires_at": expires_at,
            "used": False,
        }
        self._save_tokens(tokens)

        return token

    def verify_recovery_token(self, recovery_token: str) -> Dict[str, Any]:
        """
        Verify a password recovery token.

        Args:
            token: Recovery token

        Returns:
            Dict: Verification result
        """
        tokens = self._load_tokens()

        if recovery_token not in tokens:
            return {"valid": False, "error": "Invalid token"}

        token_data = tokens[recovery_token]

        # Check if token is expired
        if token_data.get("expires_at", 0) < datetime.now().timestamp():
            return {"valid": False, "error": "Token expired"}

        # Check if token has been used
        if token_data.get("used", False):
            return {"valid": False, "error": "Token already used"}

        return {
            "valid": True,
            "user_id": token_data["user_id"],
            "email": token_data["email"],
        }

    def mark_token_used(self, recovery_token: str) -> bool:
        """
        Mark a recovery token as used.

        Args:
            token: Recovery token

        Returns:
            bool: Success status
        """
        tokens = self._load_tokens()

        if recovery_token not in tokens:
            return False

        tokens[recovery_token]["used"] = True
        self._save_tokens(tokens)

        return True

    def send_recovery_email(
        self, email: str, recovery_token: str, reset_url: str
    ) -> bool:
        """
        Send a password recovery email.

        Args:
            email: Recipient email
            token: Recovery token
            reset_url: URL for password reset page

        Returns:
            bool: Success status
        """
        if not self.smtp_configured:
            logger.error("Cannot send recovery email: SMTP not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = email
            msg["Subject"] = "Grace - Password Recovery"

            # Create reset URL with token
            full_reset_url = f"{reset_url}?token={recovery_token}"

            # Create message body
            body = f"""
            Hello,
           
            You requested a password reset for your Grace account.
           
            Click the link below to reset your password:
            {full_reset_url}
           
            This link will expire in {self.token_expiry_hours} hours.
           
            If you did not request this reset, please ignore this email.
           
            Best regards,
            The Grace Team
            """

            msg.attach(MIMEText(body, "plain"))

            # Connect to SMTP server
            logger.info(
                "Connecting to SMTP server %s:%s", self.smtp_host, self.smtp_port
            )
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()

            # Login if credentials provided
            if self.smtp_username and self.smtp_password:
                logger.info(
                    "Logging in to SMTP server with username %s", self.smtp_username
                )
                server.login(self.smtp_username, self.smtp_password)
            else:
                logger.warning(
                    "No SMTP credentials provided, attempting to send without authentication"
                )

            # Send email
            logger.info("Sending recovery email to %s", email)
            server.send_message(msg)
            server.quit()

            logger.info("Recovery email sent successfully to %s", email)
            return True
        except ConnectionRefusedError:
            logger.error(
                f"Connection refused to SMTP server {self.smtp_host}:{self.smtp_port}"
            )
            return False
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check username and password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending recovery email: {str(e)}")
            return False
        except Exception as e:
            logger.error("Error sending recovery email: %s", str(e))
            return False

    def send_recovery_sms(self, phone: str, recovery_token: str) -> bool:
        """
        Send a password recovery SMS.

        Args:
            phone: Recipient phone number
            token: Recovery token

        Returns:
            bool: Success status
        """
        # In a real implementation, this would use a SMS gateway
        # For now, just log the message and return success
        logger.info("Would send SMS to %s with token %s", phone, recovery_token)
        return True

    def initiate_recovery(
        self, email: str, user_id: str, reset_url: str, phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate the password recovery process.

        Args:
            email: User email
            user_id: User ID
            reset_url: URL for password reset page
            phone: Optional phone number for SMS recovery

        Returns:
            Dict: Recovery result
        """
        # Generate recovery token
        token = self.generate_recovery_token(user_id, email)

        # Send recovery email
        email_sent = self.send_recovery_email(email, token, reset_url)

        # Send recovery SMS if phone provided
        sms_sent = False
        if phone:
            sms_sent = self.send_recovery_sms(phone, token)

        result = {
            "success": email_sent or sms_sent,
            "email_sent": email_sent,
            "sms_sent": sms_sent,
        }

        # Only include token in development/debug environments
        if os.environ.get("GRACE_ENV") == "development":
            result["token"] = token
            logger.warning(
                "Including recovery token in response (development mode only)"
            )

        return result

    def complete_recovery(
        self, token: str, new_password: str, user_profile_system
    ) -> Dict[str, Any]:
        """
        Complete the password recovery process.

        Args:
            token: Recovery token
            new_password: New password
            user_profile_system: User profile system instance

        Returns:
            Dict: Recovery result
        """
        # Verify token
        verification = self.verify_recovery_token(token)

        if not verification["valid"]:
            return {"success": False, "error": verification["error"]}

        # Update password
        try:
            user_id = verification["user_id"]
            success = user_profile_system.update_password(user_id, new_password)

            if success:
                # Mark token as used
                self.mark_token_used(token)
                return {"success": True}

            return {"success": False, "error": "Failed to update password"}
        except Exception as e:
            logger.error("Error completing recovery: %s", str(e))
            return {"success": False, "error": str(e)}


# Example usage
if __name__ == "__main__":
    recovery_system = PasswordRecoverySystem()

    # Simulate recovery process
    recovery_result = recovery_system.initiate_recovery(
        "test@example.com",
        "user123",
        "http://localhost:3000/reset-password",
        "1234567890",
    )

    print(f"Recovery initiated: {recovery_result}")

    # Verify token
    test_token = recovery_result.get("token", "")
    token_verification = recovery_system.verify_recovery_token(test_token)

    print(f"Token verification: {token_verification}")
