#!/usr/bin/env python3
"""
Usage examples for the enhanced Medico-Dict database.

This file demonstrates how to use the enhanced database for:
1. TF-IDF-based search
2. Semantic search with symptom clusters
3. Patient-friendly term matching
4. Medical terminology search
"""

import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MedicoSearchEngine:
    """Search engine for the enhanced medical database."""
    
    def __init__(self, enhanced_db_path='diseases_enhanced.json',
                 thesaurus_path='symptoms_thesaurus.json'):
        """Initialize the search engine."""
        print("🔧 Loading databases...")
        
        # Load enhanced database
        with open(enhanced_db_path, 'r', encoding='utf-8') as f:
            self.diseases = json.load(f)
        
        # Load thesaurus
        with open(thesaurus_path, 'r', encoding='utf-8') as f:
            self.thesaurus = json.load(f)
        
        print(f"✅ Loaded {len(self.diseases)} diseases")
        
        # Build TF-IDF vectorizer
        print("🔍 Building TF-IDF index...")
        self.build_tfidf_index()
        
        # Build symptom normalization maps
        self.build_normalization_maps()
        
        print("✨ Search engine ready!")
    
    def build_tfidf_index(self):
        """Build TF-IDF index from searchable text."""
        corpus = [d['searchable_text'] for d in self.diseases]
        
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
            min_df=2,  # Ignore very rare terms
            max_df=0.8  # Ignore very common terms
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        print(f"   TF-IDF matrix shape: {self.tfidf_matrix.shape}")
    
    def build_normalization_maps(self):
        """Build maps for symptom normalization."""
        self.variation_to_canonical = {}
        
        for canonical, data in self.thesaurus['symptom_synonyms'].items():
            # Map all variations to canonical
            for variation in data['variations']:
                normalized = self.normalize_text(variation)
                self.variation_to_canonical[normalized] = canonical
            
            # Map patient terms too
            for term in data['patient_terms']:
                normalized = self.normalize_text(term)
                self.variation_to_canonical[normalized] = canonical
    
    def normalize_text(self, text):
        """Normalize text for matching."""
        if not text:
            return ""
        
        text = text.lower()
        
        # Remove accents
        accent_map = self.thesaurus['normalization_rules']['accents_removal']
        for accented, plain in accent_map.items():
            text = text.replace(accented, plain)
        
        return text.strip()
    
    def tfidf_search(self, query, top_k=10):
        """
        Search using TF-IDF similarity.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of (disease, score) tuples
        """
        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include non-zero scores
                results.append((self.diseases[idx], similarities[idx]))
        
        return results
    
    def semantic_search(self, symptoms, top_k=10):
        """
        Search using semantic symptom matching.
        
        Args:
            symptoms: List of symptom strings (can be patient terms)
            top_k: Number of results to return
            
        Returns:
            List of (disease, score) tuples
        """
        # Normalize input symptoms
        normalized_symptoms = []
        for symptom in symptoms:
            normalized = self.normalize_text(symptom)
            if normalized in self.variation_to_canonical:
                normalized_symptoms.append(self.variation_to_canonical[normalized])
            else:
                normalized_symptoms.append(normalized)
        
        # Calculate match scores
        results = []
        for disease in self.diseases:
            disease_symptoms = set(disease['symptoms_normalized'])
            
            # Calculate Jaccard similarity
            intersection = len(set(normalized_symptoms) & disease_symptoms)
            union = len(set(normalized_symptoms) | disease_symptoms)
            
            if union > 0:
                score = intersection / union
                
                # Boost score if patient terms match
                patient_terms_lower = [t.lower() for t in disease['symptoms_patient_terms']]
                for symptom in symptoms:
                    if symptom.lower() in patient_terms_lower:
                        score *= 1.2  # 20% boost
                
                if score > 0:
                    results.append((disease, score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def cluster_filter_search(self, query, clusters, top_k=10):
        """
        Search within specific symptom clusters.
        
        Args:
            query: Search query string
            clusters: List of cluster names to filter by
            top_k: Number of results to return
            
        Returns:
            List of (disease, score) tuples
        """
        # Filter diseases by clusters
        filtered_indices = []
        filtered_diseases = []
        
        for idx, disease in enumerate(self.diseases):
            disease_clusters = disease.get('symptom_clusters', [])
            if any(c in disease_clusters for c in clusters):
                filtered_indices.append(idx)
                filtered_diseases.append(disease)
        
        if not filtered_indices:
            return []
        
        # Build filtered matrix
        filtered_matrix = self.tfidf_matrix[filtered_indices]
        
        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vec, filtered_matrix)[0]
        
        # Get top k
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append((filtered_diseases[idx], similarities[idx]))
        
        return results
    
    def hybrid_search(self, query, symptoms=None, clusters=None, top_k=10):
        """
        Hybrid search combining TF-IDF, semantic, and cluster filtering.
        
        Args:
            query: Text query
            symptoms: Optional list of symptom strings
            clusters: Optional list of cluster names
            top_k: Number of results
            
        Returns:
            List of (disease, combined_score) tuples
        """
        # Get TF-IDF results
        if clusters:
            tfidf_results = self.cluster_filter_search(query, clusters, top_k * 2)
        else:
            tfidf_results = self.tfidf_search(query, top_k * 2)
        
        # If symptoms provided, get semantic results
        semantic_results = []
        if symptoms:
            semantic_results = self.semantic_search(symptoms, top_k * 2)
        
        # Combine scores
        disease_scores = {}
        
        # Add TF-IDF scores (weight: 0.6)
        for disease, score in tfidf_results:
            disease_id = disease['id']
            disease_scores[disease_id] = {
                'disease': disease,
                'tfidf_score': score * 0.6,
                'semantic_score': 0
            }
        
        # Add semantic scores (weight: 0.4)
        for disease, score in semantic_results:
            disease_id = disease['id']
            if disease_id in disease_scores:
                disease_scores[disease_id]['semantic_score'] = score * 0.4
            else:
                disease_scores[disease_id] = {
                    'disease': disease,
                    'tfidf_score': 0,
                    'semantic_score': score * 0.4
                }
        
        # Calculate combined scores
        results = []
        for disease_id, data in disease_scores.items():
            combined_score = data['tfidf_score'] + data['semantic_score']
            results.append((data['disease'], combined_score))
        
        # Sort by combined score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]


def main():
    """Run example searches."""
    print("=" * 80)
    print("Medico-Dict Enhanced Search Examples")
    print("=" * 80)
    print()
    
    # Initialize search engine
    engine = MedicoSearchEngine()
    print()
    
    # Example 1: TF-IDF search with medical query
    print("=" * 80)
    print("Example 1: TF-IDF Search with Medical Query")
    print("=" * 80)
    query = "fièvre élevée céphalées douleurs musculaires fatigue"
    print(f"Query: '{query}'")
    print()
    
    results = engine.tfidf_search(query, top_k=5)
    print(f"Top {len(results)} results:")
    for i, (disease, score) in enumerate(results, 1):
        print(f"{i}. {disease['name']} (Score: {score:.4f})")
        print(f"   Symptoms: {', '.join(disease['symptoms'][:5])}")
        print()
    
    # Example 2: Semantic search with patient-friendly terms
    print("=" * 80)
    print("Example 2: Semantic Search with Patient-Friendly Terms")
    print("=" * 80)
    symptoms = ["mal de tête", "température", "nausée", "fatigué"]
    print(f"Symptoms: {symptoms}")
    print()
    
    results = engine.semantic_search(symptoms, top_k=5)
    print(f"Top {len(results)} results:")
    for i, (disease, score) in enumerate(results, 1):
        print(f"{i}. {disease['name']} (Score: {score:.4f})")
        print(f"   Normalized symptoms: {', '.join(disease['symptoms_normalized'][:5])}")
        print(f"   Clusters: {', '.join(disease['symptom_clusters'])}")
        print()
    
    # Example 3: Cluster-filtered search
    print("=" * 80)
    print("Example 3: Cluster-Filtered Search")
    print("=" * 80)
    query = "douleur ventre diarrhée"
    clusters = ["symptomes_digestifs"]
    print(f"Query: '{query}'")
    print(f"Clusters: {clusters}")
    print()
    
    results = engine.cluster_filter_search(query, clusters, top_k=5)
    print(f"Top {len(results)} results:")
    for i, (disease, score) in enumerate(results, 1):
        print(f"{i}. {disease['name']} (Score: {score:.4f})")
        print(f"   Category: {disease.get('category', 'N/A')}")
        print()
    
    # Example 4: Hybrid search
    print("=" * 80)
    print("Example 4: Hybrid Search (TF-IDF + Semantic)")
    print("=" * 80)
    query = "infection fièvre toux difficulté respirer"
    symptoms = ["fièvre", "toux", "essoufflement"]
    clusters = ["symptomes_respiratoires", "symptomes_generaux"]
    print(f"Query: '{query}'")
    print(f"Symptoms: {symptoms}")
    print(f"Clusters: {clusters}")
    print()
    
    results = engine.hybrid_search(query, symptoms=symptoms, clusters=clusters, top_k=5)
    print(f"Top {len(results)} results:")
    for i, (disease, score) in enumerate(results, 1):
        print(f"{i}. {disease['name']} (Combined Score: {score:.4f})")
        print(f"   ICD-10: {disease.get('icd10', 'N/A')}")
        print(f"   Severity: {disease.get('severity', 'N/A')}")
        print()
    
    # Example 5: Finding diseases by specific symptom
    print("=" * 80)
    print("Example 5: Search by Specific Symptom")
    print("=" * 80)
    symptom = "ictère"
    print(f"Searching for diseases with symptom: '{symptom}'")
    print()
    
    # Find diseases with this symptom (normalized)
    normalized = engine.normalize_text(symptom)
    matching = []
    for disease in engine.diseases:
        if normalized in disease['symptoms_normalized']:
            matching.append(disease)
    
    print(f"Found {len(matching)} diseases with '{symptom}':")
    for i, disease in enumerate(matching[:10], 1):
        print(f"{i}. {disease['name']}")
        print(f"   Category: {disease.get('category', 'N/A')}")
        print(f"   All symptoms: {', '.join(disease['symptoms'][:5])}")
        if len(disease['symptoms']) > 5:
            print(f"   ... and {len(disease['symptoms']) - 5} more")
        print()
    
    print("=" * 80)
    print("Examples complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
