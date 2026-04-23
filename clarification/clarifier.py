def generate_question(issue):
    questions = {
        "missing_app": "Which application should I open?",
        "missing_text": "What should I type?",
        "missing_key": "Which key should I press?",
        "invalid_action": "I cannot perform that action. Please rephrase.",
        "invalid_format": "I didn't understand the command properly. Can you rephrase?"
    }

    return questions.get(issue, "Something is unclear. Please clarify.")