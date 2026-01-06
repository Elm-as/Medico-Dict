#!/usr/bin/env python3
"""
Script to enhance the disease database with normalized symptoms,
extended descriptions, and semantic clustering for improved TF-IDF search.
"""

import json
import re
from typing import Dict, List, Set
from pathlib import Path


class SymptomNormalizer:
    """Normalizes symptoms using thesaurus and ontology."""
    
    def __init__(self, thesaurus_path: str, ontology_path: str):
        with open(thesaurus_path, 'r', encoding='utf-8') as f:
            self.thesaurus = json.load(f)
        with open(ontology_path, 'r', encoding='utf-8') as f:
            self.ontology = json.load(f)
        
        # Build reverse mapping from variations to canonical forms
        self.variation_to_canonical = {}
        self.symptom_to_cluster = {}
        
        for canonical, data in self.thesaurus['symptom_synonyms'].items():
            for variation in data['variations']:
                normalized = self.normalize_text(variation)
                self.variation_to_canonical[normalized] = {
                    'canonical': canonical,
                    'canonical_form': data['canonical_form'],
                    'medical_term': data['medical_term'],
                    'patient_terms': data['patient_terms'],
                    'cluster': data['semantic_cluster'],
                    'secondary_clusters': data.get('secondary_clusters', [])
                }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text by removing accents and lowercasing."""
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove accents
        accent_map = self.thesaurus['normalization_rules']['accents_removal']
        for accented, plain in accent_map.items():
            text = text.replace(accented, plain)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def find_canonical_form(self, symptom: str) -> Dict:
        """Find canonical form and metadata for a symptom."""
        normalized = self.normalize_text(symptom)
        
        # Direct match
        if normalized in self.variation_to_canonical:
            return self.variation_to_canonical[normalized]
        
        # Partial match - check if normalized symptom contains any known term
        for known_normalized, data in self.variation_to_canonical.items():
            if known_normalized in normalized or normalized in known_normalized:
                return data
        
        # No match found
        return {
            'canonical': normalized,
            'canonical_form': symptom,
            'medical_term': symptom,
            'patient_terms': [symptom],
            'cluster': 'symptomes_non_classifies',
            'secondary_clusters': []
        }
    
    def get_symptom_cluster_info(self, cluster_id: str) -> Dict:
        """Get information about a symptom cluster."""
        clusters = self.thesaurus.get('symptom_clusters', {})
        return clusters.get(cluster_id, {})


class DiseaseEnhancer:
    """Enhances disease entries with normalized and extended symptom information."""
    
    def __init__(self, normalizer: SymptomNormalizer):
        self.normalizer = normalizer
    
    def create_core_symptoms_description(self, disease: Dict, symptoms: List[str]) -> str:
        """Create focused clinical symptom description (for TF-IDF core signal)."""
        parts = []
        
        # Core symptoms with emphasis
        if symptoms:
            symptom_text = "Symptômes clés : " + ", ".join(symptoms).lower() + "."
            parts.append(symptom_text)
        
        # Add diagnostic tests (clinical signal)
        diagnostic_tests = disease.get('diagnosticTests', [])
        if diagnostic_tests:
            tests_text = "Diagnostic : " + ", ".join(diagnostic_tests[:3]).lower() + "."
            parts.append(tests_text)
        
        # Add key complications (discriminant)
        complications = disease.get('complications', [])
        if complications:
            key_comps = complications[:2]  # Only most important
            comp_text = "Complications : " + ", ".join(key_comps).lower() + "."
            parts.append(comp_text)
        
        return " ".join(parts)
    
    def create_context_description(self, disease: Dict) -> str:
        """Create narrative context description (for TF-IDF context)."""
        description = disease.get('description', '')
        
        # Build narrative context
        parts = []
        
        # Add disease context
        if description:
            parts.append(description)
        
        # Add severity context
        severity = disease.get('severity', '')
        if severity:
            severity_map = {
                'low': 'Cette affection est généralement bénigne.',
                'moderate': 'Cette affection nécessite une surveillance médicale.',
                'high': 'Cette affection est sérieuse et nécessite une prise en charge médicale.',
                'critical': 'Cette affection est grave et nécessite une intervention médicale urgente.'
            }
            if severity in severity_map:
                parts.append(severity_map[severity])
        
        # Add body parts context
        body_parts = disease.get('bodyParts', [])
        if body_parts:
            body_map = {
                'blood': 'le sang',
                'liver': 'le foie',
                'lungs': 'les poumons',
                'heart': 'le cœur',
                'brain': 'le cerveau',
                'kidneys': 'les reins',
                'stomach': 'l\'estomac',
                'intestines': 'les intestins',
                'skin': 'la peau',
                'bones': 'les os',
                'joints': 'les articulations',
                'muscles': 'les muscles'
            }
            affected = [body_map.get(bp, bp) for bp in body_parts[:3]]
            if affected:
                parts.append(f"Cette maladie affecte principalement {', '.join(affected)}.")
        
        # Add prevention (contextual, not clinical)
        prevention = disease.get('prevention', [])
        if prevention:
            prev_text = "Prévention : " + ", ".join(prevention[:3]).lower() + "."
            parts.append(prev_text)
        
        return " ".join(parts)
    
    def extract_key_discriminant_terms(self, disease: Dict, normalized_symptoms: List[str]) -> List[str]:
        """Extract clinically discriminant terms that are diagnostically significant."""
        discriminant_keywords = [
            'coma', 'ictere', 'convulsion', 'hemoptysie', 'hematemeese',
            'ascite', 'paralysie', 'cyanose', 'oedeme', 'hemorragie',
            'deshydratation', 'collapsus', 'choc', 'detresse', 'insuffisance',
            'delire', 'hallucination', 'syncope', 'vertige', 'paresthesie',
            'adenopathie', 'splenomegalie', 'hepatomegalie', 'masse', 'nodule'
        ]
        
        key_terms = []
        
        # Check normalized symptoms for discriminant terms
        for symptom in normalized_symptoms:
            for keyword in discriminant_keywords:
                if keyword in symptom.lower():
                    key_terms.append(symptom)
                    break
        
        # Add category as discriminant
        category = disease.get('category', '')
        if category:
            key_terms.append(category.lower())
        
        return list(set(key_terms))
    
    def enhance_disease(self, disease: Dict) -> Dict:
        """Enhance a disease entry with normalized and extended information."""
        enhanced = disease.copy()
        
        # Get original symptoms
        original_symptoms = disease.get('symptoms', [])
        
        # Process each symptom
        normalized_symptoms = []
        symptom_metadata = []
        patient_friendly_terms = []
        medical_terms = []
        symptom_clusters = set()
        
        # Multi-cluster mapping
        symptom_clusters_weighted = {}
        
        for symptom in original_symptoms:
            canonical_data = self.normalizer.find_canonical_form(symptom)
            
            normalized_symptoms.append(canonical_data['canonical'])
            patient_friendly_terms.extend(canonical_data['patient_terms'])
            medical_terms.append(canonical_data['medical_term'])
            
            # Support multi-cluster with weights
            primary_cluster = canonical_data['cluster']
            symptom_clusters.add(primary_cluster)
            
            # Increment cluster weight
            if primary_cluster not in symptom_clusters_weighted:
                symptom_clusters_weighted[primary_cluster] = 0
            symptom_clusters_weighted[primary_cluster] += 1
            
            # Check for secondary clusters (e.g., pain can be neurological AND musculoskeletal)
            secondary_clusters = canonical_data.get('secondary_clusters', [])
            for sec_cluster in secondary_clusters:
                symptom_clusters.add(sec_cluster)
                if sec_cluster not in symptom_clusters_weighted:
                    symptom_clusters_weighted[sec_cluster] = 0
                symptom_clusters_weighted[sec_cluster] += 0.5  # Secondary clusters get half weight
            
            symptom_metadata.append({
                'original': symptom,
                'canonical': canonical_data['canonical'],
                'canonical_form': canonical_data['canonical_form'],
                'medical_term': canonical_data['medical_term'],
                'cluster': canonical_data['cluster'],
                'secondary_clusters': secondary_clusters
            })
        
        # Add new fields
        enhanced['symptoms_normalized'] = list(set(normalized_symptoms))
        enhanced['symptoms_medical_terms'] = list(set(medical_terms))
        enhanced['symptoms_patient_terms'] = list(set(patient_friendly_terms))
        enhanced['symptom_clusters'] = list(symptom_clusters)
        enhanced['symptom_clusters_weighted'] = symptom_clusters_weighted  # NEW: weighted clusters
        enhanced['symptom_metadata'] = symptom_metadata
        
        # NEW: Separate core symptoms from context
        enhanced['tfidf_core_symptoms'] = self.create_core_symptoms_description(disease, original_symptoms)
        enhanced['tfidf_context'] = self.create_context_description(disease)
        
        # NEW: Extract key discriminant terms
        enhanced['key_discriminant_terms'] = self.extract_key_discriminant_terms(disease, enhanced['symptoms_normalized'])
        
        # Keep extended_description for backward compatibility
        enhanced['extended_description'] = enhanced['tfidf_core_symptoms'] + " " + enhanced['tfidf_context']
        
        # Add searchable text field with weighted components
        searchable_parts = [
            disease.get('name', ''),
            enhanced['tfidf_core_symptoms'],  # Core symptoms get priority
            enhanced['tfidf_context'],
            ' '.join(original_symptoms),
            ' '.join(enhanced['symptoms_patient_terms']),
            ' '.join(enhanced['symptoms_medical_terms']),
            ' '.join(enhanced['key_discriminant_terms']),  # NEW: discriminant terms
            disease.get('category', '')
        ]
        enhanced['searchable_text'] = ' '.join(filter(None, searchable_parts))
        
        # Add semantic search metadata
        enhanced['semantic_metadata'] = {
            'version': '2.0',  # Updated version
            'normalized_at': '2026-01-06',
            'symptom_count': len(original_symptoms),
            'unique_normalized_symptoms': len(enhanced['symptoms_normalized']),
            'symptom_clusters': list(symptom_clusters),
            'weighted_clusters': symptom_clusters_weighted,
            'key_discriminant_count': len(enhanced['key_discriminant_terms'])
        }
        
        return enhanced


def main():
    """Main function to enhance disease database."""
    print("🔧 Starting disease database enhancement...")
    
    # Paths
    base_path = Path(__file__).parent
    thesaurus_path = base_path / 'symptoms_thesaurus.json'
    ontology_path = base_path / 'medical_ontology.json'
    diseases_path = base_path / 'diseases_merged.json'
    output_path = base_path / 'diseases_enhanced.json'
    
    # Load components
    print("📚 Loading thesaurus and ontology...")
    normalizer = SymptomNormalizer(str(thesaurus_path), str(ontology_path))
    enhancer = DiseaseEnhancer(normalizer)
    
    # Load diseases
    print("📖 Loading disease database...")
    with open(diseases_path, 'r', encoding='utf-8') as f:
        diseases = json.load(f)
    
    print(f"✅ Loaded {len(diseases)} diseases")
    
    # Enhance each disease
    print("🚀 Enhancing diseases...")
    enhanced_diseases = []
    
    for i, disease in enumerate(diseases, 1):
        if i % 50 == 0:
            print(f"   Processing {i}/{len(diseases)}...")
        
        enhanced = enhancer.enhance_disease(disease)
        enhanced_diseases.append(enhanced)
    
    # Save enhanced database
    print(f"💾 Saving enhanced database to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_diseases, f, ensure_ascii=False, indent=2)
    
    # Generate statistics
    print("\n📊 Enhancement Statistics:")
    print(f"   Total diseases: {len(enhanced_diseases)}")
    
    total_symptoms = sum(len(d.get('symptoms', [])) for d in diseases)
    total_normalized = sum(len(d.get('symptoms_normalized', [])) for d in enhanced_diseases)
    print(f"   Total original symptoms: {total_symptoms}")
    print(f"   Total normalized symptoms: {total_normalized}")
    print(f"   Reduction: {total_symptoms - total_normalized} ({100 * (1 - total_normalized / total_symptoms):.1f}%)")
    
    # Count symptom clusters
    all_clusters = set()
    for d in enhanced_diseases:
        all_clusters.update(d.get('symptom_clusters', []))
    print(f"   Unique symptom clusters: {len(all_clusters)}")
    print(f"   Clusters: {', '.join(sorted(all_clusters))}")
    
    print("\n✨ Enhancement complete!")
    print(f"   Enhanced database saved to: {output_path}")
    print("\n📝 New fields added to each disease:")
    print("   - symptoms_normalized: Normalized symptom forms")
    print("   - symptoms_medical_terms: Medical terminology")
    print("   - symptoms_patient_terms: Patient-friendly terms")
    print("   - symptom_clusters: Semantic clusters")
    print("   - symptom_metadata: Detailed symptom mappings")
    print("   - extended_description: Rich contextual description")
    print("   - searchable_text: Combined text for TF-IDF")
    print("   - semantic_metadata: Enhancement metadata")


if __name__ == '__main__':
    main()
