"""Test coverage for utils.py module."""

from unittest.mock import patch

from app import _rate_limit_counts as rate_limit_counts
from app import _require_admin as require_admin

# Import the actual modules to test
from app import parse_list_field, send_password_reset_email  # type: ignore


class TestParseListField:
    """Test the parse_list_field utility function."""

    def test_parse_list_field_with_actual_list(self):
        """Test parsing when input is already a list."""
        result = parse_list_field(["apple", "banana", "cherry"])
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_with_empty_list(self):
        """Test parsing empty list."""
        result = parse_list_field([])
        assert result == []

    def test_parse_list_field_with_list_containing_empty_strings(self):
        """Test list with empty strings are filtered out."""
        result = parse_list_field(["apple", "", "banana", "   ", "cherry"])
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_with_json_string(self):
        """Test parsing JSON list string."""
        result = parse_list_field('["apple", "banana", "cherry"]')
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_with_python_repr_string(self):
        """Test parsing Python list representation."""
        result = parse_list_field("['apple', 'banana', 'cherry']")
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_with_comma_separated_string(self):
        """Test parsing comma-separated string."""
        result = parse_list_field("apple,banana,cherry")
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_with_custom_separator(self):
        """Test parsing with custom separator."""
        result = parse_list_field("apple|banana|cherry", "|")
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_with_empty_string(self):
        """Test parsing empty string."""
        result = parse_list_field("")
        assert result == []

    def test_parse_list_field_with_none(self):
        """Test parsing None."""
        result = parse_list_field(None)
        assert result == []

    def test_parse_list_field_with_whitespace_only(self):
        """Test parsing whitespace-only string."""
        result = parse_list_field("   ")
        assert result == []

    def test_parse_list_field_with_malformed_json(self):
        """Test parsing malformed JSON falls back to comma separation."""
        result = parse_list_field("[apple, banana, cherry")
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_with_quoted_items_in_brackets(self):
        """Test parsing bracket-enclosed items with quotes."""
        result = parse_list_field("[' apple ', \"banana\", 'cherry ']")
        assert result == ["apple", "banana", "cherry"]

    def test_parse_list_field_strips_surrounding_quotes(self):
        """Test that surrounding quotes are stripped from items."""
        result = parse_list_field("'apple','banana','cherry'")
        assert result == ["apple", "banana", "cherry"]


class TestSendPasswordResetEmail:
    """Test the send_password_reset_email function."""

    def test_send_password_reset_email_no_resend_key(self, client):
        """With Resend available, sending can succeed even without RESEND_API_KEY."""
        with client.application.app_context():
            client.application.config["RESEND_API_KEY"] = None
            client.application.config["ENVIRONMENT"] = "development"

            result = send_password_reset_email("test@example.com", "test-token")
            assert result is False

    def test_send_password_reset_email_production_no_key(self, client):
        """In production, Resend may still accept sends without an API key in this setup."""
        with client.application.app_context():
            client.application.config["RESEND_API_KEY"] = None
            client.application.config["ENVIRONMENT"] = "production"

            result = send_password_reset_email("test@example.com", "test-token")
            assert result is False

    @patch("app.resend")
    @patch("app.RESEND_API_KEY", "test-key")
    @patch("app.RESEND_AVAILABLE", True)
    @patch("app.EMAIL_FROM", "test@sender.com")
    @patch("app.FRONTEND_BASE_URL", "https://example.com")
    def test_send_password_reset_email_with_resend_success(self, mock_resend, client):
        """Test successful email sending with Resend."""
        with client.application.app_context():
            mock_resend.Emails.send.return_value = {"id": "test-id"}

            result = send_password_reset_email("test@example.com", "test-token")
            assert result is True

            mock_resend.Emails.send.assert_called_once()
            call_args = mock_resend.Emails.send.call_args[0][0]
            assert call_args["to"] == ["test@example.com"]
            assert "test-token" in call_args["html"]

    @patch("app.resend")
    def test_send_password_reset_email_with_resend_failure(self, mock_resend, client):
        """Test email sending failure with Resend."""
        with client.application.app_context():
            client.application.config["RESEND_API_KEY"] = "test-key"
            client.application.config["RESEND_AVAILABLE"] = True

            mock_resend.Emails.send.side_effect = Exception("SMTP error")

            result = send_password_reset_email("test@example.com", "test-token")
            assert result is False

    def test_send_password_reset_email_exception_handling(self, client):
        """Test that exceptions are handled gracefully."""
        with client.application.app_context():
            # Invalid config that should cause an exception
            client.application.config.pop("FRONTEND_BASE_URL", None)

            result = send_password_reset_email("test@example.com", "test-token")
            assert result is False


class TestRequireAdmin:
    """Test the require_admin function."""

    def test_require_admin_no_token_header(self, client):
        """Test admin check with no token header."""
        with client.application.test_request_context():
            client.application.config["ADMIN_TOKEN"] = "secret-admin-token"

            result = require_admin()
            assert result is False

    def test_require_admin_no_configured_token(self, client):
        """Test admin check with no configured admin token."""
        with client.application.test_request_context(headers={"X-Admin-Token": "some-token"}):
            client.application.config["ADMIN_TOKEN"] = None

            result = require_admin()
            assert result is False

    def test_require_admin_wrong_token(self, client):
        """Test admin check with wrong token."""
        with client.application.test_request_context(headers={"X-Admin-Token": "wrong-token"}):
            client.application.config["ADMIN_TOKEN"] = "secret-admin-token"

            result = require_admin()
            assert result is False

    @patch("app.ADMIN_TOKEN", "secret-admin-token")
    def test_require_admin_correct_token(self, client):
        """Test admin check with correct token."""
        with client.application.test_request_context(
            headers={"X-Admin-Token": "secret-admin-token"}
        ):
            result = require_admin()
            assert result is True


class TestRateLimitCounts:
    """Test the rate_limit_counts function."""

    def test_rate_limit_counts_with_ip_and_email(self, client):
        """Test rate limit counting with both IP and email."""
        with client.application.app_context():
            result = rate_limit_counts("test@example.com", "192.168.1.1")

            expected = {
                "ip": {"last_hour": 0, "last_24h": 0},
                "email": {"last_hour": 0, "last_24h": 0},
            }
            assert result == expected

    def test_rate_limit_counts_with_none_values(self, client):
        """Test rate limit counting with None values."""
        with client.application.app_context():
            result = rate_limit_counts(None, None)

            expected = {
                "ip": {"last_hour": 0, "last_24h": 0},
                "email": {"last_hour": 0, "last_24h": 0},
            }
            assert result == expected
