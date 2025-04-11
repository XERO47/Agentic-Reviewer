from pocketflow import Flow
from nodes import (
    IdentifyAbstractions,
    SequenceAbstractions,
    GenerateOverview,
    GenerateDetails,
    CombineDocument
)

def create_knowledge_builder_flow():
    """Create and return a codebase knowledge builder flow."""
    # Create nodes
    identify_node = IdentifyAbstractions()
    sequence_node = SequenceAbstractions()
    overview_node = GenerateOverview()
    details_node = GenerateDetails()
    combine_node = CombineDocument()
    
    # Connect nodes in a linear sequence
    identify_node >> sequence_node >> overview_node >> details_node >> combine_node
    
    # Create flow starting with identify node
    return Flow(start=identify_node)

# Create the knowledge builder flow
knowledge_builder_flow = create_knowledge_builder_flow()