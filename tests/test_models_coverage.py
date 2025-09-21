"""Test coverage for models.py module."""

from datetime import datetime, timedelta

import pytest

# Import the actual modules to test
from app import PasswordResetRequestLog, PasswordResetToken, SavedRecipe, User, db  # type: ignore


class TestUserModel:
    """Test the User model."""

    def test_user_creation(self, client):
        """Test creating a User instance."""
        with client.application.app_context():
            user = User(
                email_address="test@example.com",
                full_name="Test User",
                password_hash="hashed_password",
                country="USA",
                newsletter_signup=True,
            )

            db.session.add(user)
            db.session.commit()

            assert user.user_id is not None
            assert user.email_address == "test@example.com"
            assert user.full_name == "Test User"
            assert user.password_hash == "hashed_password"
            assert user.country == "USA"
            assert user.newsletter_signup is True

    def test_user_get_id_method(self, client):
        """Test the get_id method for Flask-Login integration."""
        with client.application.app_context():
            user = User(
                email_address="test@example.com",
                full_name="Test User",
                password_hash="hashed_password",
            )

            db.session.add(user)
            db.session.commit()

            # get_id should return string representation of user_id
            assert user.get_id() == str(user.user_id)

    def test_user_minimal_fields(self, client):
        """Test User creation with minimal required fields."""
        with client.application.app_context():
            user = User(
                email_address="minimal@example.com",
                full_name="Minimal User",
                password_hash="hashed_password",
            )

            db.session.add(user)
            db.session.commit()

            assert user.user_id is not None
            assert user.email_address == "minimal@example.com"
            assert user.full_name == "Minimal User"
            assert user.country is None
            assert user.newsletter_signup is None


class TestSavedRecipeModel:
    """Test the SavedRecipe model."""

    def test_saved_recipe_creation(self, client):
        """Test creating a SavedRecipe instance."""
        with client.application.app_context():
            # First create a user
            user = User(
                email_address="test@example.com",
                full_name="Test User",
                password_hash="hashed_password",
            )
            db.session.add(user)
            db.session.commit()

            # Create saved recipe
            saved_recipe = SavedRecipe(user_id=user.user_id, recipe_id="recipe123")

            db.session.add(saved_recipe)
            db.session.commit()

            assert saved_recipe.id is not None
            assert saved_recipe.user_id == user.user_id
            assert saved_recipe.recipe_id == "recipe123"
            assert saved_recipe.saved_at is not None
            assert isinstance(saved_recipe.saved_at, datetime)

    def test_saved_recipe_unique_constraint(self, client):
        """Test that the unique constraint works for user_id + recipe_id."""
        with client.application.app_context():
            # Create user
            user = User(
                email_address="test@example.com",
                full_name="Test User",
                password_hash="hashed_password",
            )
            db.session.add(user)
            db.session.commit()

            # Create first saved recipe
            saved_recipe1 = SavedRecipe(user_id=user.user_id, recipe_id="recipe123")
            db.session.add(saved_recipe1)
            db.session.commit()

            # Try to create duplicate - should raise integrity error
            saved_recipe2 = SavedRecipe(user_id=user.user_id, recipe_id="recipe123")
            db.session.add(saved_recipe2)

            with pytest.raises(Exception):  # IntegrityError or similar
                db.session.commit()

    def test_saved_recipe_different_users_same_recipe(self, client):
        """Test that different users can save the same recipe."""
        with client.application.app_context():
            # Create two users
            user1 = User(
                email_address="user1@example.com",
                full_name="User One",
                password_hash="hashed_password",
            )
            user2 = User(
                email_address="user2@example.com",
                full_name="User Two",
                password_hash="hashed_password",
            )
            db.session.add_all([user1, user2])
            db.session.commit()

            # Both users save the same recipe
            saved_recipe1 = SavedRecipe(user_id=user1.user_id, recipe_id="recipe123")
            saved_recipe2 = SavedRecipe(user_id=user2.user_id, recipe_id="recipe123")

            db.session.add_all([saved_recipe1, saved_recipe2])
            db.session.commit()

            assert saved_recipe1.id != saved_recipe2.id
            assert saved_recipe1.user_id != saved_recipe2.user_id
            assert saved_recipe1.recipe_id == saved_recipe2.recipe_id


class TestPasswordResetTokenModel:
    """Test the PasswordResetToken model."""

    def test_password_reset_token_creation(self, client):
        """Test creating a PasswordResetToken instance."""
        with client.application.app_context():
            # Create user first
            user = User(
                email_address="test@example.com",
                full_name="Test User",
                password_hash="hashed_password",
            )
            db.session.add(user)
            db.session.commit()

            # Create password reset token
            expires_at = datetime.utcnow() + timedelta(hours=1)
            reset_token = PasswordResetToken(
                user_id=user.user_id, token="test-token-123", expires_at=expires_at
            )

            db.session.add(reset_token)
            db.session.commit()

            assert reset_token.id is not None
            assert reset_token.user_id == user.user_id
            assert reset_token.token == "test-token-123"
            assert reset_token.expires_at == expires_at
            assert reset_token.used is False  # Default value
            assert reset_token.created_at is not None
            assert isinstance(reset_token.created_at, datetime)

    def test_password_reset_token_used_flag(self, client):
        """Test the used flag functionality."""
        with client.application.app_context():
            # Create user
            user = User(
                email_address="test@example.com",
                full_name="Test User",
                password_hash="hashed_password",
            )
            db.session.add(user)
            db.session.commit()

            # Create reset token
            reset_token = PasswordResetToken(
                user_id=user.user_id,
                token="test-token-123",
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            db.session.add(reset_token)
            db.session.commit()

            # Mark as used
            reset_token.used = True
            db.session.commit()

            assert reset_token.used is True

    def test_password_reset_token_unique_token(self, client):
        """Test that tokens must be unique."""
        with client.application.app_context():
            # Create users
            user1 = User(
                email_address="user1@example.com",
                full_name="User One",
                password_hash="hashed_password",
            )
            user2 = User(
                email_address="user2@example.com",
                full_name="User Two",
                password_hash="hashed_password",
            )
            db.session.add_all([user1, user2])
            db.session.commit()

            # Create first token
            reset_token1 = PasswordResetToken(
                user_id=user1.user_id,
                token="unique-token-123",
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            db.session.add(reset_token1)
            db.session.commit()

            # Try to create second token with same token string
            reset_token2 = PasswordResetToken(
                user_id=user2.user_id,
                token="unique-token-123",  # Same token
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            db.session.add(reset_token2)

            with pytest.raises(Exception):  # IntegrityError or similar
                db.session.commit()


class TestPasswordResetRequestLogModel:
    """Test the PasswordResetRequestLog model."""

    def test_password_reset_request_log_creation(self, client):
        """Test creating a PasswordResetRequestLog instance."""
        with client.application.app_context():
            log_entry = PasswordResetRequestLog(email="test@example.com", ip="192.168.1.1")

            db.session.add(log_entry)
            db.session.commit()

            assert log_entry.id is not None
            assert log_entry.email == "test@example.com"
            assert log_entry.ip == "192.168.1.1"
            assert log_entry.created_at is not None
            assert isinstance(log_entry.created_at, datetime)

    def test_password_reset_request_log_with_none_email(self, client):
        """Test creating a log entry with None email."""
        with client.application.app_context():
            log_entry = PasswordResetRequestLog(email=None, ip="192.168.1.1")

            db.session.add(log_entry)
            db.session.commit()

            assert log_entry.id is not None
            assert log_entry.email is None
            assert log_entry.ip == "192.168.1.1"

    def test_password_reset_request_log_multiple_entries(self, client):
        """Test creating multiple log entries."""
        with client.application.app_context():
            log_entry1 = PasswordResetRequestLog(email="user1@example.com", ip="192.168.1.1")
            log_entry2 = PasswordResetRequestLog(email="user2@example.com", ip="192.168.1.2")

            db.session.add_all([log_entry1, log_entry2])
            db.session.commit()

            assert log_entry1.id != log_entry2.id
            assert log_entry1.email != log_entry2.email
            assert log_entry1.ip != log_entry2.ip
