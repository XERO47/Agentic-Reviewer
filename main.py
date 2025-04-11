from flow import knowledge_builder_flow
import os
import sys
import argparse
import tempfile
import shutil
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

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

def main():
    # Note: Make sure to set your Google API key using:
    # Windows PowerShell: $env:GOOGLE_API_KEY = "your-api-key-here"
    # Bash: export GOOGLE_API_KEY="your-api-key-here"
    
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Generate knowledge documentation for a codebase')
    parser.add_argument('--dir', '-d', help='Path to the codebase directory')
    parser.add_argument('--github', '-g', help='GitHub repository URL to analyze')
    parser.add_argument('--example', '-e', action='store_true', help='Use the built-in example codebase')
    parser.add_argument('--output', '-o', default='codebase_knowledge.md', help='Output file path')
    args = parser.parse_args()
    
    # Determine what codebase to analyze
    codebase_context = ""
    temp_dir = None
    
    if args.github:
        # Clone the GitHub repository to a temporary directory
        temp_dir = clone_github_repo(args.github)
        logger.info("\n📚 Reading files from cloned repository. This may take a few minutes for large repos...")
        codebase_context = read_files_from_directory(temp_dir)
    elif args.dir:
        # Read from the specified directory
        if not os.path.isdir(args.dir):
            logger.error("❌ Error: '%s' is not a valid directory", args.dir)
            sys.exit(1)
        logger.info("\n📚 Reading codebase from directory: %s", args.dir)
        logger.info("⏳ This may take a few minutes depending on the size of the codebase...")
        codebase_context = read_files_from_directory(args.dir)
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
    
    try:
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
        
        # Print or save the final document
        logger.info("\n\n📄 CODEBASE KNOWLEDGE DOCUMENT 📄\n")
        
        if "final_document" in shared:
            print(shared["final_document"])
            
            # Save to file
            output_file = args.output
            with open(output_file, "w", encoding='utf-8') as f:
                f.write(shared["final_document"])
            
            logger.info("\n\n💾 Document saved to %s", os.path.abspath(output_file))
        else:
            logger.error("❌ Error: Final document was not generated. This could be due to one of the following reasons:")
            logger.error("1. The AI model encountered an error during processing")
            logger.error("2. The flow did not complete successfully")
            logger.error("3. One of the nodes did not generate its expected output")
            logger.error("\n🔍 Trying to save intermediate results to help with debugging...")
            
            # Save whatever we have to help with debugging
            debug_file = "debug_output.txt"
            with open(debug_file, "w", encoding='utf-8') as f:
                f.write("DEBUG INFORMATION\n\n")
                for key, value in shared.items():
                    f.write(f"=== {key} ===\n")
                    f.write(str(value)[:1000])  # Limit to first 1000 chars to avoid huge files
                    f.write("\n...\n\n")
            
            logger.info("🔧 Debug information saved to %s", os.path.abspath(debug_file))
        
        total_time = time.time() - start_time
        logger.info("✅ Analysis completed in %.1f seconds", analysis_time)
        logger.info("⏱️ Total process time: %.1f seconds", total_time)
    finally:
        # Clean up the temporary directory if we created one
        if temp_dir and os.path.exists(temp_dir):
            logger.info("🧹 Cleaning up temporary directory: %s", temp_dir)
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()