#!/usr/bin/env python3
import argparse
import os
import sys
import glob
import tempfile
import shutil
from utils.call_llm import call_llm

def clone_github_repo(repo_url):
    """Clone a GitHub repository to a temporary directory and return the path."""
    try:
        import git
    except ImportError:
        print("GitPython is not installed. Please install it using: pip install gitpython")
        sys.exit(1)
    
    print(f"Cloning repository: {repo_url}")
    temp_dir = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(repo_url, temp_dir)
        print(f"Repository cloned successfully to {temp_dir}")
        return temp_dir
    except Exception as e:
        print(f"Error cloning repository: {e}")
        sys.exit(1)

class CodebaseQA:
    def __init__(self, knowledge_path="codebase_knowledge.md", codebase_dir="."):
        """Initialize the CodebaseQA system with knowledge document and codebase directory."""
        self.knowledge_path = knowledge_path
        self.codebase_dir = codebase_dir
        self.knowledge_content = self.load_knowledge()
        self.history = []  # Store conversation history
        
    def load_knowledge(self):
        """Load the codebase knowledge document."""
        try:
            with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Knowledge document not found at {self.knowledge_path}")
            print("Please run the knowledge builder first to generate the document.")
            sys.exit(1)
    
    def find_files(self, pattern):
        """Find files in the codebase matching a pattern."""
        matches = glob.glob(os.path.join(self.codebase_dir, pattern))
        matches += glob.glob(os.path.join(self.codebase_dir, "**", pattern), recursive=True)
        return sorted(list(set(matches)))
    
    def get_file_content(self, file_path):
        """Get the content of a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File {file_path} not found."
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def get_answer(self, question):
        """Get an answer to a question about the codebase."""
        # Add the question to the history
        self.history.append({"role": "user", "content": question})
        
        # Prepare the context for the LLM
        context = self.knowledge_content
        
        # Create the prompt for the LLM
        prompt = f"""You are a helpful assistant answering questions about a codebase. 
Use the provided codebase knowledge document to answer the question.

If you need the content of a specific file to provide a better answer, you can request it using:
[REQUEST_FILE: filename or path pattern]

For example:
[REQUEST_FILE: main.py]
[REQUEST_FILE: *.py]

CODEBASE KNOWLEDGE:
{context}

QUESTION: {question}

PREVIOUS CONVERSATION:
{self._format_history()}

Answer the question thoroughly but concisely. If you request a file, explain why you need it.
"""
        
        # Get response from LLM
        response = call_llm(prompt)
        
        # Check if the LLM requested a file
        while "[REQUEST_FILE:" in response:
            # Extract the file pattern
            file_request_start = response.find("[REQUEST_FILE:")
            file_request_end = response.find("]", file_request_start)
            file_pattern = response[file_request_start+14:file_request_end].strip()
            
            # Find matching files
            matching_files = self.find_files(file_pattern)
            
            if matching_files:
                file_contents = ""
                # Limit to first 3 matches if there are many
                for file_path in matching_files[:3]:
                    content = self.get_file_content(file_path)
                    file_contents += f"\n\nFILE: {file_path}\n```\n{content}\n```\n"
                
                if len(matching_files) > 3:
                    file_contents += f"\n\nNote: {len(matching_files) - 3} more files matched but were not shown."
            else:
                file_contents = f"No files matching '{file_pattern}' were found."
            
            # Update the prompt with the file contents
            prompt += f"\n\nYou requested file: {file_pattern}\n{file_contents}\n\nPlease continue your answer with this information."
            
            # Get updated response from LLM
            response = call_llm(prompt)
            
            # Remove the request file part from the response
            response = response.replace(f"[REQUEST_FILE: {file_pattern}]", "")
        
        # Add the response to the history
        self.history.append({"role": "assistant", "content": response})
        
        return response
    
    def _format_history(self):
        """Format the conversation history for inclusion in the prompt."""
        if not self.history:
            return "No previous conversation."
        
        formatted = []
        for entry in self.history[-6:]:  # Only include the last 6 exchanges to save context space
            role = "User" if entry["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {entry['content']}")
        
        return "\n\n".join(formatted)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ask questions about your codebase.")
    parser.add_argument("--knowledge", "-k", default="codebase_knowledge.md", 
                        help="Path to the codebase knowledge document")
    parser.add_argument("--dir", "-d", default=".", 
                        help="Path to the codebase directory")
    parser.add_argument("--github", "-g", help="GitHub repository URL to analyze")
    args = parser.parse_args()
    
    # Initialize variables
    codebase_dir = args.dir
    temp_dir = None
    
    # Handle GitHub repository if specified
    if args.github:
        temp_dir = clone_github_repo(args.github)
        codebase_dir = temp_dir
    
    try:
        # Initialize the QA system
        qa = CodebaseQA(knowledge_path=args.knowledge, codebase_dir=codebase_dir)
        
        print("🧠 Codebase QA System")
        print("Type your questions about the codebase below. Type 'exit' or 'quit' to exit.")
        print("The system may request additional files to provide better answers.")
        
        # Main interaction loop
        while True:
            try:
                # Get user question
                print("\n> ", end="")
                question = input().strip()
                
                # Check for exit command
                if question.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                # Get and display answer
                print("\n🔍 Analyzing codebase knowledge...")
                answer = qa.get_answer(question)
                print("\n" + answer)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
    finally:
        # Clean up the temporary directory if we created one
        if temp_dir and os.path.exists(temp_dir):
            print(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main() 