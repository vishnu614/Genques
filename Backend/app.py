import random
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import spacy
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/generate_questions": {"origins": "http://localhost:3000"}})  # Assuming frontend is running on localhost:3000

# Load spaCy English model and T5 model for question generation
nlp = spacy.load("en_core_web_sm")
model_name = "mrm8488/t5-base-finetuned-question-generation-ap"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Function to split text into sentences
def split_text_into_sentences(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return sentences

# Function to generate a question using the model
def generate_question(sentence):
    inputs = tokenizer.encode(f"generate question: {sentence}", return_tensors="pt")
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Function to generate questions based on input type, applied to each sentence
def generate_questions_from_sentences(sentences, question_type, num_questions):
    questions = []
    unique_questions = set()  # Set to keep track of unique question texts

    for sentence in sentences:
        doc = nlp(sentence)
       
        entities = [ent.text for ent in doc.ents]
        nouns = [token.text for token in doc if token.pos_ == "NOUN"]
        

        # Generate MCQ questions
        if question_type == "MCQ" and entities + nouns:
            for _ in range(num_questions):
                question_topic = random.choice(entities + nouns)
                question_text = generate_question(sentence)
                options = list(set(random.sample(entities + nouns, min(3, len(entities + nouns))) + [question_topic]))
                random.shuffle(options)
                if question_text not in unique_questions:
                    questions.append({"question": question_text, "options": options})
                    unique_questions.add(question_text)

        # Generate Fill-in-the-Blank questions
        elif question_type == "Fill in the Blanks" and nouns:
            fillup_noun = random.choice(nouns)
            fillup = f"{sentence.replace(fillup_noun, '__________')} (Fill in the blank)"
            if fillup not in unique_questions:
                questions.append({"question": fillup})
                unique_questions.add(fillup)

        # Generate Short Answer questions
        elif question_type == "Short Answer" and nouns:
            for _ in range(num_questions):
                question_topic = random.choice(entities + nouns)
                question_text = generate_question(sentence)
                if question_text not in unique_questions:
                    questions.append({"question": question_text})
                    unique_questions.add(question_text)

    return questions

# Define API endpoint for question generation
@app.route('/generate_questions', methods=['POST'])
def generate_questions_api():
    data = request.get_json()
    text = data.get("text")
    question_type = data.get("question_type")
    num_questions = int(data.get("num_questions"))

    # Split text into sentences
    sentences = split_text_into_sentences(text)
    print("in the duncion")

    # Generate questions based on sentences
    questions = generate_questions_from_sentences(sentences, question_type, num_questions+4)

    return jsonify({"questions": questions[:num_questions]})

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
