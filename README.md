#Codebase Knowledge Builder

A powerful AI-powered tool to **automatically analyze and understand codebases**, built on the [PocketFlow](https://github.com/the-pocket/PocketFlow) framework. It:

1. **Analyzes your code** to identify key abstractions
2. **Generates comprehensive documentation** explaining each abstraction
3. **Creates an interactive QA system** where you can ask questions about your code

## 📋 Features

- **Codebase Analysis**: Automatically identifies and sequences the core abstractions in your code
- **Knowledge Document**: Generates a detailed Markdown document explaining your codebase
- **Interactive Q&A**: Ask questions about your code and get informed answers
- **Agentic File Access**: The system can request specific files when needed to answer questions
- **GitHub Integration**: Analyze any GitHub repository with a single command

## 🔧 Installation

1. Clone this repository:
   

2. Install dependencies:
   ```bash
   pip install pocketflow gitpython
   ```

3. Set up your API keys (either Google Gemini or OpenAI):
   ```bash
   # For Windows PowerShell:
   $env:GOOGLE_API_KEY="your-google-api-key"
   # OR
   $env:OPENAI_API_KEY="your-openai-api-key"
   
   # For Linux/Mac:
   export GOOGLE_API_KEY="your-google-api-key"
   # OR
   export OPENAI_API_KEY="your-openai-api-key"
   ```

## 🚀 Usage

### Step 1: Generate Codebase Knowledge Document

Analyze your local codebase:
```bash
python main.py --dir path/to/your/codebase
```

Or analyze a GitHub repository:
```bash
python main.py --github https://github.com/username/repo
```

The tool will generate a `codebase_knowledge.md` document containing:
- An overview of your codebase's purpose and architecture
- A logical sequence for learning the codebase
- Detailed explanations of each abstraction with real code examples

### Step 2: Ask Questions About Your Codebase

Once the knowledge document is generated, you can use the interactive Q&A system:

```bash
python codebase_qa.py --knowledge codebase_knowledge.md --dir path/to/your/codebase
```

Or for a GitHub repository:
```bash
python codebase_qa.py --knowledge codebase_knowledge.md --github https://github.com/username/repo
```

Then simply ask questions about your codebase:
```
> What are the main abstractions in this codebase?
> How does the X class work?
> Show me an example of Y in use
```

The system will provide answers based on the generated knowledge document and will automatically request specific files when needed for deeper analysis.

## 📝 Example

Here's a sample interaction with the Q&A system:

```
> What is the main purpose of this codebase?

This codebase is designed to automate the process of answering questions from online assignments and generating comprehensive HTML reports of the results. It uses web browsing capabilities, Large Language Models (LLMs), and structured data parsing.

The system can navigate to an assignment link, extract questions and options, use an LLM to generate answers based on a knowledge base, and then create a formatted HTML report with questions, answers, explanations, and related topics.

> How does the Browser abstraction work?

[REQUEST_FILE: browser_use.py]

Looking at the codebase, the Browser abstraction serves as a wrapper around a web browser (Chrome), providing methods to interact with web pages programmatically.

The Browser class is initialized with a BrowserConfig that specifies settings like the Chrome executable path and headless mode. It handles navigation to URLs, extracting information, and simulating user interactions.

Key methods likely include initialization, navigation methods (goto), interaction methods (clicking buttons, scrolling), and extraction methods for getting data from pages...
```

## ⚠️ Limitations

- The quality of analysis depends on the quality of your codebase and comments
- Large codebases may take longer to process and might exceed token limits
- The system requires either a Google Gemini API key or an OpenAI API key

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
