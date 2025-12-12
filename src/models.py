from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class QuestionCategory(str, Enum):
    """Categories for user questions."""
    INFORMATIONAL = "Informational"
    SAFETY = "Safety"
    USAGE = "Usage"
    PURCHASE = "Purchase"
    COMPARISON = "Comparison"
    INGREDIENTS = "Ingredients"
    BENEFITS = "Benefits"


class ProductData(BaseModel):
    """Structured product information model."""
    product_name: str = Field(..., description="Name of the product")
    concentration: str = Field(..., description="Active ingredient concentration")
    skin_type: List[str] = Field(..., description="Suitable skin types")
    key_ingredients: List[str] = Field(..., description="Key ingredients list")
    benefits: List[str] = Field(..., description="Product benefits")
    how_to_use: str = Field(..., description="Usage instructions")
    side_effects: str = Field(..., description="Potential side effects")
    price: str = Field(..., description="Product price")


class Question(BaseModel):
    """User question with category."""
    question: str = Field(..., description="The question text")
    category: QuestionCategory = Field(..., description="Question category")


class ContentBlock(BaseModel):
    """Reusable content transformation block."""
    block_type: str = Field(..., description="Type of content block")
    content: str = Field(..., description="Generated content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class QAPair(BaseModel):
    """Question and answer pair for FAQ."""
    question: str = Field(..., description="Question text")
    answer: str = Field(..., description="Answer text")
    category: QuestionCategory = Field(..., description="Question category")


class FAQPage(BaseModel):
    """FAQ page structure."""
    page_type: str = Field(default="FAQ", description="Page type identifier")
    product_name: str = Field(..., description="Product name")
    total_questions: int = Field(..., description="Total number of Q&A pairs")
    qa_pairs: List[QAPair] = Field(..., description="List of Q&A pairs", min_length=5)
    categories: List[str] = Field(..., description="List of categories covered")


class ProductSection(BaseModel):
    """Section in product page."""
    section_name: str = Field(..., description="Section name")
    content: str = Field(..., description="Section content")


class ProductPage(BaseModel):
    """Product page structure."""
    page_type: str = Field(default="Product", description="Page type identifier")
    product_name: str = Field(..., description="Product name")
    tagline: str = Field(..., description="Product tagline")
    sections: List[ProductSection] = Field(..., description="Product page sections")
    metadata: Dict[str, Any] = Field(..., description="Product metadata")


class ComparisonFeature(BaseModel):
    """Feature comparison between products."""
    feature_name: str = Field(..., description="Feature being compared")
    product_a_value: str = Field(..., description="Value for Product A")
    product_b_value: str = Field(..., description="Value for Product B")
    winner: Optional[str] = Field(default=None, description="Which product is better for this feature")


class ComparisonPage(BaseModel):
    """Comparison page structure."""
    page_type: str = Field(default="Comparison", description="Page type identifier")
    product_a: Dict[str, Any] = Field(..., description="Product A details")
    product_b: Dict[str, Any] = Field(..., description="Product B details")
    comparison_matrix: List[ComparisonFeature] = Field(..., description="Feature comparison matrix")
    summary: str = Field(..., description="Comparison summary")
    recommendation: str = Field(..., description="Recommendation based on comparison")


class WorkflowState(BaseModel):
    """LangGraph workflow state."""
    
    # input
    raw_product_data: Dict[str, Any] = Field(..., description="Raw product data input")

    product_data: Optional[ProductData] = Field(default=None, description="Parsed product data")
    questions: Optional[List[Question]] = Field(default=None, description="Generated questions")
    content_blocks: Optional[Dict[str, ContentBlock]] = Field(default=None, description="Content blocks")
    fictional_product_b: Optional[Dict[str, Any]] = Field(default=None, description="Fictional product for comparison")
    
    # Outputs
    faq_page: Optional[FAQPage] = Field(default=None, description="Generated FAQ page")
    product_page: Optional[ProductPage] = Field(default=None, description="Generated product page")
    comparison_page: Optional[ComparisonPage] = Field(default=None, description="Generated comparison page")
    
    # Control
    error: Optional[str] = Field(default=None, description="Error message if any")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True