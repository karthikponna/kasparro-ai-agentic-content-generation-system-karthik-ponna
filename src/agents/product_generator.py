from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import ProductPage, ProductSection, WorkflowState
from pydantic import BaseModel, Field


class ProductPageContent(BaseModel):
    """Structured product page content."""
    tagline: str = Field(..., description="Compelling tagline for the product (max 150 characters)")
    overview: str = Field(..., description="Engaging overview section introducing the product")
    pricing_content: str = Field(..., description="Pricing section with value proposition")


def generate_product_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate comprehensive product page using AI and content blocks.
    """

    try:
        product_data = state.product_data
        content_blocks = state.content_blocks
        
        if not product_data or not content_blocks:
            return {"error": "Product Page Generator Error: Missing required data"}
        

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        structured_llm = llm.with_structured_output(ProductPageContent)
        

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert copywriter for premium skincare products. Generate compelling product page content that converts browsers into buyers.

Create:
1. Tagline: A short, punchy tagline (max 150 characters) that captures the essence of the product
2. Overview: An engaging introduction that highlights what makes this product special
3. Pricing Content: A value-focused pricing section that justifies the cost and emphasizes quality

Use persuasive language while remaining factual and professional."""),
            ("user", """Product: {product_name}
Concentration: {concentration}
Skin Types: {skin_type}
Key Ingredients: {key_ingredients}
Benefits: {benefits}
Price: {price}

Generate tagline, overview, and pricing content for this premium skincare product.""")
        ])
        

        chain = prompt | structured_llm
        result = chain.invoke({
            "product_name": product_data.product_name,
            "concentration": product_data.concentration,
            "skin_type": ", ".join(product_data.skin_type),
            "key_ingredients": ", ".join(product_data.key_ingredients),
            "benefits": ", ".join(product_data.benefits),
            "price": product_data.price
        })
        

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
            "price": product_data.price,
            "total_sections": len(sections)
        }
        
        # create product page
        product_page = ProductPage(
            product_name=product_data.product_name,
            tagline=result.tagline,
            sections=sections,
            metadata=metadata
        )
        
        return {"product_page": product_page}
        
    except Exception as e:
        return {"error": f"Product Page Generator Error: {str(e)}"}