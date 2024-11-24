import React, { useState } from 'react';
import axios from "axios";
import { Oval } from "react-loader-spinner"; // Fancy Loader
import jsPDF from "jspdf";
import html2canvas from "html2canvas"; // For capturing the questions section and converting it to PDF
import '../App.css'


export default function Ques() {
    
    const [text, setText] = useState("");
    const [questionType, setQuestionType] = useState("MCQ");
    const [numQuestions, setNumQuestions] = useState(1);
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleGenerateQuestions = async () => {
      setLoading(true);
      try {
        const response = await axios.post("http://localhost:5000/generate_questions", {
          text,
          question_type: questionType,
          num_questions: numQuestions,
        });
        setQuestions(response.data.questions);
      } catch (error) {
        console.error("Error generating questions:", error);
      }
      setLoading(false);
    };

    // Function to download the questions as a PDF
    const downloadPDF = () => {
        const doc = new jsPDF();
        
        let yPosition = 20; // Initial position for text
        
        // Title for the PDF
        doc.setFontSize(18);
        doc.text("Generated Questions", 10, yPosition);
        yPosition += 10; // Increase position for next line
        
        // Loop through questions and add them to the PDF
        questions.forEach((q, index) => {
            doc.setFontSize(12);
            doc.text(`Q${index + 1}: ${q.question}`, 10, yPosition);
            yPosition += 10;
            
            if (q.options) {
                q.options.forEach((option, idx) => {
                    doc.text(`- ${option}`, 10, yPosition);
                    yPosition += 8;
                });
            }
            
            // Add a little spacing between questions
            yPosition += 10;
        });
    
        // Save the PDF
        doc.save("generated_questions.pdf");
    };
    
    return (
      <div className="App">
        <h1>Question Generator</h1>

        <div className="form-container">
          <textarea
            placeholder="Enter text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows="5"
          />

          <select
            value={questionType}
            onChange={(e) => setQuestionType(e.target.value)}
          >
            <option value="MCQ">Multiple Choice Questions</option>
            <option value="Fill in the Blanks">Fill in the Blanks</option>
            <option value="Short Answer">Short Answer Questions</option>
          </select>

          <input
            type="number"
            min="1"
            max="10"
            value={numQuestions}
            onChange={(e) => setNumQuestions(e.target.value)}
            placeholder="Number of questions (max 10)"
          />

          <button onClick={handleGenerateQuestions} disabled={loading}>
            {loading ? <Oval color="#fff" height={20} width={20} /> : "Generate Questions"}
          </button>
        </div>

        <div className="output-container" id="questions-section">
          <h2>Generated Questions:</h2>
          {questions.map((q, index) => (
            <div key={index} className="question">
              <p><strong>Q{index + 1}:</strong> {q.question}</p>
              {q.options && (
                <ul>
                  {q.options.map((option, idx) => (
                    <li key={idx}>{option}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>

        {questions.length > 0 && (
          <button onClick={downloadPDF}>
            Download as PDF
          </button>
        )}
      </div>
    );
}
