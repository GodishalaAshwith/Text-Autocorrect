# pyrefly: ignore [missing-import]
import gradio as gr
from autocorrect import AutocorrectModel
import difflib

def build_interface():
    # Initialize both models
    print("Loading models...")
    low_model = AutocorrectModel(mode="low")
    
    try:
        high_model = AutocorrectModel(mode="high")
    except Exception as e:
        print(f"Could not load high model: {e}")
        high_model = None

    def get_diff_html(original, corrected):
        # A simple diff function to highlight changes
        matcher = difflib.SequenceMatcher(None, original.split(), corrected.split())
        html = []
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                html.append(" ".join(original.split()[i1:i2]))
            elif op == 'delete':
                html.append(f'<span style="background-color: #ffcccc; color: #cc0000; text-decoration: line-through; padding: 0 2px; border-radius: 2px;">{" ".join(original.split()[i1:i2])}</span>')
            elif op == 'insert':
                html.append(f'<span style="background-color: #ccffcc; color: #008800; font-weight: bold; padding: 0 2px; border-radius: 2px;">{" ".join(corrected.split()[j1:j2])}</span>')
            elif op == 'replace':
                html.append(f'<span style="background-color: #ffcccc; color: #cc0000; text-decoration: line-through; padding: 0 2px; border-radius: 2px;">{" ".join(original.split()[i1:i2])}</span>')
                html.append(f'<span style="background-color: #ccffcc; color: #008800; font-weight: bold; padding: 0 2px; border-radius: 2px;">{" ".join(corrected.split()[j1:j2])}</span>')
        
        # Add some basic styling for the container
        return f'<div style="font-family: sans-serif; font-size: 1.1em; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background: #fff;">{" ".join(html)}</div>'

    def correct_single(text, mode, num_suggestions):
        if not text.strip():
            return "", "", ""
            
        model = high_model if mode == "High-End (Transformers)" and high_model else low_model
        
        # Get multiple suggestions
        results = model.correct(text, num_return_sequences=int(num_suggestions))
        
        primary = results[0] if isinstance(results, list) else results
        
        if isinstance(results, list) and len(results) > 1:
            alternatives = "\n".join([f"{i+1}. {r}" for i, r in enumerate(results[1:])])
        else:
            alternatives = "No other suggestions found."
        
        diff_html = get_diff_html(text, primary)
        
        return diff_html, primary, alternatives

    def correct_file(file_obj, mode):
        if file_obj is None:
            return None
            
        model = high_model if mode == "High-End (Transformers)" and high_model else low_model
        
        with open(file_obj.name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        corrected_lines = []
        for line in lines:
            if not line.strip():
                corrected_lines.append("\n")
                continue
            # Correct each line
            corrected = model.correct(line.strip(), num_return_sequences=1)
            primary = corrected[0] if isinstance(corrected, list) else corrected
            corrected_lines.append(primary + "\n")
            
        out_filename = "corrected_document.txt"
        with open(out_filename, 'w', encoding='utf-8') as f:
            f.writelines(corrected_lines)
            
        return out_filename

    # Define the Gradio Interface
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# ✍️ AI Autocorrect Pro")
        gr.Markdown("Experience next-gen spelling and grammar correction with visual diffs and batch document processing.")
        
        with gr.Tabs():
            # TAB 1: Single Sentence Correction
            with gr.TabItem("Interactive Correction"):
                with gr.Row():
                    with gr.Column():
                        input_text = gr.Textbox(label="Original Text", placeholder="Type your sentence here...", lines=4)
                        mode_selector = gr.Radio(choices=["Low-End (TextBlob)", "High-End (Transformers)"], value="High-End (Transformers)", label="Correction Mode")
                        num_sug = gr.Slider(minimum=1, maximum=5, step=1, value=3, label="Number of Alternative Suggestions")
                        submit_btn = gr.Button("Correct Text", variant="primary")
                        
                    with gr.Column():
                        gr.Markdown("### Visual Diff")
                        diff_output = gr.HTML(value="<i>Type text and click 'Correct Text' to see changes...</i>")
                        primary_output = gr.Textbox(label="Primary Correction", lines=2, interactive=False)
                        alt_output = gr.Textbox(label="Alternative Suggestions", lines=3, interactive=False)
                        
                submit_btn.click(fn=correct_single, inputs=[input_text, mode_selector, num_sug], outputs=[diff_output, primary_output, alt_output])
            
            # TAB 2: Batch Document Processing
            with gr.TabItem("Batch Document Processing"):
                gr.Markdown("Upload a `.txt` file. The AI will process it line-by-line and give you a new file to download.")
                with gr.Row():
                    with gr.Column():
                        file_input = gr.File(label="Upload .txt File", file_types=[".txt"])
                        batch_mode_selector = gr.Radio(choices=["Low-End (TextBlob)", "High-End (Transformers)"], value="High-End (Transformers)", label="Correction Mode")
                        process_btn = gr.Button("Process Document", variant="primary")
                    with gr.Column():
                        file_output = gr.File(label="Download Corrected File")
                        
                process_btn.click(fn=correct_file, inputs=[file_input, batch_mode_selector], outputs=file_output)

    return demo

if __name__ == "__main__":
    demo = build_interface()
    # share=True creates a public link
    demo.launch(share=False)
