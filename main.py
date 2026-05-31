import argparse
import sys
from autocorrect import AutocorrectModel

def main():
    parser = argparse.ArgumentParser(description="Autocorrect AI Tool")
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["low", "high"], 
        default="low",
        help="Mode to run the autocorrect in. 'low' for fast local TextBlob correction, 'high' for context-aware Transformer correction."
    )
    parser.add_argument(
        "--text", 
        type=str, 
        help="The text to correct. If not provided, you will be prompted to enter text interactively."
    )

    args = parser.parse_args()

    print(f"Loading Autocorrect Model in '{args.mode.upper()}' mode...")
    
    try:
        model = AutocorrectModel(mode=args.mode)
    except Exception as e:
        print(f"Error initializing model: {e}")
        sys.exit(1)

    if args.text:
        print("\nOriginal Text :", args.text)
        corrected = model.correct(args.text)
        print("Corrected Text:", corrected)
    else:
        print("\nEnter sentences to correct (type 'exit' or 'quit' to stop):")
        while True:
            try:
                user_input = input(">> ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input.strip():
                    continue
                
                corrected = model.correct(user_input)
                print(">>", corrected)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
