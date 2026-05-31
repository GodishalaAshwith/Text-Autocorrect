import re

class AutocorrectModel:
    def __init__(self, mode="low"):
        """
        Initializes the Autocorrect tool.
        :param mode: 'low' for TextBlob, 'high' for Transformer-based model (BERT/T5)
        """
        self.mode = mode.lower()
        
        if self.mode == "low":
            try:
                # pyrefly: ignore [missing-import]
                from textblob import TextBlob
                self.TextBlob = TextBlob
                print("Initialized Low-end mode (TextBlob).")
            except ImportError:
                raise ImportError("Please install textblob: pip install textblob")
                
        elif self.mode == "high":
            try:
                # pyrefly: ignore [missing-import]
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                # pyrefly: ignore [missing-import]
                import torch
                print("Initializing High-end mode (Transformers)... This may take a moment to load the model.")
                
                model_name = "vennify/t5-base-grammar-correction"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                # tie_word_embeddings=False silences a harmless warning
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, tie_word_embeddings=False)
                
                # Move to GPU if available
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model = self.model.to(self.device)
                
                print(f"High-end mode initialized on {self.device.upper()}.")
            except ImportError:
                raise ImportError("Please install transformers and torch: pip install transformers torch")
        else:
            raise ValueError("Mode must be either 'low' or 'high'")

    def correct_low_end(self, text, num_return_sequences=1):
        """
        Uses TextBlob to correct spelling. Returns a list if num_return_sequences > 1.
        """
        blob = self.TextBlob(text)
        corrected = str(blob.correct())
        return [corrected] if num_return_sequences > 1 else corrected

    def correct_high_end(self, text, num_return_sequences=1):
        """
        Uses a Transformer model to correct grammar and contextual spelling.
        Supports returning multiple alternative suggestions.
        """
        input_text = "grammar: " + text
        
        # Tokenize and move to device
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        
        # Generate correction(s)
        outputs = self.model.generate(
            **inputs, 
            max_length=128,
            num_return_sequences=num_return_sequences,
            num_beams=max(5, num_return_sequences), # Beam search for better alternatives
            early_stopping=True
        )
        
        # Decode the output
        results = [self.tokenizer.decode(out, skip_special_tokens=True) for out in outputs]
        
        # Remove duplicates
        unique_results = []
        for r in results:
            if r not in unique_results:
                unique_results.append(r)
                
        if num_return_sequences > 1:
            return unique_results
        else:
            return unique_results[0] if unique_results else text

    def correct(self, text, num_return_sequences=1):
        """
        Main interface to correct text based on the selected mode.
        """
        if self.mode == "low":
            return self.correct_low_end(text, num_return_sequences)
        elif self.mode == "high":
            return self.correct_high_end(text, num_return_sequences)

if __name__ == "__main__":
    # Simple test if run directly
    text = "I like your short."
    
    print("Original:", text)
    
    # Test high
    # try:
    #     high_model = AutocorrectModel(mode="high")
    #     print("High mode (1):", high_model.correct(text))
    #     print("High mode (3):", high_model.correct(text, num_return_sequences=3))
    # except Exception as e:
    #     print(e)
