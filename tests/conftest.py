import os
import sys
import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models import (
    ProductData, 
    WorkflowState, 
    Question, 
    QuestionCategory,
    ContentBlock,
    QAPair,
    FAQPage,
    ProductSection,
    ProductPage,
    ComparisonFeature,
    ComparisonPage
)


@pytest.fixture
def sample_product_data_dict():
    """Sample raw product data dictionary."""
    return {
        "product_name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": ["Oily", "Combination"],
        "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
        "benefits": ["Brightening", "Fades dark spots"],
        "how_to_use": "Apply 2-3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }


@pytest.fixture
def sample_product_data(sample_product_data_dict):
    """Sample parsed ProductData model."""
    return ProductData(**sample_product_data_dict)


@pytest.fixture
def sample_workflow_state(sample_product_data_dict):
    """Sample workflow state with raw product data."""
    return WorkflowState(raw_product_data=sample_product_data_dict)


@pytest.fixture
def sample_workflow_state_with_product_data(sample_product_data_dict, sample_product_data):
    """Sample workflow state with parsed product data."""
    return WorkflowState(
        raw_product_data=sample_product_data_dict,
        product_data=sample_product_data
    )


@pytest.fixture
def sample_questions():
    """Sample list of questions."""
    return [
        Question(question="What is the concentration?", category=QuestionCategory.INFORMATIONAL),
        Question(question="Is it safe for sensitive skin?", category=QuestionCategory.SAFETY),
        Question(question="How do I apply it?", category=QuestionCategory.USAGE),
        Question(question="What is the price?", category=QuestionCategory.PURCHASE),
        Question(question="How does it compare to other serums?", category=QuestionCategory.COMPARISON),
        Question(question="What are the key ingredients?", category=QuestionCategory.INGREDIENTS),
        Question(question="What are the benefits?", category=QuestionCategory.BENEFITS),
        Question(question="Can I use it with other products?", category=QuestionCategory.USAGE),
        Question(question="What skin types is it for?", category=QuestionCategory.INFORMATIONAL),
        Question(question="Are there any side effects?", category=QuestionCategory.SAFETY),
        Question(question="How long until I see results?", category=QuestionCategory.BENEFITS),
        Question(question="Is it worth the price?", category=QuestionCategory.PURCHASE),
        Question(question="What makes it different?", category=QuestionCategory.COMPARISON),
        Question(question="What does Vitamin C do?", category=QuestionCategory.INGREDIENTS),
        Question(question="How often should I use it?", category=QuestionCategory.USAGE),
    ]


@pytest.fixture
def sample_content_blocks():
    """Sample content blocks."""
    return {
        "benefits": ContentBlock(
            block_type="benefits",
            content="This serum provides brightening effects and fades dark spots.",
            metadata={"benefit_count": 2}
        ),
        "usage": ContentBlock(
            block_type="usage",
            content="Apply 2-3 drops after cleansing, before sunscreen.",
            metadata={"skin_types": ["Oily", "Combination"]}
        ),
        "ingredients": ContentBlock(
            block_type="ingredients",
            content="Contains 10% Vitamin C and Hyaluronic Acid.",
            metadata={"ingredient_count": 2}
        ),
        "safety": ContentBlock(
            block_type="safety",
            content="May cause mild tingling for sensitive skin. Patch test recommended.",
            metadata={"side_effects": "Mild tingling for sensitive skin"}
        )
    }


@pytest.fixture
def sample_fictional_product_b():
    """Sample fictional product B for comparison."""
    return {
        "product_name": "RadiancePro Vitamin C Elixir",
        "concentration": "15% Vitamin C",
        "skin_type": ["Normal", "Dry"],
        "key_ingredients": ["Vitamin C", "Niacinamide"],
        "benefits": ["Anti-aging", "Hydrating"],
        "price": "₹899"
    }


@pytest.fixture
def empty_workflow_state():
    """Empty workflow state for error testing."""
    return WorkflowState(raw_product_data={})
