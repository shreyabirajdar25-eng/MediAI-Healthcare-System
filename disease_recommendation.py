def get_recommendation(disease):

    recommendations = {

        "Allergic Rhinitis": {
            "Medicine": "Antihistamines (as prescribed by doctor)",
            "Diet": "Warm fluids, fruits and vegetables",
            "Exercise": "Light exercise and breathing exercises",
            "Water": "2.5-3 Litres/day",
            "Precautions": "Avoid dust, pollen, smoke and allergens"
        },

        "Bronchitis": {
            "Medicine": "Cough syrup and medicines prescribed by doctor",
            "Diet": "Warm soup, fruits and balanced diet",
            "Exercise": "Breathing exercises and proper rest",
            "Water": "3 Litres/day",
            "Precautions": "Avoid smoking and dust"
        },

        "Diabetes": {
            "Medicine": "Medicines as prescribed by doctor",
            "Diet": "Low sugar and balanced diet",
            "Exercise": "30 minutes walking daily",
            "Water": "2.5 Litres/day",
            "Precautions": "Monitor blood sugar regularly"
        }

    }


    return recommendations.get(

        disease,

        {
            "Medicine": "Consult a Doctor",
            "Diet": "Healthy Balanced Diet",
            "Exercise": "As advised by your doctor",
            "Water": "2-3 Litres/day",
            "Precautions": "Medical consultation recommended"
        }

    )