from owlready2 import *
import numpy as np
from scipy.spatial.distance import cosine
from flask import Flask, render_template, request

app = Flask(__name__)

# Load the ontology
onto = get_ontology("calculus.rdf").load()

# Use a mock or placeholder vector dictionary for demonstration purposes
# Replace with actual vector loading or predefine some vectors if needed
word_vectors = {
    "differentiation": np.array([0.1, 0.2, 0.3]),
    "integration": np.array([0.2, 0.1, 0.4]),
    "limits": np.array([0.3, 0.4, 0.1])
}

SYNONYMS = {
    "differentiation": "differentiation",
    "integration": "integration",
    "limits": "limits",
    "area under curve": "integration",
    "slope": "differentiation",
    "continuity": "limits"
}

def query_ontology(concept):
    normalized_concept = concept.strip().lower()

    # Handle synonyms
    normalized_concept = SYNONYMS.get(normalized_concept, normalized_concept)

    # Vector for the input concept
    if normalized_concept in word_vectors:
        concept_vector = word_vectors[normalized_concept]
    else:
        return "The concept you entered was not found in the vocabulary."

    closest_match = None
    highest_similarity = 0

    for individual in onto.individuals():
        labels = [lbl.lower() for lbl in getattr(individual, "label", [])]
        for label in labels:
            if label in word_vectors:
                label_vector = word_vectors[label]
                # Use SciPy's cosine distance (1 - cosine similarity)
                similarity = 1 - cosine(concept_vector, label_vector)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    closest_match = individual

    if closest_match:
        formula = getattr(closest_match, "hasFormula", None)
        explanation = getattr(closest_match, "hasExplanation", None)

        formula_text = (formula[0].strip() if isinstance(formula, list) else formula.strip()) if formula else "Formula not available."
        explanation_text = (explanation[0].strip() if isinstance(explanation, list) else explanation.strip()) if explanation else "Explanation not available."

        return f"<strong>Formula:</strong> {formula_text}<br><strong>Explanation:</strong> {explanation_text}"

    return "The concept you entered was not found. Please try again."

def suggest_related_concepts(concept):
    """Suggest related concepts based on the similarity to existing ontology concepts."""
    normalized_concept = concept.strip().lower()
    if normalized_concept not in word_vectors:
        return []

    concept_vector = word_vectors[normalized_concept]
    related_concepts = []

    for individual in onto.individuals():
        labels = [lbl.lower() for lbl in getattr(individual, "label", [])]
        for label in labels:
            if label in word_vectors:
                label_vector = word_vectors[label]
                similarity = 1 - cosine(concept_vector, label_vector)
                if similarity > 0.7:  # Threshold for relatedness
                    related_concepts.append(label)

    return related_concepts

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/calculus', methods=['GET', 'POST'])
def calculus():
    if request.method == 'POST':
        concept = request.form['concept']
        result = query_ontology(concept)
        return render_template('calculus.html', concept=concept, response=result)
    return render_template('calculus.html', concept=None, response=None)

@app.route('/ontology', methods=['GET'])
def show_ontology():
    ontology_data = []
    for individual in onto.individuals():
        labels = getattr(individual, "label", [])
        formula = getattr(individual, "hasFormula", ["Not available"])
        explanation = getattr(individual, "hasExplanation", ["Not available"])
        ontology_data.append({
            "labels": labels,
            "formula": formula[0] if isinstance(formula, list) else formula,
            "explanation": explanation[0] if isinstance(explanation, list) else explanation
        })
    return render_template('ontology.html', ontology_data=ontology_data)

if __name__ == "__main__":
    app.run(debug=True)
