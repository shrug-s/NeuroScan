# model.py (replace predict_from_tensor or add this updated version)
import torch
import numpy as np

# Mapping from label -> suggested treatments (short, user-facing text + source keys)
TREATMENT_DB = {
    "Alzheimer": [
        {
            "type": "pharmacologic",
            "name": "Cholinesterase inhibitors (donepezil, rivastigmine, galantamine)",
            "notes": "May help memory and cognition in mild-to-moderate Alzheimer’s disease; discuss side effects with clinician.",
            "sources": ["NIA", "NICE"]
        },
        {
            "type": "pharmacologic",
            "name": "Memantine (for moderate-to-severe disease)",
            "notes": "NMDA receptor antagonist; often used in moderate-to-severe stages.",
            "sources": ["NIA", "NICE"]
        },
        {
            "type": "nonpharmacologic",
            "name": "Cognitive rehabilitation / occupational therapy / caregiver support",
            "notes": "Non-drug interventions to support function and safety.",
            "sources": ["NIA", "NICE"]
        }
    ],
    "Parkinson": [
        {
            "type": "pharmacologic",
            "name": "Levodopa (with carbidopa)",
            "notes": "Mainstay for symptomatic treatment of bradykinesia and rigidity. Many dosing options and side effects—clinician supervision required.",
            "sources": ["NHS", "NICE"]
        },
        {
            "type": "pharmacologic",
            "name": "Dopamine agonists / MAO-B inhibitors / COMT inhibitors",
            "notes": "Used as early alternatives or add-ons to manage symptoms and 'off' periods.",
            "sources": ["NHS", "NICE"]
        },
        {
            "type": "nonpharmacologic",
            "name": "Physiotherapy, exercise, multidisciplinary care",
            "notes": "Helps mobility, gait, balance and quality of life.",
            "sources": ["NICE"]
        }
    ],
    "ALS": [
        {
            "type": "pharmacologic",
            "name": "Riluzole",
            "notes": "Modestly extends survival; requires liver monitoring.",
            "sources": ["MayoClinic"]
        },
        {
            "type": "pharmacologic",
            "name": "Edaravone (in some regions)",
            "notes": "May slow progression in selected patients; regionally approved.",
            "sources": ["PMCID"]
        },
        {
            "type": "nonpharmacologic",
            "name": "Multidisciplinary supportive care (respiratory, nutritional, PT/OT, speech)",
            "notes": "Central to maintaining function and quality of life.",
            "sources": ["MayoClinic", "PMCID"]
        }
    ],
    "LewyBody": [
        {
            "type": "pharmacologic",
            "name": "Cholinesterase inhibitors (rivastigmine, donepezil)",
            "notes": "May improve cognition and visual hallucinations in some patients.",
            "sources": ["NHS", "PMCID"]
        },
        {
            "type": "nonpharmacologic",
            "name": "Multidisciplinary support",
            "notes": "Physio/OT, sleep management, caregiver support.",
            "sources": ["NHS", "PMCID"]
        }
    ],
    "NoNeurodegenerativeSignal": [
        {
            "type": "advice",
            "name": "Lifestyle and vascular risk optimization",
            "notes": "Manage blood pressure, diabetes, stay active, treat hearing loss — reduces dementia risk.",
            "sources": ["PMCID", "NIA"]
        }
    ]
}

# human-readable source mapping to actual URLs for UI (short)
SOURCE_URLS = {
    "NIA": "https://www.nia.nih.gov/health/alzheimers-treatment/how-alzheimers-disease-treated",
    "NICE": "https://www.nice.org.uk/guidance",
    "NHS": "https://www.nhs.uk",
    "MayoClinic": "https://www.mayoclinic.org",
    "PMCID": "https://www.ncbi.nlm.nih.gov/pmc/"
}


def predict_from_tensor(model, tensor, scanner_type="MRI", info=None):
    """
    Returns dict with predictions and treatment suggestions.
    If no real model is provided (model is None), returns a demo response.
    """
    # Ensure batch dim for demo (not full production code)
    if tensor.dim() == 4:
        tensor = tensor.unsqueeze(0)

    # Demo random behavior if model is None
    if model is None:
        probs = np.random.dirichlet([1.0, 0.8, 2.0])
        labels = ["Alzheimer", "Parkinson", "NoNeurodegenerativeSignal"]
        top_idx = int(np.argmax(probs))
        top_label = labels[top_idx]
    else:
        model.eval()
        with torch.no_grad():
            out = model(tensor)
            probs = torch.softmax(out, dim=1).cpu().numpy().squeeze()
            # map indices to labels for your trained model
            labels = ["Alzheimer", "Parkinson", "Other"]
            top_idx = int(np.argmax(probs))
            top_label = labels[top_idx]

    # Lookup suggestions (fallback to generic if label not in DB)
    suggestions = TREATMENT_DB.get(top_label, [
        {"type": "advice", "name": "Specialist referral",
            "notes": "Refer to neurology for further evaluation.", "sources": ["NHS"]}
    ])

    # Attach full URL list for UI convenience
    for s in suggestions:
        s["source_links"] = {k: SOURCE_URLS.get(
            k, "") for k in s.get("sources", [])}

    # Prepare result
    result = {
        "labels": labels,
        "probs": probs.tolist() if 'probs' in locals() else None,
        "top": top_label,
        "confidence": float(max(probs)) if 'probs' in locals() else None,
        "treatment_suggestions": suggestions,
        "disclaimer": "This is informational only. Consult a licensed clinician before taking any medical action."
    }
    return result
