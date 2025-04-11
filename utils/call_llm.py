import google.generativeai as genai
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(prompt):    
    # Try Google Gemini first
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if api_key:
        try:
            # Configure the API
            genai.configure(api_key=api_key)
            
            # Try to list models (quietly)
            try:
                models = genai.list_models()
                model_names = [model.name for model in models]
                logger.debug("Available models: %s", model_names)
                
                # Try to find gemini models
                gemini_model = None
                
                # Preferred models in order of preference
                preferred_models = [
                    "models/gemini-2.0-flash",
                    "models/gemini-1.5-pro",
                    "models/gemini-1.5-flash",
                    "models/gemini-2.0-pro",
                ]
                
                # First try to find any of the preferred models
                for preferred in preferred_models:
                    for name in model_names:
                        if preferred in name:
                            gemini_model = name
                            break
                    if gemini_model:
                        break
                
                # If none of the preferred models are found, try to find any gemini model
                if not gemini_model:
                    for name in model_names:
                        if "gemini" in name and "pro" in name and "vision" not in name:
                            gemini_model = name
                            break
                        
                    if not gemini_model:
                        for name in model_names:
                            if "gemini" in name and "flash" in name:
                                gemini_model = name
                                break
                
                if gemini_model:
                    logger.info("🤖 Using Google Gemini model: %s", gemini_model)
                    model = genai.GenerativeModel(gemini_model)
                else:
                    logger.info("🤖 No specific Gemini model found. Using gemini-1.5-pro...")
                    model = genai.GenerativeModel("gemini-1.5-pro")
            except Exception as model_error:
                logger.warning("⚠️ Error listing models: %s", model_error)
                logger.info("🤖 Falling back to gemini-1.5-pro...")
                model = genai.GenerativeModel("gemini-1.5-pro")
            
            # Generate content with appropriate safety settings
            safety_settings = {
                "HARASSMENT": "BLOCK_NONE",
                "HATE": "BLOCK_NONE",
                "SEXUAL": "BLOCK_NONE",
                "DANGEROUS": "BLOCK_NONE",
            }
            
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            logger.info("🧠 Generating content with Google Gemini...")
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            # Return the text response
            return response.text
        except Exception as e:
            logger.error("❌ Google Gemini API error: %s", e)
            logger.info("🔄 Trying OpenAI as fallback...")
    
    # Try OpenAI as fallback
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            logger.info("🤖 Using OpenAI as fallback...")
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as openai_error:
            logger.error("❌ OpenAI API error: %s", openai_error)
    
    # If all else fails
    logger.error("\n❌ ERROR: Could not use any LLM API! ❌")
    logger.error("Please set either GOOGLE_API_KEY or OPENAI_API_KEY environment variables:")
    logger.error("\nOn Windows PowerShell:")
    logger.error("$env:GOOGLE_API_KEY = \"your-google-api-key-here\"")
    logger.error("$env:OPENAI_API_KEY = \"your-openai-api-key-here\"")
    logger.error("\nYou can get API keys from:")
    logger.error("- Google: https://makersuite.google.com/app/apikey")
    logger.error("- OpenAI: https://platform.openai.com/api-keys")
    sys.exit(1)

if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))
