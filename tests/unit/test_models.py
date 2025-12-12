import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.models import (
    ProductData,
    Question,
    QuestionCategory,
    ContentBlock,
    QAPair,
    FAQPage,
    ProductSection,
    ProductPage,
    ComparisonFeature,
    ComparisonPage,
    WorkflowState
)


class TestProductData:
    """Tests for ProductData model."""
    
    def test_product_data_creation(self, sample_product_data_dict):
        """Test ProductData creation with valid data."""
        product = ProductData(**sample_product_data_dict)
        
        assert product.product_name == "GlowBoost Vitamin C Serum"
        assert product.concentration == "10% Vitamin C"
        assert len(product.skin_type) == 2
    
    def test_product_data_serialization(self, sample_product_data):
        """Test ProductData can be serialized to dict."""
        data = sample_product_data.model_dump()
        
        assert "product_name" in data
        assert "skin_type" in data
        assert isinstance(data["skin_type"], list)


class TestQuestion:
    """Tests for Question model."""
    
    def test_question_creation(self):
        """Test Question creation."""
        q = Question(
            question="What is the concentration?",
            category=QuestionCategory.INFORMATIONAL
        )
        
        assert q.question == "What is the concentration?"
        assert q.category == QuestionCategory.INFORMATIONAL
    
    def test_all_question_categories(self):
        """Test all question categories are valid."""
        categories = [
            QuestionCategory.INFORMATIONAL,
            QuestionCategory.SAFETY,
            QuestionCategory.USAGE,
            QuestionCategory.PURCHASE,
            QuestionCategory.COMPARISON,
            QuestionCategory.INGREDIENTS,
            QuestionCategory.BENEFITS
        ]
        
        for cat in categories:
            q = Question(question="Test", category=cat)
            assert q.category == cat


class TestContentBlock:
    """Tests for ContentBlock model."""
    
    def test_content_block_creation(self):
        """Test ContentBlock creation."""
        block = ContentBlock(
            block_type="benefits",
            content="This product provides great benefits.",
            metadata={"count": 3}
        )
        
        assert block.block_type == "benefits"
        assert "great benefits" in block.content
        assert block.metadata["count"] == 3
    
    def test_content_block_without_metadata(self):
        """Test ContentBlock without metadata."""
        block = ContentBlock(
            block_type="usage",
            content="Apply daily."
        )
        
        assert block.metadata is None


class TestFAQPage:
    """Tests for FAQPage model."""
    
    def test_faq_page_minimum_questions(self):
        """Test FAQPage requires minimum 5 questions."""
        qa_pairs = [
            QAPair(question=f"Q{i}?", answer=f"A{i}", category="Informational")
            for i in range(5)
        ]
        
        faq = FAQPage(
            product_name="Test Product",
            total_questions=5,
            qa_pairs=qa_pairs,
            categories=["Informational"]
        )
        
        assert faq.total_questions == 5
        assert len(faq.qa_pairs) == 5


class TestWorkflowState:
    """Tests for WorkflowState model."""
    
    def test_workflow_state_initial(self, sample_product_data_dict):
        """Test initial WorkflowState."""
        state = WorkflowState(raw_product_data=sample_product_data_dict)
        
        assert state.raw_product_data == sample_product_data_dict
        assert state.product_data is None
        assert state.questions is None
        assert state.error is None
    
    def test_workflow_state_with_error(self, sample_product_data_dict):
        """Test WorkflowState with error."""
        state = WorkflowState(
            raw_product_data=sample_product_data_dict,
            error="Something went wrong"
        )
        
        assert state.error == "Something went wrong"
