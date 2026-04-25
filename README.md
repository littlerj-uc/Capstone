# Capstone
ProcessPilot
Process Documentation Assistant
ProcessPilot is a Streamlit-based web application that transforms rough, unstructured process descriptions into clear, professional Standard Operating Procedures (SOPs). It is designed to support both users who prefer to provide a complete “brain dump” of a process and users who benefit from guided, conversational prompting.
This project was developed as a capstone to explore ambiguity handling, user-centered AI design, and real-world documentation workflows.

KEY FEATURES
Freeform Input Mode

Users paste a full process description in their own words
The system immediately generates structured documentation
No follow-up questions or interruptions

Guided Assistant Mode

Users can start with partial or ambiguous input
The AI asks targeted clarification questions such as triggers, roles, or exceptions
The conversation loops until the user types DONE
Final output is a polished SOP based on clarified information

Structured SOP Output
All generated documentation follows a consistent structure:

Process Overview
Trigger
Roles and Responsibilities
Prerequisites
Step-by-Step Instructions
Exception Handling
Completion Criteria
Notes and Tips

Clean, Professional Interface

Custom dark-theme UI designed for documentation work
No chat bubbles; interaction occurs through a single text area
Emphasis on clarity, focus, and usability


DESIGN RATIONALE
A core goal of ProcessPilot is to handle ambiguity without overwhelming the user. Instead of forcing all users into a chatbot-style workflow, the application provides two interaction modes:
Freeform mode supports users who already understand their process and want fast results.
Guided Assistant mode supports users who may be unsure, incomplete, or thinking through the process as they describe it.
This dual-mode design reflects real-world documentation work, where users often alternate between structured thinking and exploratory clarification.

TECHNOLOGY STACK

Python 3
Streamlit for the web interface
Anthropic Claude API for language reasoning and generation
Custom CSS for styling and layout


RUNNING THE APPLICATION LOCALLY


Clone the repository
git clone https://github.com/your-username/processpilot.git
cd processpilot


Install dependencies
pip install -r requirements.txt


Add your Anthropic API key
Create a file at .streamlit/secrets.toml with the following content:
ANTHROPIC_API_KEY = "your_api_key_here"
This file should not be committed to version control.


Start the application
streamlit run app.py



PROJECT STRUCTURE
processpilot/

app.py               Main Streamlit application
requirements.txt     Python dependencies
README.txt           Project documentation (this file)
.gitignore           Prevents secrets and cache files from being committed
.streamlit/

secrets.toml       Local API key (not committed)




FUTURE ENHANCEMENTS
Potential future improvements include:

Voice input and transcription
Confidence indicators for ambiguous input
Guided progress indicators during clarification
Export to Word or PDF
User feedback loops for iterative SOP improvement


CAPSTONE OUTCOMES
This project demonstrates:

Real-world AI API integration
UX design for ambiguous and incomplete input
User-controlled interaction modes
Clean separation of interface, logic, and AI behavior
Practical application of human-centered design principles
