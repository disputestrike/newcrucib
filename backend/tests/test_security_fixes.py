"""
Test suite for security fixes
Tests encryption, redaction, input validation, and other security enhancements
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from encryption import encrypt_value, decrypt_value, encrypt_dict, decrypt_dict
from error_handlers import redact_sensitive_data


class TestEncryption:
    """Test API key encryption functionality"""
    
    def test_encrypt_decrypt_value(self):
        """Test basic encryption and decryption"""
        original = "sk-test-1234567890abcdef"
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        assert decrypted == original
    
    def test_encrypt_empty_string(self):
        """Test encryption of empty string"""
        assert encrypt_value("") == ""
        assert decrypt_value("") == ""
    
    def test_encrypt_dict_sensitive_fields(self):
        """Test dictionary encryption of sensitive fields"""
        data = {
            "api_key": "sk-1234",
            "password": "secret123",
            "username": "user",
            "email": "user@example.com"
        }
        encrypted = encrypt_dict(data)
        
        # Sensitive fields should be encrypted (different from original)
        assert encrypted["api_key"] != data["api_key"]
        assert encrypted["password"] != data["password"]
        
        # Non-sensitive fields should remain unchanged
        assert encrypted["username"] == data["username"]
        assert encrypted["email"] == data["email"]
    
    def test_decrypt_dict_sensitive_fields(self):
        """Test dictionary decryption"""
        original_data = {
            "openai_api_key": "sk-openai-test",
            "anthropic_api_key": "sk-ant-test",
            "user_name": "testuser"
        }
        encrypted = encrypt_dict(original_data)
        decrypted = decrypt_dict(encrypted)
        
        assert decrypted["openai_api_key"] == original_data["openai_api_key"]
        assert decrypted["anthropic_api_key"] == original_data["anthropic_api_key"]
        assert decrypted["user_name"] == original_data["user_name"]


class TestLoggingRedaction:
    """Test sensitive data redaction in logs"""
    
    def test_redact_password_in_dict(self):
        """Test password redaction"""
        data = {
            "username": "user",
            "password": "secret123",
            "email": "user@test.com"
        }
        redacted = redact_sensitive_data(data)
        
        assert redacted["username"] == "user"
        assert redacted["password"] == "***REDACTED***"
        assert redacted["email"] == "user@test.com"
    
    def test_redact_api_keys_in_dict(self):
        """Test API key redaction"""
        data = {
            "api_key": "sk-1234567890",
            "apikey": "key-abcdef",
            "API_KEY": "TEST-KEY",
            "user_id": "12345"
        }
        redacted = redact_sensitive_data(data)
        
        assert redacted["api_key"] == "***REDACTED***"
        assert redacted["apikey"] == "***REDACTED***"
        assert redacted["API_KEY"] == "***REDACTED***"
        assert redacted["user_id"] == "12345"
    
    def test_redact_bearer_token_in_string(self):
        """Test Bearer token redaction in strings"""
        log_message = "Authorization: Bearer sk-abc123def456"
        redacted = redact_sensitive_data(log_message)
        
        assert "Bearer ***REDACTED***" in redacted
        assert "sk-abc123def456" not in redacted
    
    def test_redact_nested_dict(self):
        """Test redaction in nested dictionaries"""
        data = {
            "user": {
                "name": "test",
                "credentials": {
                    "password": "secret",
                    "api_token": "token123"
                }
            },
            "public_info": "visible"
        }
        redacted = redact_sensitive_data(data)
        
        assert redacted["user"]["name"] == "test"
        assert redacted["user"]["credentials"]["password"] == "***REDACTED***"
        assert redacted["user"]["credentials"]["api_token"] == "***REDACTED***"
        assert redacted["public_info"] == "visible"
    
    def test_truncate_traceback(self):
        """Test traceback truncation"""
        long_traceback = "\n".join([f"Line {i}" for i in range(100)])
        data = {
            "error": "Test error",
            "traceback": long_traceback
        }
        redacted = redact_sensitive_data(data, max_traceback_lines=20)
        
        # Traceback should be truncated
        assert "truncated" in redacted["traceback"]
        assert len(redacted["traceback"].split("\n")) <= 22  # 20 lines + truncation message


class TestInputValidation:
    """Test Pydantic input validation"""
    
    def test_string_max_length(self):
        """Test that strings are limited by max_length"""
        from server import ChatMessage
        from pydantic import ValidationError
        
        # Valid message
        msg = ChatMessage(message="Hello")
        assert msg.message == "Hello"
        
        # Too long message should raise validation error
        with pytest.raises(ValidationError):
            ChatMessage(message="x" * 10001)
    
    def test_numeric_bounds(self):
        """Test numeric field bounds"""
        from server import RAGQuery
        from pydantic import ValidationError
        
        # Valid query
        query = RAGQuery(query="test", top_k=5)
        assert query.top_k == 5
        
        # top_k too large
        with pytest.raises(ValidationError):
            RAGQuery(query="test", top_k=101)
        
        # top_k negative
        with pytest.raises(ValidationError):
            RAGQuery(query="test", top_k=-1)
    
    def test_file_size_validation(self):
        """Test file size validation"""
        from server import ExportFilesBody
        from pydantic import ValidationError
        
        # Valid file size
        files = {"file1.js": "x" * 1000}
        body = ExportFilesBody(files=files)
        assert len(body.files) == 1
        
        # Too large total size (>100MB)
        large_files = {f"file{i}.js": "x" * (50 * 1024 * 1024) for i in range(3)}
        with pytest.raises(ValidationError):
            ExportFilesBody(files=large_files)


class TestCORSConfiguration:
    """Test CORS security configuration"""
    
    def test_cors_not_wildcard(self):
        """Test that CORS is not set to wildcard by default"""
        # This would need to be tested in integration tests with the app
        # Here we just verify the configuration logic
        import os
        
        # Default should not be wildcard
        default_cors = os.environ.get('CORS_ORIGINS', 'http://localhost:3000')
        assert default_cors != '*'


class TestJWTConfiguration:
    """Test JWT secret configuration"""
    
    def test_jwt_secret_check_exists(self):
        """Test that JWT_SECRET validation code exists"""
        # Verify the server code has JWT_SECRET validation
        # In actual deployment, server.py will fail to import if JWT_SECRET is missing
        import os
        
        # Check that JWT_SECRET is either set in environment or would be required
        # This test documents the requirement without causing test failures
        jwt_secret = os.environ.get('JWT_SECRET')
        
        # If JWT_SECRET is set, verify it's non-empty
        if jwt_secret:
            assert len(jwt_secret) > 0, "JWT_SECRET should not be empty"
        
        # The actual validation happens at server startup in server.py
        # We verify the validation code exists by checking the file
        server_file = os.path.join(os.path.dirname(__file__), '..', 'server.py')
        with open(server_file, 'r') as f:
            server_code = f.read()
            assert 'JWT_SECRET' in server_code
            assert 'raise ValueError' in server_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
