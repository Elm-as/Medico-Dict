# Medico-Dict: Database Enhancements for TF-IDF and Semantic Search

## 🎯 Overview

This documentation describes the enhancements made to the Medico-Dict database to address structural limitations for TF-IDF-based symptom search and enable better semantic search capabilities.

## 🔍 Problems Addressed

### Original Issues

1. **Symptom Variations Not Unified**: Same concepts expressed in multiple forms (e.g., "Fièvre élevée", "Fièvre très élevée", "Fièvre vespérale")
2. **Short Symptom Phrases**: Insufficient context for meaningful TF-IDF scores
3. **Writing Variations**: Accent inconsistencies and spelling variations breaking similarity
4. **Fragmented Composite Symptoms**: Related symptoms split into disconnected fragments
5. **No Medical Hierarchy**: Lack of ontological structure or ICD-10/SNOMED mapping
6. **Missing Patient Synonyms**: No mapping between medical and colloquial terms
7. **Length Bias**: Diseases with more symptoms artificially over-weighted

## 📦 New Files Created

### 1. `symptoms_thesaurus.json`

A comprehensive symptom synonym and normalization mapping containing:

- **Symptom Synonyms**: 18 major symptom groups with:
  - Canonical forms (standardized term)
  - Normalized terms (accent-free, lowercase)
  - Medical terminology
  - Patient-friendly terms
  - All variations found in the database
  - Semantic cluster assignments
  - ICD-10 code references

- **Symptom Clusters**: 10 semantic clusters:
  - `symptomes_generaux` - General symptoms (fever, fatigue, weight changes)
  - `symptomes_neurologiques` - Neurological (headaches, convulsions, vertigo)
  - `symptomes_respiratoires` - Respiratory (cough, dyspnea, expectoration)
  - `symptomes_digestifs` - Digestive (nausea, vomiting, diarrhea)
  - `symptomes_cutanes` - Skin (rash, pruritus, jaundice)
  - `symptomes_douleur` - Pain-related (various types of pain)
  - `symptomes_lymphatiques` - Lymphatic (adenopathy)
  - `symptomes_cardiovasculaires` - Cardiovascular
  - `symptomes_urinaires` - Urinary
  - `symptomes_psychiatriques` - Psychiatric

- **Normalization Rules**: Text processing rules for standardization

### 2. `medical_ontology.json`

A hierarchical medical ontology providing:

- **Symptom Hierarchy**: Tree structure from root to specific symptoms
  - Parent-child relationships
  - ICD-10 chapter mappings
  - SNOMED CT concept codes
  - Severity and temporal modifiers
  - Location modifiers

- **Disease Categories**: 10 major disease categories with:
  - ICD-10 chapter ranges
  - Common symptom cluster associations

- **Severity Scale**: Standardized severity levels with numeric values

### 3. `diseases_enhanced.json`

Enhanced version of `diseases_merged.json` with additional fields for each disease:

#### New Fields

1. **`symptoms_normalized`** (Array of strings)
   - Normalized, canonical form of each symptom
   - Reduces variations to common terms
   - Example: `["fievre", "cephalee", "fatigue", "douleur", "nausee"]`

2. **`symptoms_medical_terms`** (Array of strings)
   - Medical terminology for each symptom
   - Example: `["pyrexie", "céphalée", "asthénie", "algie", "nausée"]`

3. **`symptoms_patient_terms`** (Array of strings)
   - Patient-friendly, colloquial terms
   - Enables matching user queries in everyday language
   - Example: `["fièvre", "température", "chaud", "mal de tête", "maux de tête", "fatigué", "épuisement"]`

4. **`symptom_clusters`** (Array of strings)
   - Semantic clusters this disease's symptoms belong to
   - Example: `["symptomes_generaux", "symptomes_neurologiques", "symptomes_douleur", "symptomes_digestifs"]`

5. **`symptom_metadata`** (Array of objects)
   - Detailed mapping for each original symptom
   - Each object contains:
     - `original`: Original symptom text
     - `canonical`: Normalized canonical form
     - `canonical_form`: Human-readable canonical
     - `medical_term`: Medical terminology
     - `cluster`: Semantic cluster assignment

6. **`extended_description`** (String)
   - Rich, contextual description combining:
     - Original description
     - Symptom narrative
     - Severity context
     - Complications
     - Affected body parts
   - Provides richer text for TF-IDF analysis

7. **`searchable_text`** (String)
   - Combined text field optimized for TF-IDF search
   - Includes: name, descriptions, all symptom variations, category
   - Single field for efficient full-text indexing

8. **`semantic_metadata`** (Object)
   - Enhancement version and date
   - Symptom counts (original vs. normalized)
   - Cluster assignments

### 4. `enhance_database.py`

Python script that performs the database enhancement:

- Loads thesaurus and ontology
- Processes each disease entry
- Normalizes symptoms
- Generates extended descriptions
- Creates patient-friendly mappings
- Outputs enhanced database

## 🚀 Usage

### Running the Enhancement

```bash
python3 enhance_database.py
```

This will:
1. Load `symptoms_thesaurus.json` and `medical_ontology.json`
2. Process all diseases from `diseases_merged.json`
3. Generate `diseases_enhanced.json` with all enhancements
4. Display statistics about the enhancement

### Using the Enhanced Database

#### For TF-IDF Search

Use the `searchable_text` field for TF-IDF vectorization:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
import json

# Load enhanced database
with open('diseases_enhanced.json', 'r', encoding='utf-8') as f:
    diseases = json.load(f)

# Extract searchable text
corpus = [d['searchable_text'] for d in diseases]

# Create TF-IDF matrix
vectorizer = TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 3),  # Use unigrams, bigrams, and trigrams
    min_df=2
)
tfidf_matrix = vectorizer.fit_transform(corpus)
```

#### For Semantic Search

Use normalized symptoms and clusters:

```python
# Query with patient terms
query_symptoms = ["mal de tête", "fièvre", "nausée"]

# Load thesaurus for normalization
with open('symptoms_thesaurus.json', 'r', encoding='utf-8') as f:
    thesaurus = json.load(f)

# Normalize query (implementation in enhance_database.py)
# Match against symptoms_normalized or symptoms_patient_terms

# Filter by symptom clusters for hierarchical search
target_clusters = ["symptomes_generaux", "symptomes_neurologiques"]
matching_diseases = [
    d for d in diseases 
    if any(c in d['symptom_clusters'] for c in target_clusters)
]
```

#### For Medical Professional Search

Use medical terminology:

```python
# Search with medical terms
query = "pyrexie céphalée"
# Match against symptoms_medical_terms field
```

## 📊 Enhancement Statistics

From the initial enhancement run:

- **Total diseases**: 431
- **Original symptoms**: 2,146
- **Normalized symptoms**: 2,122
- **Symptom reduction**: 24 symptoms (1.1%)
- **Unique symptom clusters**: 8
- **Average symptoms per disease**: ~5

## 🔧 Customization

### Adding New Symptoms to Thesaurus

Edit `symptoms_thesaurus.json`:

```json
{
  "symptom_synonyms": {
    "new_symptom": {
      "canonical_form": "New Symptom",
      "normalized_term": "new_symptom",
      "medical_term": "Medical Term",
      "patient_terms": ["patient term 1", "patient term 2"],
      "variations": [
        "Variation 1",
        "Variation 2"
      ],
      "semantic_cluster": "symptomes_generaux",
      "icd10_related": ["R99"]
    }
  }
}
```

### Extending the Ontology

Edit `medical_ontology.json` to add new hierarchy nodes or update existing ones.

### Re-running Enhancement

After modifying thesaurus or ontology:

```bash
python3 enhance_database.py
```

This will regenerate `diseases_enhanced.json` with updated mappings.

## 🎓 Best Practices

### For TF-IDF Implementation

1. **Use `searchable_text` field**: Contains rich, contextual information
2. **Use n-grams**: Set `ngram_range=(1, 3)` to capture multi-word symptoms
3. **Adjust min_df**: Filter rare terms that may be noise
4. **Consider symptom clusters**: Pre-filter by cluster before TF-IDF for better precision

### For Semantic Search

1. **Normalize user input**: Use the normalization rules from thesaurus
2. **Support patient terms**: Match against `symptoms_patient_terms` for user-friendly search
3. **Use hierarchical filtering**: Start with symptom clusters, then drill down
4. **Combine approaches**: Use semantic filtering + TF-IDF ranking

### For Production Systems

1. **Index the enhanced database**: Use Elasticsearch or similar for efficient search
2. **Cache TF-IDF vectors**: Pre-compute and store for fast lookups
3. **Implement query expansion**: Use synonyms from thesaurus for better recall
4. **Add spell correction**: Handle typos in user queries
5. **Track query performance**: Monitor which searches work well vs. poorly

## 🔬 Technical Details

### Normalization Process

1. **Lowercase conversion**: All text converted to lowercase
2. **Accent removal**: Using mapping in `normalization_rules`
3. **Whitespace trimming**: Remove leading/trailing spaces
4. **Variation matching**: Both exact and partial matching supported

### Symptom Cluster Assignment

Each symptom is assigned to one primary cluster based on:
- Medical classification
- ICD-10 chapter
- Clinical usage
- Semantic similarity

### Extended Description Generation

Combines:
1. Original description
2. Symptom list with natural language
3. Severity context
4. Complications
5. Affected body systems

## 🆘 Troubleshooting

### Symptom Not Normalized

If a symptom isn't being normalized:
1. Check if it exists in thesaurus variations
2. Add it to appropriate symptom group
3. Re-run enhancement script

### Cluster Assignment Issues

If symptoms are in wrong clusters:
1. Review cluster definition in thesaurus
2. Update `semantic_cluster` field
3. Re-run enhancement

### Performance Issues

For large datasets:
1. Process diseases in batches
2. Use multiprocessing for parallel processing
3. Cache normalized symptom mappings

## 📈 Future Enhancements

Potential improvements:

1. **SNOMED CT Integration**: Full SNOMED concept mappings
2. **ICD-11 Support**: Add ICD-11 codes alongside ICD-10
3. **Multi-language Support**: French, English, local languages
4. **Weighted Symptoms**: Assign importance weights to symptoms
5. **Temporal Patterns**: Capture symptom progression over time
6. **Age/Gender Specificity**: Symptom presentation variations
7. **Geographic Relevance**: Regional disease prevalence
8. **Machine Learning Embeddings**: Pre-computed semantic vectors

## 📝 Version History

- **Version 1.0** (2026-01-06)
  - Initial implementation
  - 18 major symptom groups
  - 10 semantic clusters
  - Medical ontology with ICD-10 mapping
  - Enhanced database with 8 new fields

## 📄 License

Same as parent Medico-Dict project.

## 🤝 Contributing

To contribute:
1. Update thesaurus with new symptom mappings
2. Extend ontology with additional hierarchies
3. Improve normalization algorithms
4. Add more patient-friendly terms
5. Validate medical accuracy with domain experts
