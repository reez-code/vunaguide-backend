from typing import List, Optional

# ADK uses type hints to build the schema automatically
def submit_diagnosis_report(
    plant_name: str,
    status: str,
    confidence_score: float,
    remedies: List[str],
    local_advice: str,
    disease_name: Optional[str] = None,
    is_severe: bool = False
) -> dict:
    """
    Submits the final diagnosis report for a crop.
    
    Args:
        plant_name: The species of the plant (e.g., Maize, Tomato).
        status: Health status ('Healthy' or 'Diseased').
        confidence_score: 0-100 confidence level.
        remedies: List of 2-3 Kenyan remedies.
        local_advice: Practical advice in Swahili/English.
        disease_name: The specific disease if identified.
        is_severe: True if the disease is contagious/severe.
    """
    # In a real app, you might save this to a database here.
    # For now, we just return it so the Runner can pass it to the API.
    return {
        "plant_name": plant_name,
        "status": status,
        "disease_name": disease_name,
        "confidence_score": confidence_score,
        "remedies": remedies,
        "local_advice": local_advice,
        "sentinel_flag": is_severe
    }