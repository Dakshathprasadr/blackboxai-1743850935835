import spacy
from spacy.matcher import PhraseMatcher
import random

# Load English language model
nlp = spacy.load("en_core_web_sm")

# Define common health patterns and responses
health_patterns = {
    "headache": [
        "For headaches, try resting in a quiet room and drinking water.",
        "A mild headache can be treated with over-the-counter pain relievers."
    ],
    "fever": [
        "For fever, drink plenty of fluids and rest.",
        "If fever persists above 102°F, consult a doctor."
    ],
    "cut": [
        "Clean the cut with water and apply antibiotic ointment.",
        "For deep cuts, apply pressure and seek medical attention."
    ],
    "burn": [
        "Cool the burn with running water for 10-15 minutes.",
        "Don't apply ice or butter to burns."
    ]
}

# Create phrase matcher
matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp(text) for text in health_patterns.keys()]
matcher.add("HEALTH", patterns)

def process_message(message):
    doc = nlp(message.lower())
    matches = matcher(doc)
    
    if matches:
        # Get the matched pattern
        match_id, start, end = matches[0]
        pattern = doc[start:end].text
        
        # Return a random response for the matched pattern
        return random.choice(health_patterns.get(pattern, ["I understand you're not feeling well. Can you describe your symptoms in more detail?"]))
    
    # Default response if no pattern matches
    return "I'm sorry, I didn't understand that. Could you describe your symptoms differently?"

def analyze_symptoms(symptoms):
    doc = nlp(symptoms)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Emergency conditions
    emergency_keywords = ["chest pain", "difficulty breathing", "severe bleeding", 
                         "sudden weakness", "loss of consciousness"]
    if any(keyword in symptoms.lower() for keyword in emergency_keywords):
        return {
            "advice": "🚨 EMERGENCY - Seek immediate medical attention!",
            "severity": "critical",
            "action": "Call emergency services or go to ER immediately"
        }
    
    # Urgent care conditions
    urgent_keywords = ["high fever", "severe pain", "head injury", 
                      "persistent vomiting", "burn"]
    if any(keyword in symptoms.lower() for keyword in urgent_keywords):
        return {
            "advice": "⚠️ Urgent - See a doctor within 24 hours",
            "severity": "high",
            "action": "Book urgent appointment or visit urgent care"
        }
    
    # Routine care
    routine_keywords = ["cold", "cough", "mild pain", "rash", "allergies"]
    if any(keyword in symptoms.lower() for keyword in routine_keywords):
        return {
            "advice": "🩺 Routine - Schedule a doctor visit when convenient",
            "severity": "medium", 
            "action": "Book GP appointment within 3-5 days"
        }
    
    # Self-care
    return {
        "advice": "💊 Self-care - Monitor symptoms at home",
        "severity": "low",
        "action": "Rest and try over-the-counter remedies. Contact doctor if symptoms worsen"
    }
