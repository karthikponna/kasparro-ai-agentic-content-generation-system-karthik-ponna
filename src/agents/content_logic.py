from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import ContentBlock, ProductData, WorkflowState
from pydantic import BaseModel, Field


class ContentBlockList(BaseModel):
    """List of content blocks for different sections."""
    benefits: str = Field(..., description="Benefits content block with rich, detailed descriptions")
    usage: str = Field(..., description="Usage instructions content block with clear, actionable steps")
    ingredients: str = Field(..., description="Ingredients content block with detailed explanations")
    safety: str = Field(..., description="Safety information content block with comprehensive precautions")


def create_content_blocks(state: WorkflowState) -> Dict[str, Any]:

    """
    Create all reusable content blocks for the product using llm.
    """

    try:
        product_data = state.product_data

        if not product_data:
            return {"error": "Content Logic Error: No product data available"}
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        structured_llm = llm.with_structured_output(ContentBlockList)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert skincare content creator. Generate rich, engaging, and informative content blocks for different sections of a product page.

For each content block:
- Benefits: Create compelling, detailed descriptions of product benefits with specific outcomes
- Usage: Write clear, step-by-step usage instructions that are easy to follow
- Ingredients: Explain key ingredients with their functions and benefits
- Safety: Provide comprehensive safety information, precautions, and recommendations

Make the content professional, informative, and engaging. Use natural language that connects with skincare enthusiasts."""),
            ("user", """Product: {product_name}
Concentration: {concentration}
Skin Types: {skin_type}
Key Ingredients: {key_ingredients}
Benefits: {benefits}
How to Use: {how_to_use}
Side Effects: {side_effects}
Price: {price}

Generate detailed content blocks for: benefits, usage, ingredients, and safety.""")
        ])

        chain = prompt | structured_llm
        result = chain.invoke({
            "product_name": product_data.product_name,
            "concentration": product_data.concentration,
            "skin_type": ", ".join(product_data.skin_type),
            "key_ingredients": ", ".join(product_data.key_ingredients),
            "benefits": ", ".join(product_data.benefits),
            "how_to_use": product_data.how_to_use,
            "side_effects": product_data.side_effects,
            "price": product_data.price
        })

        # sturcturing hte generated content to ContentBlock objects
        content_blocks = {
            "benefits": ContentBlock(
                block_type="benefits",
                content=result.benefits,
                metadata={"benefit_count": len(product_data.benefits)}
            ),
            "usage": ContentBlock(
                block_type="usage",
                content=result.usage,
                metadata={"skin_types": product_data.skin_type}
            ),
            "ingredients": ContentBlock(
                block_type="ingredients",
                content=result.ingredients,
                metadata={"ingredient_count": len(product_data.key_ingredients)}
            ),
            "safety": ContentBlock(
                block_type="safety",
                content=result.safety,
                metadata={"side_effects": product_data.side_effects}
            )
        }

        return {"content_blocks": content_blocks}
    
    except Exception as e:
        return {"error": f"Content Logic Error: {str(e)}"}