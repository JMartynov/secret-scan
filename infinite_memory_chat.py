import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from detector import SecretDetector

# Load environment variables from .env file
load_dotenv()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment or .env file.")
        print("Please set it using: export OPENAI_API_KEY='your-key'")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    detector = SecretDetector(entropy_threshold=float(os.getenv("ENTROPY_THRESHOLD", "3.5")))
    
    print("--- LLM Secrets Leak Detector Chat ---")
    print("Type 'exit' or 'quit' to stop.")
    print("All your prompts are scanned for secrets before being sent to the LLM.")
    print("-" * 40)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Scan for secrets
            findings = detector.scan(user_input)
            if findings:
                print("\n" + detector.format_report(findings))
                confirm = input("⚠ Potential secrets detected! Do you still want to send this prompt? (y/n): ")
                if confirm.lower() != 'y':
                    print("Prompt cancelled. Please remove the secrets and try again.")
                    continue
            
            messages.append({"role": "user", "content": user_input})

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            assistant_message = response.choices[0].message.content
            print(f"\nAssistant: {assistant_message}")
            messages.append({"role": "assistant", "content": assistant_message})

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
