from app.config import settings
import os

def verify():
    print("--- HelixOS Config Verification ---")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    
    # Check if key is loaded in settings
    key_in_settings = settings.ANTHROPIC_API_KEY
    if key_in_settings:
        print(f"ANTHROPIC_API_KEY in Settings: {key_in_settings[:10]}...{key_in_settings[-5:]}")
    else:
        print("ANTHROPIC_API_KEY in Settings: MISSING ❌")
        
    # Check if key is in os.environ (due to load_dotenv)
    key_in_env = os.environ.get("ANTHROPIC_API_KEY")
    if key_in_env:
        print(f"ANTHROPIC_API_KEY in os.environ: {key_in_env[:10]}...{key_in_env[-5:]}")
    else:
        print("ANTHROPIC_API_KEY in os.environ: MISSING ❌")
        
    if key_in_settings and key_in_env:
        print("\n✅ Verification SUCCESS: API Key is correctly loaded!")
    else:
        print("\n❌ Verification FAILED: API Key is still missing.")

if __name__ == "__main__":
    verify()
