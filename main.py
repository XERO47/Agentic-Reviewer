from flow import knowledge_builder_flow
import os
import sys
import argparse
import tempfile
import shutil
import time
import logging
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Import utility for LLM calls
from utils.call_llm import call_llm

def clone_github_repo(repo_url):
    """Clone a GitHub repository to a temporary directory and return the path."""
    try:
        import git
    except ImportError:
        logger.error("❌ GitPython is not installed. Please install it using: pip install gitpython")
        sys.exit(1)
    
    logger.info("🔄 Cloning repository: %s", repo_url)
    temp_dir = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(repo_url, temp_dir)
        logger.info("✅ Repository cloned successfully to %s", temp_dir)
        return temp_dir
    except Exception as e:
        logger.error("❌ Error cloning repository: %s", e)
        sys.exit(1)

def read_files_from_directory(directory_path):
    """Read all code files from a directory recursively."""
    codebase_content = []
    file_count = 0
    processed_count = 0
    
    # First count total files for progress reporting
    for root, dirs, files in os.walk(directory_path):
        # Skip .git directory completely
        if '.git' in dirs:
            dirs.remove('.git')
        # Skip node_modules and other large directories
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if 'venv' in dirs:
            dirs.remove('venv')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            # Skip binary and non-code files
            if (not file.startswith('.') and 
                not file.endswith(('.pyc', '.pyo', '.so', '.obj', 
                                 '.dll', '.exe', '.bin', '.dat',
                                 '.png', '.jpg', '.jpeg', '.gif', '.ico',
                                 '.mp3', '.mp4', '.avi', '.mov',
                                 '.zip', '.tar', '.gz', '.rar'))):
                file_count += 1
    
    logger.info("📄 Found %d files to process", file_count)
    
    # Now read the files
    for root, dirs, files in os.walk(directory_path):
        # Skip .git directory completely
        if '.git' in dirs:
            dirs.remove('.git')
        # Skip node_modules and other large directories
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if 'venv' in dirs:
            dirs.remove('venv')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            # Skip binary and non-code files that are commonly found in codebases
            if (file.startswith('.') or 
                file.endswith(('.md', '.txt', '.json', '.log', '.pyc', '.pyo', 
                             '.so', '.obj', '.dll', '.exe', '.bin', '.dat',
                             '.png', '.jpg', '.jpeg', '.gif', '.ico',
                             '.mp3', '.mp4', '.avi', '.mov',
                             '.zip', '.tar', '.gz', '.rar'))):
                continue
            
            # Skip files larger than 1MB to avoid memory issues
            file_path = os.path.join(root, file)
            try:
                if os.path.getsize(file_path) > 1024 * 1024:
                    logger.info("⏩ Skipping large file: %s", file_path)
                    continue
                    
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                rel_path = os.path.relpath(file_path, directory_path)
                codebase_content.append(f"# File: {rel_path}\n{content}\n")
                processed_count += 1
                
                # Report progress every 10 files
                if processed_count % 10 == 0:
                    logger.info("⏳ Processed %d/%d files (%.1f%%)", 
                              processed_count, file_count, processed_count/file_count*100)
                    
            except Exception as e:
                # Just skip files that can't be read rather than erroring out
                pass
    
    logger.info("✅ Successfully processed %d/%d files", processed_count, file_count)
    return "\n".join(codebase_content)

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
            logger.error(f"❌ Error: Knowledge document not found at {self.knowledge_path}")
            logger.error("Please run the knowledge builder first to generate the document.")
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

def start_qa_interface(knowledge_path, codebase_dir):
    """Start the QA interface with the given knowledge document and codebase directory."""
    # Initialize the QA system
    qa = CodebaseQA(knowledge_path=knowledge_path, codebase_dir=codebase_dir)
    
    logger.info("\n🤖 Codebase AI Assistant")
    logger.info("I've analyzed your code and built my knowledge base.")
    logger.info("Ask me anything about your codebase! Type 'exit' or 'quit' to end.")
    
    # Main interaction loop
    while True:
        try:
            # Get user question
            print("\n> ", end="")
            question = input().strip()
            
            # Check for exit command
            if question.lower() in ["exit", "quit", "q"]:
                logger.info("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            # Get and display answer
            logger.info("\n🔍 Analyzing your question...")
            answer = qa.get_answer(question)
            print("\n" + answer)
            
        except KeyboardInterrupt:
            logger.info("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"\n❌ Error: {str(e)}")

def main():
    # Note: Make sure to set your Google API key using:
    # Windows PowerShell: $env:GOOGLE_API_KEY = "your-api-key-here"
    # Bash: export GOOGLE_API_KEY="your-api-key-here"
    
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='AI-powered code reviewer and codebase assistant')
    parser.add_argument('--dir', '-d', default=".", help='Path to the codebase directory')
    parser.add_argument('--github', '-g', help='GitHub repository URL to analyze')
    parser.add_argument('--example', '-e', action='store_true', help='Use the built-in example codebase')
    parser.add_argument('--output', '-o', default='codebase_knowledge.md', help='Output file path')
    parser.add_argument('--chat', '-c', action='store_true', default=True, 
                      help='Start chat interface after generating knowledge (default: True)')
    parser.add_argument('--skip-build', '-s', action='store_true',
                      help='Skip knowledge building and use existing document for chat')
    args = parser.parse_args()
    
    # Determine what codebase to analyze
    codebase_context = ""
    temp_dir = None
    codebase_dir = args.dir
    knowledge_path = args.output
    
    # Handle GitHub repository if specified
    if args.github:
        # Clone the GitHub repository to a temporary directory
        temp_dir = clone_github_repo(args.github)
        codebase_dir = temp_dir
    
    try:
        # Skip the knowledge building if requested
        if not args.skip_build:
            if args.github:
                logger.info("\n📚 Reading files from cloned repository. This may take a few minutes for large repos...")
                codebase_context = read_files_from_directory(codebase_dir)
            elif args.dir:
                # Read from the specified directory
                if not os.path.isdir(codebase_dir):
                    logger.error("❌ Error: '%s' is not a valid directory", codebase_dir)
                    sys.exit(1)
                logger.info("\n📚 Reading codebase from directory: %s", codebase_dir)
                logger.info("⏳ This may take a few minutes depending on the size of the codebase...")
                codebase_context = read_files_from_directory(codebase_dir)
            elif args.example or (not args.dir and not args.github):
                # Use the built-in example
                logger.info("🧪 Using built-in example codebase")
                codebase_context = """
                # File: data_processor.py
                class DataLoader:
                    def __init__(self, filename):
                        self.filename = filename
                        
                    def load_data(self):
                        with open(self.filename, 'r') as f:
                            return f.read()
                
                class DataProcessor:
                    def __init__(self, data):
                        self.data = data
                        
                    def process(self):
                        # Process the data
                        return self.data.upper()
                
                # File: visualization.py
                class Visualizer:
                    def __init__(self, data):
                        self.data = data
                        
                    def create_chart(self, chart_type):
                        print(f"Creating {chart_type} chart with {self.data[:10]}...")
                
                # File: main_app.py
                from data_processor import DataLoader, DataProcessor
                from visualization import Visualizer
                
                class Application:
                    def __init__(self, config):
                        self.config = config
                        
                    def run(self):
                        loader = DataLoader(self.config['input_file'])
                        data = loader.load_data()
                        
                        processor = DataProcessor(data)
                        processed_data = processor.process()
                        
                        visualizer = Visualizer(processed_data)
                        visualizer.create_chart(self.config['chart_type'])
                        
                if __name__ == "__main__":
                    config = {
                        'input_file': 'data.txt',
                        'chart_type': 'bar'
                    }
                    app = Application(config)
                    app.run()
                """
            
            # Initialize shared memory
            shared = {
                        "codebase_context": codebase_context,
                    }
            
            file_processing_time = time.time() - start_time
            logger.info("\n⏱️ Files processed in %.1f seconds", file_processing_time)
            
            logger.info("\n🧠 Now analyzing the codebase with AI...")
            logger.info("⏳ This process can take anywhere from 2-10 minutes depending on the size of your codebase.")
            logger.info("🔍 The AI is working through these steps:")
            logger.info("1️⃣ Identifying core abstractions (1-2 min)")
            logger.info("2️⃣ Sequencing abstractions logically (1-2 min)")
            logger.info("3️⃣ Generating overview (1-2 min)")
            logger.info("4️⃣ Creating detailed explanations for each abstraction (varies by number of abstractions)")
            logger.info("5️⃣ Combining all sections into final document (30 sec)")
            
            # Run the knowledge builder flow
            analysis_start_time = time.time()
            knowledge_builder_flow.run(shared)
            analysis_time = time.time() - analysis_start_time
            
            if "final_document" in shared:
                # Save to file
                with open(knowledge_path, "w", encoding='utf-8') as f:
                    f.write(shared["final_document"])
                
                logger.info("\n💾 Knowledge document saved to %s", os.path.abspath(knowledge_path))
                logger.info("✅ Analysis completed in %.1f seconds", analysis_time)
            else:
                logger.error("❌ Error: Final document was not generated.")
                logger.error("Please check logs for issues or try again.")
                sys.exit(1)
        else:
            # Verify the knowledge file exists when skipping build
            if not os.path.exists(knowledge_path):
                logger.error(f"❌ Knowledge file not found at {knowledge_path}")
                logger.error("Please remove --skip-build flag to generate it first.")
                sys.exit(1)
            logger.info(f"📚 Using existing knowledge file: {knowledge_path}")
        
        # Start chat interface if requested
        if args.chat:
            start_qa_interface(knowledge_path, codebase_dir)
        
    finally:
        # Clean up the temporary directory if we created one
        if temp_dir and os.path.exists(temp_dir):
            logger.info(f"🧹 Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()