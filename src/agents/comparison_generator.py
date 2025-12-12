from typing import Dict, Any, List
from loguru import logger
from exceptions import ValidationError, LLMError, ContentGenerationError
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI

from models import ComparisonPage, ComparisonFeature, WorkflowState
from utils.prompt_loader import load_prompt
from utils.llm_factory import create_structured_llm, invoke_with_retry
from config import settings


class FictionalProduct(BaseModel):
    """Fictional product for comparison."""
    product_name: str = Field(..., description="Product name")
    concentration: str = Field(..., description="Active ingredient concentration")
    skin_type: List[str] = Field(..., description="Suitable skin types")
    key_ingredients: List[str] = Field(..., description="Key ingredients")
    benefits: List[str] = Field(..., description="Product benefits")
    price: str = Field(..., description="Product price")


class ComparisonAnalysis(BaseModel):
    """Comparison analysis structure."""
    comparison_matrix: List[ComparisonFeature] = Field(..., description="Feature comparison matrix")
    summary: str = Field(..., description="Comparison summary")
    recommendation: str = Field(..., description="Recommendation")


def generate_fictional_product_b(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate fictional Product B for comparison.
    
    Args:
        state: Current workflow state with product data
        
    Returns:
        Updated state with fictional Product B
        
    Raises:
        ValidationError: If product data is missing
        LLMError: If LLM API call fails
    """
    try:
        product_data = state.product_data
        if not product_data:
            raise ValidationError(
                "No product data available",
                {"agent": "comparison_generator", "function": "generate_fictional_product_b"}
            )
        
        logger.info(f"Generating fictional competitor for: {product_data.product_name}")
        

        # Initialize LLM with structured output using factory
        structured_llm = create_structured_llm(FictionalProduct)
        

        # Load prompt from YAML
        prompt = load_prompt("comparison_generator", "fictional_product")
        

        chain = prompt | structured_llm
        try:
            fictional_product = invoke_with_retry(chain, {
                "product_name": product_data.product_name,
                "concentration": product_data.concentration,
                "skin_type": ", ".join(product_data.skin_type),
                "key_ingredients": ", ".join(product_data.key_ingredients),
                "benefits": ", ".join(product_data.benefits),
                "price": product_data.price
            })
        except Exception as e:
            if "openai" in str(type(e).__module__).lower() or "api" in str(e).lower():
                raise LLMError(
                    f"LLM API call failed: {str(e)}",
                    {"product": product_data.product_name}
                ) from e
            raise ContentGenerationError(f"Fictional product generation failed: {str(e)}") from e
        
        # Return Pydantic model directly as dict
        fictional_product_dict = fictional_product.model_dump()
        
        logger.info(f"Successfully generated fictional product: {fictional_product.product_name}")
        return {"fictional_product_b": fictional_product_dict}
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except LLMError as e:
        logger.error(f"LLM error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {str(e)}", exc_info=True)
        return {"error": str(e)}


def generate_comparison_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate comparison page between Product A and Product B.
    
    Args:
        state: Current workflow state with both products
        
    Returns:
        Updated state with comparison page
        
    Raises:
        ValidationError: If product data is missing
        LLMError: If LLM API call fails
    """
    try:
        product_data = state.product_data
        fictional_product_b = state.fictional_product_b
        
        if not product_data or not fictional_product_b:
            raise ValidationError(
                "Missing product data for comparison",
                {"agent": "comparison_generator", "function": "generate_comparison_page"}
            )
        
        logger.info(f"Generating comparison page: {product_data.product_name} vs {fictional_product_b['product_name']}")
        

        # Initialize LLM with structured output using factory
        structured_llm = create_structured_llm(ComparisonAnalysis)
        

        # Load prompt from YAML
        prompt = load_prompt("comparison_generator", "comparison_page")
        
        # generate comparison
        chain = prompt | structured_llm
        try:
            comparison = invoke_with_retry(chain, {
                "product_a_name": product_data.product_name,
                "product_a_concentration": product_data.concentration,
                "product_a_skin_type": ", ".join(product_data.skin_type),
                "product_a_ingredients": ", ".join(product_data.key_ingredients),
                "product_a_benefits": ", ".join(product_data.benefits),
                "product_a_price": product_data.price,
                "product_b_name": fictional_product_b["product_name"],
                "product_b_concentration": fictional_product_b["concentration"],
                "product_b_skin_type": ", ".join(fictional_product_b["skin_type"]),
                "product_b_ingredients": ", ".join(fictional_product_b["key_ingredients"]),
                "product_b_benefits": ", ".join(fictional_product_b["benefits"]),
                "product_b_price": fictional_product_b["price"]
            })
        except Exception as e:
            if "openai" in str(type(e).__module__).lower() or "api" in str(e).lower():
                raise LLMError(
                    f"LLM API call failed: {str(e)}",
                    {"product_a": product_data.product_name, "product_b": fictional_product_b["product_name"]}
                ) from e
            raise ContentGenerationError(f"Comparison page generation failed: {str(e)}") from e
        
        # create product dictionaries for the page
        product_a_dict = product_data.model_dump()
        
        # create comparison page
        comparison_page = ComparisonPage(
            product_a=product_a_dict,
            product_b=fictional_product_b,
            comparison_matrix=comparison.comparison_matrix,
            summary=comparison.summary,
            recommendation=comparison.recommendation
        )
        
        logger.info(f"Successfully generated comparison page with {len(comparison.comparison_matrix)} comparison features")

        return {"comparison_page": comparison_page}
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except LLMError as e:
        logger.error(f"LLM error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
