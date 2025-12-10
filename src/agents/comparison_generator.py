from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import ComparisonPage, ComparisonFeature, WorkflowState
from pydantic import BaseModel, Field


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
    """
    try:
        product_data = state.product_data
        if not product_data:
            return {"error": "Comparison Generator Error: No product data available"}
        

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
        structured_llm = llm.with_structured_output(FictionalProduct)
        

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are creating a fictional competitor product for comparison purposes.
The product should be realistic and comparable but have some differences in formulation, pricing, and benefits.
Make it a credible alternative with its own strengths and weaknesses."""),
            ("user", """Create a fictional Vitamin C serum product to compare against:

Original Product:
- Name: {product_name}
- Concentration: {concentration}
- Skin Types: {skin_type}
- Key Ingredients: {key_ingredients}
- Benefits: {benefits}
- Price: {price}

Generate a fictional competing product with similar but different specifications.""")
        ])
        

        chain = prompt | structured_llm
        fictional_product = chain.invoke({
            "product_name": product_data.product_name,
            "concentration": product_data.concentration,
            "skin_type": ", ".join(product_data.skin_type),
            "key_ingredients": ", ".join(product_data.key_ingredients),
            "benefits": ", ".join(product_data.benefits),
            "price": product_data.price
        })
        
        # convert to dict
        fictional_product_dict = {
            "product_name": fictional_product.product_name,
            "concentration": fictional_product.concentration,
            "skin_type": fictional_product.skin_type,
            "key_ingredients": fictional_product.key_ingredients,
            "benefits": fictional_product.benefits,
            "price": fictional_product.price
        }
        
        return {"fictional_product_b": fictional_product_dict}
        
    except Exception as e:
        return {"error": f"Fictional Product Generator Error: {str(e)}"}


def generate_comparison_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate comparison page between Product A and Product B.
    """
    try:
        product_data = state.product_data
        fictional_product_b = state.fictional_product_b
        
        if not product_data or not fictional_product_b:
            return {"error": "Comparison Generator Error: Missing product data"}
        

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        structured_llm = llm.with_structured_output(ComparisonAnalysis)
        

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at comparing skincare products objectively.
Create a detailed comparison matrix highlighting key differences and similarities.
Provide an unbiased analysis with a recommendation based on different user needs."""),
            ("user", """Compare these two products:

Product A: {product_a_name}
- Concentration: {product_a_concentration}
- Skin Types: {product_a_skin_type}
- Key Ingredients: {product_a_ingredients}
- Benefits: {product_a_benefits}
- Price: {product_a_price}

Product B: {product_b_name}
- Concentration: {product_b_concentration}
- Skin Types: {product_b_skin_type}
- Key Ingredients: {product_b_ingredients}
- Benefits: {product_b_benefits}
- Price: {product_b_price}

Create a comparison matrix with features like:
- Concentration
- Price
- Key Ingredients
- Primary Benefits
- Skin Type Suitability
- Value for Money

For each feature, indicate which product performs better (winner field).
Provide a comprehensive summary and recommendation.""")
        ])
        
        # generate comparison
        chain = prompt | structured_llm
        comparison = chain.invoke({
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
        
        # create product dictionaries for the page
        product_a_dict = {
            "product_name": product_data.product_name,
            "concentration": product_data.concentration,
            "skin_type": product_data.skin_type,
            "key_ingredients": product_data.key_ingredients,
            "benefits": product_data.benefits,
            "price": product_data.price
        }
        
        # create comparison page
        comparison_page = ComparisonPage(
            product_a=product_a_dict,
            product_b=fictional_product_b,
            comparison_matrix=comparison.comparison_matrix,
            summary=comparison.summary,
            recommendation=comparison.recommendation
        )
        
        return {"comparison_page": comparison_page}
        
    except Exception as e:
        return {"error": f"Comparison Page Generator Error: {str(e)}"}
