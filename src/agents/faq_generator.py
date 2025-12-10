from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import FAQPage, QAPair, WorkflowState
from pydantic import BaseModel, Field


class FAQContent(BaseModel):
    """FAQ content structure for LLM output."""
    qa_pairs: List[QAPair] = Field(..., description="List of Q&A pairs", min_length=5)


def generate_faq_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate FAQ page with Q&A pairs.
    """
    try: 
        product_data = state.product_data
        questions = state.questions
        content_blocks = state.content_blocks

        if not product_data or not questions:
            return {"error": "FAQ Generator Error: Missing required data"}
        
        # seletcting at least 5 for FAQ
        selected_questions = questions[:7] if len(questions) >= 7 else questions[:5]

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        structured_llm = llm.with_structured_output(FAQContent)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at creating FAQ content for skincare products.
Generate clear, informative answers for the provided questions based on the product information.
Ensure answers are helpful, accurate, and based only on the given product data."""),
            ("user", """Product Information:
Name: {product_name}
Concentration: {concentration}
Skin Type: {skin_type}
Key Ingredients: {key_ingredients}
Benefits: {benefits}
How to Use: {how_to_use}
Side Effects: {side_effects}
Price: {price}

Content Blocks:
Benefits: {benefits_block}
Usage: {usage_block}
Ingredients: {ingredients_block}
Safety: {safety_block}

Questions to answer:
{questions_list}

Generate Q&A pairs for these questions.""")
        ])

        questions_list = "\n".join([
            f"{i+1}. [{q.category.value}] {q.question}"
            for i, q in enumerate(selected_questions)
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
            "price": product_data.price,
            "benefits_block": content_blocks["benefits"].content if content_blocks else "",
            "usage_block": content_blocks["usage"].content if content_blocks else "",
            "ingredients_block": content_blocks["ingredients"].content if content_blocks else "",
            "safety_block": content_blocks["safety"].content if content_blocks else "",
            "questions_list": questions_list
        })

        # get unique categories
        categories = list(set([qa.category for qa in result.qa_pairs]))

        # create FAQ page
        faq_page = FAQPage(
            product_name=product_data.product_name,
            total_questions=len(result.qa_pairs),
            qa_pairs=result.qa_pairs,
            categories=categories
        )
        
        return {"faq_page": faq_page}
        
    except Exception as e:
        return {"error": f"FAQ Generator Error: {str(e)}"}