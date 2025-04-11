# 🤖 AI-Powered Code Reviewer & Codebase Assistant

Have a conversation with your code! This intelligent assistant analyzes your codebase and allows you to chat with it as if it were a senior developer intimately familiar with your project.

Built on the [PocketFlow](https://github.com/the-pocket/PocketFlow) framework, this tool combines AI code analysis with an interactive chat interface to:

1. **Analyze your codebase** to identify key components and their relationships
2. **Generate detailed documentation** automatically explaining each abstraction
3. **Answer your questions** about how the code works, why decisions were made, and where to find specific functionality
4. **Review your code** by examining patterns, identifying potential issues, and suggesting improvements

## 💬 Chat With Your Codebase

Instead of spending hours trying to understand unfamiliar code, just ask questions in plain English:

```
> How does authentication work in this app?
> What design patterns are used in the data processing module?
> Where is the API rate limiting implemented?
> What would be the best way to implement a new feature for X?
```

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
   cd Agentic-Reviewer
   ```

2. Install dependencies:
   ```bash
   pip install requirements.txt
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

### Step 1: Build Knowledge of Your Codebase

First, let the AI analyze your code:

```bash
python main.py --dir path/to/your/codebase
```

Or analyze directly from GitHub:
```bash
python main.py --github https://github.com/username/repo
```

This creates a `codebase_knowledge.md` document with a comprehensive analysis of your codebase architecture.

### Step 2: Start Chatting With Your Codebase

Launch the interactive chat session:

```bash
python codebase_qa.py --knowledge codebase_knowledge.md --dir path/to/your/codebase
```

Or for GitHub repositories:
```bash
python codebase_qa.py --knowledge codebase_knowledge.md --github https://github.com/username/repo
```

Then start asking questions like you would to a senior developer who knows the codebase inside out:

```
> What are the core components of this system?
> How does error handling work across the application?
> Can you explain the data flow from user input to database storage?
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
