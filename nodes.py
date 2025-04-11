from framework import Node, BatchNode
from utils.call_llm import call_llm

class IdentifyAbstractions(Node):
    def prep(self, shared):
        # Read codebase context from shared
        return shared["codebase_context"]
    
    def exec(self, codebase_context):
        # Call LLM to identify abstractions
        prompt = f"""
        Analyze the following codebase and identify its core abstractions (classes, modules, patterns, etc.).
        Return a list of 5-10 key abstractions that someone would need to understand in order to work with this codebase.
        For each abstraction, provide a short description of what it is.

        Codebase:
        {codebase_context}
        
        Format your response as a Python list of strings, with each string being the name of an abstraction.
        For example: ["Abstraction1", "Abstraction2", "Abstraction3"]

        Important: Return ONLY the formatted list, without any other text.
        """
        response = call_llm(prompt)
        
        # Extract the list from the response
        try:
            # Find the list in the response - look for text between [ and ]
            import re
            list_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if list_match:
                abstractions_text = list_match.group(1)
                # Convert the string representation to an actual list
                try:
                    abstractions_list = eval("[" + abstractions_text + "]")
                    return abstractions_list
                except:
                    # If eval fails, try a more robust parsing approach
                    items = re.findall(r'["\'](.*?)["\']', abstractions_text)
                    if items:
                        return items
            
            # If regex approach fails, try to eval the entire response if it looks like a list
            if response.strip().startswith('[') and response.strip().endswith(']'):
                try:
                    return eval(response.strip())
                except:
                    pass
                    
            # Fallback: extract lines that look like list items
            return [item.strip().strip('"\'') for item in response.split('\n') 
                   if item.strip() and (item.strip().startswith('"') or 
                                        item.strip().startswith("'") or 
                                        item.strip().startswith("-") or
                                        item.strip().startswith("*"))]
        except Exception as e:
            # If all parsing attempts fail, return a list with the raw response
            print(f"Error parsing abstractions: {e}")
            return [response]
    
    def post(self, shared, prep_res, exec_res):
        # Store identified abstractions
        shared["identified_abstractions"] = exec_res
        print("✓ Identified core abstractions")
        return "default"

class SequenceAbstractions(Node):
    def prep(self, shared):
        # Read identified abstractions and codebase context
        return shared["identified_abstractions"], shared["codebase_context"]
    
    def exec(self, inputs):
        abstractions, codebase_context = inputs
        # Call LLM to sequence abstractions
        prompt = f"""
        Given the following list of abstractions from a codebase:
        {abstractions}
        
        And the codebase context:
        {codebase_context}
        
        Determine a logical learning sequence for these abstractions, starting with the most fundamental ones 
        that others depend on. Consider which concepts need to be understood before others.
        
        Format your response as a Python list of strings, in the exact order they should be learned.
        For example: ["Abstraction2", "Abstraction1", "Abstraction3"]
        
        Use only the abstraction names provided in the original list.
        Important: Return ONLY the formatted list, without any other text.
        """
        response = call_llm(prompt)
        
        # Extract the list from the response - similar to IdentifyAbstractions but ensuring we have all abstractions
        try:
            # Find the list in the response - look for text between [ and ]
            import re
            list_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if list_match:
                sequence_text = list_match.group(1)
                # Convert the string representation to an actual list
                try:
                    sequence_list = eval("[" + sequence_text + "]")
                    return sequence_list
                except:
                    # If eval fails, try a more robust parsing approach
                    items = re.findall(r'["\'](.*?)["\']', sequence_text)
                    if items:
                        return items
            
            # If regex approach fails, try to eval the entire response if it looks like a list
            if response.strip().startswith('[') and response.strip().endswith(']'):
                try:
                    return eval(response.strip())
                except:
                    pass
                    
            # Fallback: extract lines that look like list items
            sequence = [item.strip().strip('"\'') for item in response.split('\n') 
                       if item.strip() and (item.strip().startswith('"') or 
                                           item.strip().startswith("'") or 
                                           item.strip().startswith("-") or
                                           item.strip().startswith("*"))]
            
            # If we got something, return it
            if sequence:
                return sequence
        except Exception as e:
            print(f"Error parsing sequence: {e}")
        
        # If all parsing fails, ensure all abstractions are included in the original order
        return abstractions
    
    def post(self, shared, prep_res, exec_res):
        # Store sequenced abstractions
        shared["sequenced_abstractions"] = exec_res
        print("✓ Sequenced abstractions in logical learning order")
        return "default"

class GenerateOverview(Node):
    def prep(self, shared):
        # Read sequenced abstractions and codebase context
        return shared["sequenced_abstractions"], shared["codebase_context"]
    
    def exec(self, inputs):
        sequenced_abstractions, codebase_context = inputs
        # Call LLM to generate overview
        prompt = f"""
        Create a comprehensive overview of the following codebase, focusing on these core abstractions in this specific order:
        {sequenced_abstractions}
        
        Based on the codebase context:
        {codebase_context}
        
        Your overview should:
        1. Explain the purpose and high-level architecture of the codebase
        2. Briefly introduce each abstraction and how they connect
        3. Explain why this learning sequence is logical
        4. Help a new developer understand the big picture before diving into details
        
        Format your response as Markdown, with appropriate headers, bullet points, and emphasis.
        """
        return call_llm(prompt)
    
    def post(self, shared, prep_res, exec_res):
        # Store overview text
        shared["overview_text"] = exec_res
        print("✓ Generated overview")
        return "default"

class GenerateDetails(BatchNode):
    def prep(self, shared):
        # Return sequenced abstractions and codebase context
        return [(abstraction, shared["codebase_context"]) for abstraction in shared["sequenced_abstractions"]]
    
    def exec(self, inputs):
        # Unpack the inputs
        abstraction_name, codebase_context = inputs
        
        # For each abstraction, generate detailed explanation with examples
        prompt = f"""
        Create a detailed explanation for the abstraction "{abstraction_name}" based on the actual codebase provided.
        
        Codebase context:
        {codebase_context}
        
        Your explanation should include:
        1. A clear definition of what this abstraction is (based on the actual code)
        2. Its purpose and role in the overall system
        3. Important methods, properties, or components found in the codebase
        4. IMPORTANT: Extract 1-2 REAL code examples from the provided codebase that show this abstraction in use
           - Do not invent or create generic examples - only use actual code from the codebase
           - If you can't find explicit examples, look for places where the abstraction is used or implemented
        5. Common patterns or best practices visible in the actual code
        6. Any potential pitfalls or things to watch out for, based on how this abstraction is used in this specific codebase
        
        Format your response as Markdown, with appropriate code blocks, headers, and emphasis.
        Focus on making the explanation relevant to THIS specific codebase rather than providing generic knowledge.
        """
        explanation = call_llm(prompt)
        # Return a tuple with the abstraction name and the explanation
        return (abstraction_name, explanation)
    
    def post(self, shared, prep_res, exec_res_list):
        # Convert list of tuples to dictionary and store
        detailed_explanations = {}
        
        # Ensure proper processing of exec_res_list
        for item in exec_res_list:
            if isinstance(item, tuple) and len(item) == 2:
                abstraction_name, explanation = item
                detailed_explanations[abstraction_name] = explanation
            else:
                # If the tuple structure is not as expected, use the abstraction from prep_res
                # This handles cases where the model doesn't return the expected tuple format
                for idx, (abstraction_name, _) in enumerate(prep_res):
                    if idx < len(exec_res_list):
                        detailed_explanations[abstraction_name] = exec_res_list[idx]
                break
        
        shared["detailed_explanations"] = detailed_explanations
        print(f"✓ Generated detailed explanations for {len(detailed_explanations)} abstractions")
        return "default"

class CombineDocument(Node):
    def prep(self, shared):
        # Check if all required components are available
        is_ready = (
            "overview_text" in shared and
            "sequenced_abstractions" in shared and
            "detailed_explanations" in shared
        )
        
        if not is_ready:
            print("Not all required components are available yet:")
            if "overview_text" not in shared:
                print("- Missing overview_text")
            if "sequenced_abstractions" not in shared:
                print("- Missing sequenced_abstractions")
            if "detailed_explanations" not in shared:
                print("- Missing detailed_explanations")
            # Return None to indicate we can't proceed
            return None
        
        # If we have everything, read all components needed for final document
        return (
            shared["overview_text"],
            shared["sequenced_abstractions"],
            shared["detailed_explanations"]
        )
    
    def exec(self, inputs):
        # If prep returned None, skip execution
        if inputs is None:
            return None
            
        overview_text, sequenced_abstractions, detailed_explanations = inputs
        
        # Combine overview and detailed sections into final document
        document_parts = [
            "# Codebase Knowledge Document\n\n",
            "> **Note:** This document was automatically generated by analyzing your codebase. All code examples are extracted directly from your code.\n\n",
            "## Overview\n\n",
            overview_text,
            "\n\n## Detailed Explanations\n\n",
            "> Each section below explains a key abstraction found in your codebase, with examples taken directly from your code.\n\n"
        ]
        
        # Add each abstraction section in sequence
        for abstraction in sequenced_abstractions:
            if abstraction in detailed_explanations:
                document_parts.append(f"\n\n### {abstraction}\n\n")
                document_parts.append(detailed_explanations[abstraction])
        
        # Add footer with usage tips
        document_parts.append("\n\n---\n\n")
        document_parts.append("## Using This Document\n\n")
        document_parts.append("* This document is intended to help you understand the key abstractions in your codebase.\n")
        document_parts.append("* Code examples are taken directly from your codebase to ensure relevance.\n")
        document_parts.append("* For the most accurate understanding, refer to the actual code alongside this document.\n")
        document_parts.append("* If you find examples that seem irrelevant, please regenerate the document with a more focused codebase input.\n")
        
        return "".join(document_parts)
    
    def post(self, shared, prep_res, exec_res):
        # If we don't have a result yet, just return without storing
        if exec_res is None:
            return "default"
            
        # Store final document
        shared["final_document"] = exec_res
        print("✓ Combined document sections")
        return "default"