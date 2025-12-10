from typing import Dict, Any, Literal

from langgraph.graph import StateGraph, END

from models import WorkflowState
from agents.parser_agent import parse_product_data
from agents.questions_generator import generate_questions
from agents.content_logic import create_content_blocks
from agents.faq_generator import generate_faq_page
from agents.product_generator import generate_product_page
from agents.comparison_generator import generate_fictional_product_b, generate_comparison_page


def should_continue(state: WorkflowState) -> Literal["error", "continue"]:
    """
    Determine if workflow should continue or stop due to error.
    
    Args:
        state: Current workflow state
        
    Returns:
        "error" if error exists, "continue" otherwise
    """
    if state.error:
        return "error"
    return "continue"


def create_workflow() -> StateGraph:

    workflow = StateGraph(WorkflowState)

    # add nodes
    workflow.add_node("parse_product", parse_product_data)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("create_content_blocks", create_content_blocks)
    workflow.add_node("generate_faq", generate_faq_page)
    workflow.add_node("generate_product_page", generate_product_page)
    workflow.add_node("create_fictional_product", generate_fictional_product_b)
    workflow.add_node("generate_comparison", generate_comparison_page)

    workflow.set_entry_point("parse_product")

    # after parsing, check for errors
    workflow.add_conditional_edges(
        "parse_product",
        should_continue,
        {
            "continue": "generate_questions",
            "error": END
        }
    )

    # after generating questions, create content blocks
    workflow.add_conditional_edges(
        "generate_questions",
        should_continue,
        {
            "continue": "create_content_blocks",
            "error": END
        }
    )

    # after creating content blocks, generate FAQ page
    workflow.add_conditional_edges(
        "create_content_blocks",
        should_continue,
        {
            "continue": "generate_faq",
            "error": END
        }
    )

    # after FAQ, generate product page
    workflow.add_conditional_edges(
        "generate_faq",
        should_continue,
        {
            "continue": "generate_product_page",
            "error": END
        }
    )

    # after product page, create fictional product for comparison
    workflow.add_conditional_edges(
        "generate_product_page",
        should_continue,
        {
            "continue": "create_fictional_product",
            "error": END
        }
    )
    
    # after fictional product, generate comparison page
    workflow.add_conditional_edges(
        "create_fictional_product",
        should_continue,
        {
            "continue": "generate_comparison",
            "error": END
        }
    )

    # end after comparison page
    workflow.add_edge("generate_comparison", END)
    
    return workflow


def run_workflow(product_data: Dict[str, Any]) -> WorkflowState:
    """
    Execute the content generation workflow.
    
    Args:
        product_data: Raw product data dictionary
        
    Returns:
        Final workflow state with all generated content
    """
    try:
        # Create initial state
        initial_state = WorkflowState(raw_product_data=product_data)
        
        # Build and compile workflow
        workflow = create_workflow()
        app = workflow.compile()
        
        # executing the workflow and here langgraph returns a dictionary
        final_state_dict = app.invoke(initial_state)
        
        # Convert dictionary to WorkflowState object
        final_state = WorkflowState(**final_state_dict)
        
        return final_state
        
    except Exception as e:
        # Return error state
        error_state = WorkflowState(
            raw_product_data=product_data,
            error=f"Workflow execution error: {str(e)}"
        )
        return error_state

