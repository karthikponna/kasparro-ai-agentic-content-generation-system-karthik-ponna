from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field

from models import Question, QuestionCategory, WorkflowState


class QuestionList(BaseModel):
    """List of questions with categories."""
    questions: List[Question] = Field(..., description="List of generated questions", min_length=15)


def generate_questions(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate 15+ categorized user questions about the product.
    """

    try:
        product_data = state.product_data

        if not product_data:
            return {"error": "Question Generator Error: No product data available"}
        
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        structured_llm = llm.with_structured_output(QuestionList)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating user questions about skincare products.
Generate at least 15 diverse questions that users might ask about this product.
Categorize each question into one of these categories:
- Informational: General product information
- Safety: Safety concerns and precautions
- Usage: How to use the product
- Purchase: Buying decisions and pricing
- Comparison: Comparing with other products
- Ingredients: Questions about ingredients
- Benefits: Questions about benefits and results

Ensure a good distribution across all categories."""),
            ("user", """Product: {product_name}
Concentration: {concentration}
Skin Type: {skin_type}
Key Ingredients: {key_ingredients}
Benefits: {benefits}
How to Use: {how_to_use}
Side Effects: {side_effects}
Price: {price}

Generate at least 15 questions across all categories.""")
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

        return {"questions": result.questions}
    
    except Exception as e:
        return {"error": f"Question Generator Error: {str(e)}"}