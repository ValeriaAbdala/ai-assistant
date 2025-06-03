import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    exit()

print(f"✅ API Key loaded: {api_key[:10]}...")

try:
    # Configurar Gemini
    genai.configure(api_key=api_key)
    
    print("\n" + "="*50)
    print("🤖 AVAILABLE GEMINI MODELS")
    print("="*50)
    
    models_found = []
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            models_found.append(model.name)
            print(f"✅ {model.name}")
            print(f"   - Display name: {model.display_name}")
            print(f"   - Description: {model.description}")
            print("-" * 40)
    
    print(f"\n📊 Total models available: {len(models_found)}")
    
    # Probar el primer modelo disponible
    if models_found:
        test_model = models_found[0]
        print(f"\n🧪 Testing model: {test_model}")
        model = genai.GenerativeModel(test_model)
        response = model.generate_content("Hello! Are you working correctly?")
        print(f"✅ Test response: {response.text[:100]}...")
    else:
        print("❌ No models available for generateContent")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print("\nPossible solutions:")
    print("1. Check your API key is correct")
    print("2. Make sure you have access to Gemini API")
    print("3. Check if your region supports Gemini")