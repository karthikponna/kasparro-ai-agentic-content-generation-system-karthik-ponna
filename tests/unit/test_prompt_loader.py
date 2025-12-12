import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.utils.prompt_loader import load_prompt
from langchain_core.prompts import ChatPromptTemplate


class TestPromptLoader:
    """Tests for prompt loader utility."""
    
    def test_load_question_generator_prompt(self):
        """Test loading question generator prompt."""
        prompt = load_prompt("question_generator")
        
        assert isinstance(prompt, ChatPromptTemplate)
        assert len(prompt.messages) == 2
    
    def test_load_content_logic_prompt(self):
        """Test loading content logic prompt."""
        prompt = load_prompt("content_logic")
        
        assert isinstance(prompt, ChatPromptTemplate)
    
    def test_load_faq_generator_prompt(self):
        """Test loading FAQ generator prompt."""
        prompt = load_prompt("faq_generator")
        
        assert isinstance(prompt, ChatPromptTemplate)
    
    def test_load_product_generator_prompt(self):
        """Test loading product generator prompt."""
        prompt = load_prompt("product_generator")
        
        assert isinstance(prompt, ChatPromptTemplate)
    
    def test_load_comparison_generator_fictional_prompt(self):
        """Test loading comparison generator fictional product prompt."""
        prompt = load_prompt("comparison_generator", "fictional_product")
        
        assert isinstance(prompt, ChatPromptTemplate)
    
    def test_load_comparison_generator_comparison_prompt(self):
        """Test loading comparison generator comparison page prompt."""
        prompt = load_prompt("comparison_generator", "comparison_page")
        
        assert isinstance(prompt, ChatPromptTemplate)
    
    def test_load_nonexistent_prompt_raises_error(self):
        """Test loading non-existent prompt raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent_agent")
    
    def test_load_invalid_prompt_key_raises_error(self):
        """Test loading invalid prompt key raises KeyError."""
        with pytest.raises(KeyError):
            load_prompt("comparison_generator", "invalid_key")
