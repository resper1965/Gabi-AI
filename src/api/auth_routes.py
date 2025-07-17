"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: auth_routes.py                                                        │
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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.models import User
from src.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    ForgotPassword,
    PasswordReset,
    MessageResponse,
    ChangePassword,
)
from src.services.user_service import (
    authenticate_user,
    create_user,
    verify_email,
    resend_verification,
    forgot_password,
    reset_password,
    change_password,
)
from src.services.auth_service import (
    create_access_token,
    get_current_admin_user,
    get_current_user,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (client) in the system

    Args:
        user_data: User data to be registered
        db: Database session

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException: If there is an error in registration
    """
    user, message = create_user(db, user_data, is_admin=False, auto_verify=False)
    if not user:
        logger.error(f"Error registering user: {message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    logger.info(f"User registered successfully: {user.email}")
    return user


@router.post(
    "/register-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_admin(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Register a new admin in the system.
    Only existing admins can create new admins.

    Args:
        user_data: Admin data to be registered
        db: Database session
        current_admin: Current admin (authenticated)

    Returns:
        UserResponse: Created admin data

    Raises:
        HTTPException: If there is an error in registration
    """
    user, message = create_user(db, user_data, is_admin=True)
    if not user:
        logger.error(f"Error registering admin: {message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    logger.info(
        f"Admin registered successfully: {user.email} (created by {current_admin.email})"
    )
    return user


@router.get("/verify-email/{token}", response_model=MessageResponse)
async def verify_user_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user email using the provided token

    Args:
        token: Verification token
        db: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If the token is invalid or expired
    """
    success, message = verify_email(db, token)
    if not success:
        logger.warning(f"Failed to verify email: {message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    logger.info(f"Email verified successfully using token: {token}")
    return {"message": message}


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    email_data: ForgotPassword, db: Session = Depends(get_db)
):
    """
    Resend verification email to the user

    Args:
        email_data: User email
        db: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If there is an error in resending
    """
    success, message = resend_verification(db, email_data.email)
    if not success:
        logger.warning(f"Failed to resend verification: {message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    logger.info(f"Verification email resent successfully to: {email_data.email}")
    return {"message": message}


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    Perform login and return a JWT access token

    Args:
        form_data: Login data (email and password)
        db: Database session

    Returns:
        TokenResponse: Access token and type

    Raises:
        HTTPException: If credentials are invalid
    """
    user, reason = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        if reason == "user_not_found" or reason == "invalid_password":
            logger.warning(f"Login attempt with invalid credentials: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif reason == "email_not_verified":
            logger.warning(f"Login attempt with unverified email: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified",
            )
        elif reason == "inactive_user":
            logger.warning(f"Login attempt with inactive user: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        else:
            logger.warning(
                f"Login attempt failed for {form_data.email} (reason: {reason})"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    access_token = create_access_token(user)
    logger.info(f"Login successful for user: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_user_password(
    email_data: ForgotPassword, db: Session = Depends(get_db)
):
    """
    Initiate the password recovery process

    Args:
        email_data: User email
        db: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If there is an error in the process
    """
    success, message = forgot_password(db, email_data.email)
    # Always return the same message for security
    return {
        "message": "If the email is registered, you will receive instructions to reset your password."
    }


@router.post("/reset-password", response_model=MessageResponse)
async def reset_user_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """
    Reset user password using the provided token

    Args:
        reset_data: Token and new password
        db: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If the token is invalid or expired
    """
    success, message = reset_password(db, reset_data.token, reset_data.new_password)
    if not success:
        logger.warning(f"Failed to reset password: {message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    logger.info("Password reset successfully")
    return {"message": message}


@router.post("/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get the authenticated user's data

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        UserResponse: Authenticated user data

    Raises:
        HTTPException: If the user is not authenticated
    """
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_user_password(
    password_data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change the password of the authenticated user

    Args:
        password_data: Current and new password
        db: Database session
        current_user: Authenticated user

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If the current password is invalid
    """
    success, message = change_password(
        db, current_user.id, password_data.current_password, password_data.new_password
    )

    if not success:
        logger.warning(f"Failed to change password for user: {current_user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    logger.info(f"Password changed successfully for user: {current_user.email}")
    return {"message": message}
