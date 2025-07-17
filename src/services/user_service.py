"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: user_service.py                                                       │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: May 13, 2025                                                  │
│ Contact: contato@evolution-api.com                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ @copyright © Evolution API 2025. All rights reserved.                        │
│ Licensed under the Apache License, Version 2.0                               │
│                                                                              │
│ You may not use this file except in compliance with the License.             │
│ You may obtain a copy of the License at                                      │
│                                                                              │
│    http://www.apache.org/licenses/LICENSE-2.0                                │
│                                                                              │
│ Unless required by applicable law or agreed to in writing, software          │
│ distributed under the License is distributed on an "AS IS" BASIS,            │
│ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.     │
│ See the License for the specific language governing permissions and          │
│ limitations under the License.                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ @important                                                                   │
│ For any future changes to the code in this file, it is recommended to        │
│ include, together with the modification, the information of the developer    │
│ who changed it and the date of modification.                                 │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.models.models import User, Client
from src.schemas.user import UserCreate
from src.utils.security import get_password_hash, verify_password, generate_token
from src.services.email_service import (
    send_verification_email,
    send_password_reset_email,
)
from datetime import datetime, timedelta, timezone
import uuid
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def create_user(
    db: Session,
    user_data: UserCreate,
    is_admin: bool = False,
    client_id: Optional[uuid.UUID] = None,
    auto_verify: bool = False,
) -> Tuple[Optional[User], str]:
    """
    Creates a new user in the system

    Args:
        db: Database session
        user_data: User data to be created
        is_admin: If the user is an administrator
        client_id: Associated client ID (optional, a new one will be created if not provided)
        auto_verify: If True, user is created with email already verified and active

    Returns:
        Tuple[Optional[User], str]: Tuple with the created user (or None in case of error) and status message
    """
    try:
        # Check if email already exists
        db_user = db.query(User).filter(User.email == user_data.email).first()
        if db_user:
            logger.warning(
                f"Attempt to register with existing email: {user_data.email}"
            )
            return None, "Email already registered"

        # Create verification token if needed
        verification_token = None
        token_expiry = None
        if not auto_verify:
            verification_token = generate_token()
            token_expiry = datetime.utcnow() + timedelta(hours=24)

        # Start transaction
        user = None
        local_client_id = client_id

        try:
            # If not admin and no client_id, create an associated client
            if not is_admin and local_client_id is None:
                client = Client(name=user_data.name, email=user_data.email)
                db.add(client)
                db.flush()  # Get the client ID
                local_client_id = client.id

            # Create user
            user = User(
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                client_id=local_client_id,
                is_admin=is_admin,
                is_active=auto_verify,
                email_verified=auto_verify,
                verification_token=verification_token,
                verification_token_expiry=token_expiry,
            )
            db.add(user)
            db.commit()

            # Send verification email if not auto-verified
            if not auto_verify:
                email_sent = send_verification_email(user.email, verification_token)
                if not email_sent:
                    logger.error(f"Failed to send verification email to {user.email}")
                    # We don't do rollback here, we just log the error

                logger.info(f"User created successfully: {user.email}")
                return (
                    user,
                    "User created successfully. Check your email to activate your account.",
                )
            else:
                logger.info(f"User created and auto-verified: {user.email}")
                return (
                    user,
                    "User created successfully.",
                )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            return None, f"Error creating user: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        return None, f"Unexpected error: {str(e)}"


def verify_email(db: Session, token: str) -> Tuple[bool, str]:
    """
    Verify the user's email using the provided token

    Args:
        db: Database session
        token: Verification token

    Returns:
        Tuple[bool, str]: Tuple with verification status and message
    """
    try:
        # Search for user by token
        user = db.query(User).filter(User.verification_token == token).first()

        if not user:
            logger.warning(f"Attempt to verify with invalid token: {token}")
            return False, "Invalid verification token"

        # Check if the token has expired
        now = datetime.utcnow()
        expiry = user.verification_token_expiry

        # Ensure both dates are of the same type (aware or naive)
        if expiry.tzinfo is not None and now.tzinfo is None:
            # If expiry has timezone and now doesn't, convert now to have timezone
            now = now.replace(tzinfo=expiry.tzinfo)
        elif now.tzinfo is not None and expiry.tzinfo is None:
            # If now has timezone and expiry doesn't, convert expiry to have timezone
            expiry = expiry.replace(tzinfo=now.tzinfo)

        if expiry < now:
            logger.warning(
                f"Attempt to verify with expired token for user: {user.email}"
            )
            return False, "Verification token expired"

        # Update user
        user.email_verified = True
        user.is_active = True
        user.verification_token = None
        user.verification_token_expiry = None

        db.commit()
        logger.info(f"Email verified successfully for user: {user.email}")
        return True, "Email verified successfully. Your account is active."

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error verifying email: {str(e)}")
        return False, f"Error verifying email: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error verifying email: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def resend_verification(db: Session, email: str) -> Tuple[bool, str]:
    """
    Resend the verification email

    Args:
        db: Database session
        email: User email

    Returns:
        Tuple[bool, str]: Tuple with operation status and message
    """
    try:
        # Search for user by email
        user = db.query(User).filter(User.email == email).first()

        if not user:
            logger.warning(
                f"Attempt to resend verification email for non-existent email: {email}"
            )
            return False, "Email not found"

        if user.email_verified:
            logger.info(
                f"Attempt to resend verification email for already verified email: {email}"
            )
            return False, "Email already verified"

        # Generate new token
        verification_token = generate_token()
        token_expiry = datetime.utcnow() + timedelta(hours=24)

        # Update user
        user.verification_token = verification_token
        user.verification_token_expiry = token_expiry

        db.commit()

        # Send email
        email_sent = send_verification_email(user.email, verification_token)
        if not email_sent:
            logger.error(f"Failed to resend verification email to {user.email}")
            return False, "Failed to send verification email"

        logger.info(f"Verification email resent successfully to: {user.email}")
        return True, "Verification email resent. Check your inbox."

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error resending verification: {str(e)}")
        return False, f"Error resending verification: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error resending verification: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def forgot_password(db: Session, email: str) -> Tuple[bool, str]:
    """
    Initiates the password recovery process

    Args:
        db: Database session
        email: User email

    Returns:
        Tuple[bool, str]: Tuple with operation status and message
    """
    try:
        # Search for user by email
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # For security, we don't inform if the email exists or not
            logger.info(f"Attempt to recover password for non-existent email: {email}")
            return (
                True,
                "If the email is registered, you will receive instructions to reset your password.",
            )

        # Generate reset token
        reset_token = generate_token()
        token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

        # Update user
        user.password_reset_token = reset_token
        user.password_reset_expiry = token_expiry

        db.commit()

        # Send email
        email_sent = send_password_reset_email(user.email, reset_token)
        if not email_sent:
            logger.error(f"Failed to send password reset email to {user.email}")
            return False, "Failed to send password reset email"

        logger.info(f"Password reset email sent successfully to: {user.email}")
        return (
            True,
            "If the email is registered, you will receive instructions to reset your password.",
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error processing password recovery: {str(e)}")
        return False, f"Error processing password recovery: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error processing password recovery: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def reset_password(db: Session, token: str, new_password: str) -> Tuple[bool, str]:
    """
    Resets the user's password using the provided token

    Args:
        db: Database session
        token: Password reset token
        new_password: New password

    Returns:
        Tuple[bool, str]: Tuple with operation status and message
    """
    try:
        # Search for user by token
        user = db.query(User).filter(User.password_reset_token == token).first()

        if not user:
            logger.warning(f"Attempt to reset password with invalid token: {token}")
            return False, "Invalid password reset token"

        # Check if the token has expired
        now = datetime.now(timezone.utc)
        expiry = user.password_reset_expiry
        if expiry is not None and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry is None or expiry < now:
            logger.warning(
                f"Attempt to reset password with expired token for user: {user.email}"
            )
            return False, "Password reset token expired"

        # Update password
        user.password_hash = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expiry = None

        db.commit()
        logger.info(f"Password reset successfully for user: {user.email}")
        return (
            True,
            "Password reset successfully. You can now login with your new password.",
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error resetting password: {str(e)}")
        return False, f"Error resetting password: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error resetting password: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Searches for a user by email

    Args:
        db: Database session
        email: User email

    Returns:
        Optional[User]: User found or None
    """
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error(f"Error searching for user by email: {str(e)}")
        return None


def authenticate_user(
    db: Session, email: str, password: str
) -> Tuple[Optional[User], str]:
    """
    Authenticates a user with email and password

    Args:
        db: Database session
        email: User email
        password: User password

    Returns:
        Tuple[Optional[User], str]: Authenticated user and reason (or None and reason)
    """
    user = get_user_by_email(db, email)
    if not user:
        return None, "user_not_found"
    if not verify_password(password, user.password_hash):
        return None, "invalid_password"
    if not user.email_verified:
        return None, "email_not_verified"
    if not user.is_active:
        return None, "inactive_user"
    return user, "success"


def get_admin_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Lists the admin users

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List[User]: List of admin users
    """
    try:
        users = db.query(User).filter(User.is_admin).offset(skip).limit(limit).all()
        logger.info(f"List of admins: {len(users)} found")
        return users

    except SQLAlchemyError as e:
        logger.error(f"Error listing admins: {str(e)}")
        return []

    except Exception as e:
        logger.error(f"Unexpected error listing admins: {str(e)}")
        return []


def create_admin_user(db: Session, user_data: UserCreate) -> Tuple[Optional[User], str]:
    """
    Creates a new admin user

    Args:
        db: Database session
        user_data: User data to be created

    Returns:
        Tuple[Optional[User], str]: Tuple with the created user (or None in case of error) and status message
    """
    return create_user(db, user_data, is_admin=True, auto_verify=True)


def deactivate_user(db: Session, user_id: uuid.UUID) -> Tuple[bool, str]:
    """
    Deactivates a user (does not delete, only marks as inactive)

    Args:
        db: Database session
        user_id: ID of the user to be deactivated

    Returns:
        Tuple[bool, str]: Tuple with operation status and message
    """
    try:
        # Search for user by ID
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"Attempt to deactivate non-existent user: {user_id}")
            return False, "User not found"

        # Deactivate user
        user.is_active = False

        db.commit()
        logger.info(f"User deactivated successfully: {user.email}")
        return True, "User deactivated successfully"

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deactivating user: {str(e)}")
        return False, f"Error deactivating user: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error deactivating user: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def change_password(
    db: Session, user_id: uuid.UUID, current_password: str, new_password: str
) -> Tuple[bool, str]:
    """
    Changes the password of an authenticated user

    Args:
        db: Database session
        user_id: ID of the user
        current_password: Current password for verification
        new_password: New password to set

    Returns:
        Tuple[bool, str]: Tuple with operation status and message
    """
    try:
        # Search for user by ID
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(
                f"Attempt to change password for non-existent user: {user_id}"
            )
            return False, "User not found"

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            logger.warning(
                f"Attempt to change password with invalid current password for user: {user.email}"
            )
            return False, "Current password is incorrect"

        # Update password
        user.password_hash = get_password_hash(new_password)

        db.commit()
        logger.info(f"Password changed successfully for user: {user.email}")
        return True, "Password changed successfully"

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error changing password: {str(e)}")
        return False, f"Error changing password: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error changing password: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
