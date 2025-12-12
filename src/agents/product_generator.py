from typing import Dict, Any, List
from loguru import logger
from exceptions import ValidationError, LLMError, ContentGenerationError
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI

from models import ProductPage, ProductSection, WorkflowState
from utils.prompt_loader import load_prompt
from utils.llm_factory import create_structured_llm, invoke_with_retry


class ProductPageContent(BaseModel):
    """Structured product page content."""
    tagline: str = Field(..., description="Compelling tagline for the product (max 150 characters)")
    overview: str = Field(..., description="Engaging overview section introducing the product")
    pricing_content: str = Field(..., description="Pricing section with value proposition")


def generate_product_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate comprehensive product page using AI and content blocks.
    
    Args:
        state: Current workflow state with product data and content blocks
        
    Returns:
        Updated state with AI-generated product page
        
    Raises:
        ValidationError: If required data is missing
        LLMError: If LLM API call fails
    """

    try:
        product_data = state.product_data
        content_blocks = state.content_blocks
        
        if not product_data or not content_blocks:
            raise ValidationError(
                "Missing required data (product_data or content_blocks)",
                {"agent": "product_generator"}
            )
        
        logger.info(f"Generating product page for: {product_data.product_name}")
        

        # Initialize LLM with structured output using factory
        structured_llm = create_structured_llm(ProductPageContent)
        

        # Load prompt from YAML
        prompt = load_prompt("product_generator")
        

        chain = prompt | structured_llm
        try:
            result = invoke_with_retry(chain, {
                "product_name": product_data.product_name,
                "concentration": product_data.concentration,
                "skin_type": ", ".join(product_data.skin_type),
                "key_ingredients": ", ".join(product_data.key_ingredients),
                "benefits": ", ".join(product_data.benefits),
                "how_to_use": product_data.how_to_use,
                "side_effects": product_data.side_effects,
                "price": product_data.price
            })
        except Exception as e:
            # Wrap LLM errors
            if "openai" in str(type(e).__module__).lower() or "api" in str(e).lower():
                raise LLMError(
                    f"LLM API call failed: {str(e)}",
                    {"product": product_data.product_name}
                ) from e
            raise ContentGenerationError(f"Product page generation failed: {str(e)}") from e
        

        sections = [
            ProductSection(
                section_name="Overview",
                content=result.overview
            ),
            ProductSection(
                section_name="Benefits",
                content=content_blocks["benefits"].content
            ),
            ProductSection(
                section_name="Key Ingredients",
                content=content_blocks["ingredients"].content
            ),
            ProductSection(
                section_name="How to Use",
                content=content_blocks["usage"].content
            ),
            ProductSection(
                section_name="Safety Information",
                content=content_blocks["safety"].content
            ),
            ProductSection(
                section_name="Pricing",
                content=result.pricing_content
            )
        ]
        
        # create metadata
        metadata = {
            "concentration": product_data.concentration,
            "skin_types": product_data.skin_type,
            "key_ingredients": product_data.key_ingredients,
            "benefits": product_data.benefits,
            "how_to_use": product_data.how_to_use,
            "side_effects": product_data.side_effects,
            "price": product_data.price,
            "total_sections": len(sections),
            "content_block_metadata": {
                "benefits": content_blocks["benefits"].metadata,
                "usage": content_blocks["usage"].metadata,
                "ingredients": content_blocks["ingredients"].metadata,
                "safety": content_blocks["safety"].metadata
            }
        }
        
        # create product page
        product_page = ProductPage(
            product_name=product_data.product_name,
            tagline=result.tagline,
            sections=sections,
            metadata=metadata
        )
        
        logger.info(f"Successfully generated product page with {len(sections)} sections")
        return {"product_page": product_page}
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except LLMError as e:
        logger.error(f"LLM error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {str(e)}", exc_info=True)
        return {"error": str(e)}