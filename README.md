## Time to have a conversation with your codebase...
# Code Reviewer & Codebase Assistant

Have a conversation with your code! This intelligent assistant analyzes your codebase and allows you to chat with it as if it were a senior developer intimately familiar with your project.

This tool can do:
1. **Analyze your codebase** to identify key components and their relationships
2. **Generate detailed documentation** automatically explaining each abstraction
3. **Answer your questions** about how the code works, why decisions were made, and where to find specific functionality
4. **Review your code** by examining patterns, identifying potential issues, and suggesting improvements

## 💬 Chat With Your Codebase

Instead of spending hours trying to understand unfamiliar code, just ask questions in plain English:

![demo](https://github.com/user-attachments/assets/d7b318bf-3c12-4ca4-8ba1-f4bfdf344c58)
![image](https://github.com/user-attachments/assets/ac838de7-fd88-4e9d-b961-c4f85d2d82fd)


Your AI assistant analyzes the codebase knowledge it built and responds with accurate, contextual answers - even accessing specific code files when needed for deeper insights.

## 📋 Key Features

- **Interactive Code Chat**: Have a natural conversation about your codebase with an AI that understands its structure
- **Automatic Knowledge Building**: Identifies core abstractions and generates comprehensive documentation
- **Intelligent File Access**: The system can request specific files when needed to answer detailed questions
- **Code Review Capabilities**: Get insights into code quality, patterns, and potential improvements
- **GitHub Integration**: Analyze any GitHub repository with a single command - no local clone needed

## 🔧 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/XERO47/Agentic-Reviewer
   cd ai-code-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
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

## 🚀 How To Use

It's just one command to analyze your code and start chatting:

```bash
python main.py --dir path/to/your/codebase
```

Or analyze directly from GitHub:
```bash
python main.py --github https://github.com/username/repo
```

This will:
1. Analyze your codebase to build a knowledge document
2. Automatically launch an interactive chat interface
3. Let you ask questions about your code to understand it better

### Command Options

- `--dir PATH` - Specify the local codebase directory to analyze (default: current directory)
- `--github URL` - Analyze a GitHub repository instead of a local directory
- `--output FILE` - Set the output file for the knowledge document (default: codebase_knowledge.md)
- `--chat` - Start the chat interface after building knowledge (enabled by default)
- `--skip-build` - Skip knowledge building and use an existing knowledge document
- `--example` - Use a built-in example codebase for demonstration purposes

### Common Use Cases

**Only build the knowledge document without chatting:**
```bash
python main.py --dir path/to/codebase --chat=False
```

**Just chat using an existing knowledge document:**
```bash
python main.py --dir path/to/codebase --skip-build
```

**Analyze a GitHub repo and save knowledge to a custom file:**
```bash
python main.py --github https://github.com/username/repo --output my_project_docs.md
```

## 📝 Example Conversation

Here's how a conversation with your codebase might look:

```
> What's the overall architecture of this system?

This application follows a layered architecture with clear separation of concerns:

1. **Presentation Layer**: React-based frontend components in /src/components
2. **Service Layer**: API controllers and service classes in /src/services
3. **Data Access Layer**: Repository pattern implementation in /src/repositories
4. **Domain Model**: Core business entities in /src/models

The system uses dependency injection throughout and follows the CQRS pattern for more complex operations.

> Show me how authentication works

[REQUEST_FILE: src/services/auth-service.js]

Based on the codebase, authentication is implemented using JWT tokens with the following flow:

1. User credentials are validated in `AuthService.login()`
2. Upon successful validation, a JWT token is generated with user claims
3. Token is returned to client and stored in localStorage
4. Subsequent requests use an auth interceptor to attach the token
5. Protected routes use the `AuthGuard` middleware to verify tokens

Here's the key authentication method from auth-service.js:
```javascript
async login(username, password) {
  const user = await this.userRepo.findByUsername(username);
  if (!user || !this.verifyPassword(password, user.passwordHash)) {
    throw new AuthenticationError('Invalid credentials');
  }
  
  const token = jwt.sign({
    id: user.id,
    roles: user.roles
  }, config.jwtSecret, { expiresIn: '24h' });
  
  return { token, user: this.sanitizeUser(user) };
}
```
```

## ⚠️ Limitations

- The quality of analysis depends on the clarity and structure of your codebase
- Large codebases may take longer to process and might exceed token limits
- The system requires either a Google Gemini API key or an OpenAI API key

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
