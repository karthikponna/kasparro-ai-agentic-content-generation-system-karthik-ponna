import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.exceptions import (
    WorkflowBaseException,
    ValidationError,
    LLMError,
    ParsingError,
    ContentGenerationError
)


class TestWorkflowBaseException:
    """Tests for WorkflowBaseException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = WorkflowBaseException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.context == {}
    
    def test_exception_with_context(self):
        """Test exception with context."""
        exc = WorkflowBaseException("Test error", {"key": "value"})
        assert "key=value" in str(exc)
        assert exc.context == {"key": "value"}


class TestValidationError:
    """Tests for ValidationError."""
    
    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from WorkflowBaseException."""
        exc = ValidationError("Validation failed")
        assert isinstance(exc, WorkflowBaseException)
    
    def test_validation_error_with_context(self):
        """Test ValidationError with context."""
        exc = ValidationError("Missing field", {"field": "product_name"})
        assert "field=product_name" in str(exc)


class TestLLMError:
    """Tests for LLMError."""
    
    def test_llm_error_inheritance(self):
        """Test LLMError inherits from WorkflowBaseException."""
        exc = LLMError("API call failed")
        assert isinstance(exc, WorkflowBaseException)
    
    def test_llm_error_with_product_context(self):
        """Test LLMError with product context."""
        exc = LLMError("Rate limit exceeded", {"product": "Test Serum"})
        assert exc.context["product"] == "Test Serum"


class TestParsingError:
    """Tests for ParsingError."""
    
    def test_parsing_error_inheritance(self):
        """Test ParsingError inherits from WorkflowBaseException."""
        exc = ParsingError("Parse failed")
        assert isinstance(exc, WorkflowBaseException)


class TestContentGenerationError:
    """Tests for ContentGenerationError."""
    
    def test_content_generation_error_inheritance(self):
        """Test ContentGenerationError inherits from WorkflowBaseException."""
        exc = ContentGenerationError("Generation failed")
        assert isinstance(exc, WorkflowBaseException)
