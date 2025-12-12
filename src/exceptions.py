class WorkflowBaseException(Exception):
    """Base exception for all workflow-related errors."""
    
    def __init__(self, message: str, context: dict = None):
        """
        Initialize workflow exception with message and context.
        
        Args:
            message: Error message
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self):
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{self.message} (Context: {context_str})"
        return self.message


class ValidationError(WorkflowBaseException):
    """Raised when data validation fails (Pydantic validation, missing data, etc.)."""
    pass


class LLMError(WorkflowBaseException):
    """Raised when LLM/API communication fails."""
    pass


class ParsingError(WorkflowBaseException):
    """Raised when data parsing fails."""
    pass


class ContentGenerationError(WorkflowBaseException):
    """Raised when content generation fails."""
    pass
