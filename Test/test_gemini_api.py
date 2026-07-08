import os
from dotenv import load_dotenv

load_dotenv()

# Test with NEW SDK (google-genai) - recommended by Google
print("Testing with NEW google.genai package...")
try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Try different model names
    model_names = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "models/gemini-2.5-flash"
    ]
    
    for model_name in model_names:
        try:
            print(f"\nTrying: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents="Say hello in 3 words"
            )
            print(f"✅ SUCCESS with {model_name}")
            print(f"Response: {response.text}")
            break
        except Exception as e:
            print(f"❌ Failed: {str(e)[:100]}")
            
except ImportError:
    print("❌ google-genai package not installed. Installing...")
    print("Run: pip install google-genai")
except Exception as e:
    print(f"Error: {e}")


