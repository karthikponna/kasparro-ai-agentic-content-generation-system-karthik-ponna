import time
from typing import Type, TypeVar
from loguru import logger
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from config import settings
from exceptions import LLMError

T = TypeVar('T', bound=BaseModel)


def create_llm(temperature: float = None) -> ChatOpenAI:
    """
    Create a ChatOpenAI instance with centralized configuration.
    
    Args:
        temperature: Optional override for temperature setting.
        
    Returns:
        Configured ChatOpenAI instance.
    """
    return ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )


def create_structured_llm(output_schema: Type[T], temperature: float = None) -> ChatOpenAI:
    """
    Create a ChatOpenAI instance with structured output support.
    
    Args:
        output_schema: Pydantic model class for structured output.
        temperature: Optional override for temperature setting.
        
    Returns:
        ChatOpenAI instance configured for structured output.
    """
    llm = create_llm(temperature)
    return llm.with_structured_output(output_schema)


def invoke_with_retry(chain, inputs: dict, max_retries: int = None, retry_delay: float = None) -> T:
    """
    Invoke an LLM chain with retry mechanism for transient errors.
    
    Args:
        chain: The LangChain chain to invoke.
        inputs: Input dictionary for the chain.
        max_retries: Maximum retry attempts (defaults to config setting).
        retry_delay: Delay between retries in seconds (defaults to config setting).
        
    Returns:
        The chain result.
        
    Raises:
        LLMError: If all retries are exhausted.
    """
    max_retries = max_retries if max_retries is not None else settings.LLM_MAX_RETRIES
    retry_delay = retry_delay if retry_delay is not None else settings.LLM_RETRY_DELAY
    
    last_exception = None
    
    for attempt in range(1, max_retries + 1):
        try:
            result = chain.invoke(inputs)
            return result
            
        except Exception as e:
            last_exception = e
            error_str = str(e).lower()
            
            # Check if it's a transient error worth retrying
            is_transient = any(keyword in error_str for keyword in [
                'rate_limit', 'ratelimit', 'timeout', 'connection', 
                'temporarily', '429', '503', '502', 'overloaded'
            ])
            
            if is_transient and attempt < max_retries:
                logger.warning(
                    f"Transient LLM error (attempt {attempt}/{max_retries}): {str(e)}. "
                    f"Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay * attempt)  # Exponential backoff
                continue
            
            # Non-transient error or last attempt
            if attempt == max_retries:
                logger.error(f"LLM call failed after {max_retries} attempts: {str(e)}")
            
            raise
    
    # Should not reach here, but just in case
    raise LLMError(f"LLM call failed after {max_retries} attempts: {str(last_exception)}")
