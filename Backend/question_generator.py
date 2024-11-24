# question_generator.py
import fitz  # PyMuPDF for PDFs
from docx import Document
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

# Initialize the T5 model and tokenizer
model_name = "t5-small"  # You can use "t5-base" or "t5-large" for better results with a larger model
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    text = ""
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def generate_question(text, question_type):
    """Generates a question based on text input and specified type using T5 model."""
    # Prepare the input based on the desired question type
    if question_type == "MCQ":
        prompt = f"generate a multiple choice question: {text}"
    elif question_type == "Fill in the blanks":
        prompt = f"generate a fill-in-the-blank question: {text}"
    elif question_type == "True or False":
        prompt = f"generate a true or false question: {text}"
    elif question_type == "Matching":
        prompt = f"generate a matching question: {text}"
    else:
        return "Invalid question type specified."

    # Tokenize the prompt and generate output
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(input_ids, max_length=100, num_beams=5, early_stopping=True)

    # Decode and return the generated question
    question = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return question

# Example functions to combine steps:
def generate_questions_from_file(file_path, file_type, question_type):
    """Extracts text from file and generates a question of the specified type."""
    if file_type == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_type == "docx":
        text = extract_text_from_docx(file_path)
    else:
        return "Unsupported file type"

    # Generate the question using the first 512 characters from the beginning of the text
    question = generate_question(text[:512], question_type)
    return question
