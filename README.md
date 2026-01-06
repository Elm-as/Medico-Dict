# Medico-Dict Enhanced

A comprehensive medical symptom and disease database optimized for TF-IDF and semantic search, with support for both medical professionals and patients.

## 🎯 Overview

This project provides a structured medical knowledge base with 431 diseases, enhanced with:
- **Symptom normalization** and synonym mapping
- **Medical ontology** with hierarchical clustering
- **Patient-friendly** terminology
- **TF-IDF optimization** with rich contextual descriptions
- **Semantic search** capabilities

## 📁 Project Structure

### Core Database Files

- **`diseases_merged.json`** - Original disease database (431 diseases)
- **`diseases_enhanced.json`** - Enhanced database with normalized symptoms and extended fields
- **`symptoms_vocabulary.json`** - Original symptom vocabulary (1,417 symptoms)
- **`symptoms_vocabulary_enhanced.json`** - Enhanced vocabulary with mappings

### Enhancement System

- **`symptoms_thesaurus.json`** - Comprehensive symptom synonym and normalization mappings
  - 18 major symptom groups
  - Medical and patient-friendly terms
  - ICD-10 code mappings
  - 10 semantic clusters

- **`medical_ontology.json`** - Hierarchical medical ontology
  - Symptom hierarchy tree
  - Disease categories
  - ICD-10 and SNOMED CT mappings
  - Severity scales

### Scripts and Tools

- **`enhance_database.py`** - Database enhancement script
  - Normalizes symptoms
  - Adds extended descriptions
  - Generates semantic metadata
  
- **`usage_examples.py`** - Practical usage examples
  - TF-IDF search
  - Semantic search
  - Cluster-based filtering
  - Hybrid search

### Documentation

- **`ENHANCEMENTS_DOCUMENTATION.md`** - Detailed technical documentation
- **`README.md`** - This file

## 🚀 Quick Start

### 1. Enhance the Database

```bash
python3 enhance_database.py
```

This generates `diseases_enhanced.json` with all enhancements.

### 2. Run Examples

```bash
# Install dependencies
pip install scikit-learn numpy

# Run usage examples
python3 usage_examples.py
```

### 3. Use in Your Application

```python
from usage_examples import MedicoSearchEngine

# Initialize search engine
engine = MedicoSearchEngine(
    enhanced_db_path='diseases_enhanced.json',
    thesaurus_path='symptoms_thesaurus.json'
)

# TF-IDF search
results = engine.tfidf_search("fièvre toux", top_k=10)

# Semantic search with patient terms
results = engine.semantic_search(["mal de tête", "nausée"], top_k=10)

# Hybrid search
results = engine.hybrid_search(
    query="infection respiratoire",
    symptoms=["fièvre", "toux"],
    clusters=["symptomes_respiratoires"],
    top_k=10
)
```

## 📊 Key Features

### 1. Symptom Normalization

**Problem**: Multiple variations of the same symptom
- "Fièvre élevée", "Fièvre très élevée", "Fièvre vespérale"

**Solution**: Normalized to canonical forms
- All map to: `fievre` (canonical)

### 2. Patient-Friendly Terms

**Problem**: Medical terminology not understood by patients

**Solution**: Patient term mappings
- Medical: "céphalée" → Patient: "mal de tête", "maux de tête"
- Medical: "ictère" → Patient: "jaunisse", "peau jaune"

### 3. Semantic Clustering

**Problem**: No hierarchical organization

**Solution**: 10 symptom clusters
- `symptomes_generaux` - General symptoms
- `symptomes_neurologiques` - Neurological
- `symptomes_respiratoires` - Respiratory
- `symptomes_digestifs` - Digestive
- `symptomes_cutanes` - Skin-related
- And 5 more...

### 4. Extended Descriptions

**Problem**: Short symptom phrases lack context for TF-IDF

**Solution**: Rich contextual descriptions
```
"Infection parasitaire transmise par les moustiques, caractérisée par 
des accès de fièvre cycliques. Les symptômes incluent : fièvre élevée, 
frissons, céphalées, douleurs musculaires, fatigue, nausées. Cette 
affection est sérieuse et nécessite une prise en charge médicale..."
```

### 5. ICD-10 & SNOMED Mappings

**Problem**: No standardized medical coding

**Solution**: 
- All diseases have ICD-10 codes
- Symptoms mapped to ICD-10 ranges
- SNOMED CT concepts in ontology

## 🔍 Search Capabilities

### TF-IDF Search
Best for: Text-based queries with context

```python
results = engine.tfidf_search("infection fièvre toux difficultés respiratoires")
```

### Semantic Search
Best for: Symptom-based diagnosis

```python
results = engine.semantic_search(["fièvre", "toux sèche", "fatigue"])
```

### Cluster-Filtered Search
Best for: Domain-specific searches

```python
results = engine.cluster_filter_search(
    "douleur abdominale diarrhée",
    clusters=["symptomes_digestifs"]
)
```

### Hybrid Search
Best for: Combining multiple approaches

```python
results = engine.hybrid_search(
    query="infection respiratoire sévère",
    symptoms=["fièvre", "toux", "essoufflement"],
    clusters=["symptomes_respiratoires", "symptomes_generaux"]
)
```

## 📈 Statistics

- **Diseases**: 431
- **Original Symptoms**: 1,417 unique terms
- **Normalized Symptoms**: ~1,400 (after deduplication)
- **Symptom Groups**: 18 major groups
- **Semantic Clusters**: 10
- **ICD-10 Coverage**: 100%

## 🛠️ Customization

### Add New Symptoms

Edit `symptoms_thesaurus.json`:

```json
{
  "symptom_synonyms": {
    "new_symptom": {
      "canonical_form": "New Symptom",
      "normalized_term": "new_symptom",
      "medical_term": "Medical Term",
      "patient_terms": ["patient term"],
      "variations": ["Variation 1", "Variation 2"],
      "semantic_cluster": "symptomes_generaux",
      "icd10_related": ["R99"]
    }
  }
}
```

Then re-run:
```bash
python3 enhance_database.py
```

### Extend Ontology

Edit `medical_ontology.json` to add new hierarchy nodes or update existing ones.

### Adjust Search Weights

In `usage_examples.py`, modify the `hybrid_search` method:

```python
# Current: TF-IDF=0.6, Semantic=0.4
disease_scores[disease_id]['tfidf_score'] = score * 0.6
disease_scores[disease_id]['semantic_score'] = score * 0.4
```

## 📚 Documentation

For detailed technical documentation, see:
- **[ENHANCEMENTS_DOCUMENTATION.md](ENHANCEMENTS_DOCUMENTATION.md)** - Complete technical guide

## 🔬 Use Cases

### For Medical Professionals
- Differential diagnosis support
- Medical terminology search
- ICD-10 code lookup
- Clinical decision support

### For Patients
- Symptom checker with patient-friendly terms
- Understanding medical conditions
- Finding relevant diseases by symptoms

### For Developers
- Building medical search applications
- Integrating symptom databases
- Creating chatbots for health queries
- Developing diagnostic tools

### For Researchers
- Medical NLP research
- Semantic similarity studies
- Healthcare data analysis
- Clinical terminology mapping

## ⚠️ Disclaimer

This database is for **educational and informational purposes only**. It should **not be used as a substitute for professional medical advice, diagnosis, or treatment**. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## 📝 Data Sources

Based on:
- WHO (World Health Organization) guidelines
- PNLP Côte d'Ivoire
- ICD-10 classification
- Medical literature

## 🤝 Contributing

Contributions are welcome! Please:

1. Add new symptom mappings to the thesaurus
2. Extend the medical ontology
3. Improve search algorithms
4. Add more patient-friendly terms
5. Validate medical accuracy

## 📄 License

Please refer to the repository license.

## 🔗 Related Files

- Original diseases: `disease*.json` files (individual disease batches)
- Disease names: `diseases_names.json`
- Normalized diseases: `diseases_normalized.json`

## 📧 Contact

For questions or suggestions, please open an issue in the repository.

---

**Last Updated**: 2026-01-06  
**Version**: 1.0  
**Enhancement Status**: ✅ Complete
