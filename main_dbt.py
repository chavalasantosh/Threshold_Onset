# Databricks notebook source
# /// script
# [tool.databricks.environment]
# base_environment = "databricks_ai_v4"
# environment_version = "4"
# dependencies = [
#   "santok",
#   "threshold-onset",
# ]
# ///
!git clone https://github.com/chavalasantosh/Threshold_Onset.git

# COMMAND ----------

!git clone https://github.com/chavalasantosh/WLAC.git

# COMMAND ----------

import os
from pathlib import Path

# Configuration
repo_root = '/Workspace/Threshold_Onset'
export_dir = '/Workspace/full_colab_export'
data_dir = os.path.join(repo_root, 'data')

# 1. Ensure the data directory exists and link the export files into it
dbutils.fs.mkdirs(data_dir)
try:
    dbutils.fs.info(export_dir)
    export_dir_exists = True
except:
    export_dir_exists = False
if export_dir_exists:
    for file_info in dbutils.fs.ls(export_dir):
        dbutils.fs.cp(file_info.path, f"{data_dir}/", recurse=True)
else:
    print(f"Export directory {export_dir} does not exist. Skipping file copy.")

# 2. Set environment variables for advanced 10x performance optimization
os.environ['SANTEK_TRAIN_FAST'] = '3'
os.environ['PHASE1_SKIP_DISTANCES'] = '0'
os.environ['PHASE3_SKIP_PATH_LENGTHS'] = '0'
os.environ['SANTEK_TEXT_WORKERS'] = '8'
os.environ['SANTEK_METHOD_WORKERS'] = '8'
os.environ['THRESHOLD_ONSET_NUM_RUNS'] = '3'
os.environ['PYTHONUNBUFFERED'] = '1'

# 3. Run the advanced training pipeline only if export_dir exists
try:
    dbutils.fs.info(export_dir)
    export_dir_exists = True
except:
    export_dir_exists = False
if export_dir_exists:
    print(f"Executing advanced training from {repo_root}...")
    dbutils.notebook.run(f"{repo_root}/build_hindu_corpus", 0, {"epochs": "18", "max-texts": "2132"})
else:
    print("Advanced training skipped due to missing export directory. Please ensure /Workspace/full_colab_export exists and contains the required files.")

# COMMAND ----------

import os
import pandas as pd

repo_root = '/content/Threshold_Onset'
export_path = '/content/full_colab_export/slm_training_base.csv'
model_path = os.path.join(repo_root, 'output/mini_least_model.json')

if os.path.exists(export_path):
    # Load tiny corpus
    df = pd.read_csv(export_path)
    # Select a tiny portion of text for the 'Extra Least' approach
    mini_corpus = ' '.join(df.iloc[:20, 0].astype(str).tolist())

    print(f'--- Developing Extra Least LM ---')
    print(f'Training on {len(mini_corpus)} chars from export data.')

    # Execute training from repo root
    %cd {repo_root}
    os.makedirs('output', exist_ok=True)
    os.environ['SANTEK_TRAIN_FAST'] = '1'

    !python santek_base_model.py train --epochs 5 --corpus "{mini_corpus}" --model "{model_path}"

    print(f'\n[OK] Mini Model created at: {model_path}')

    print('\n--- Testing Generation ---')
    !python santek_base_model.py generate "Action" --model "{model_path}" --length 10
else:
    print(f'Data source not found at {export_path}. Please ensure the unzip cell finished successfully.')

# COMMAND ----------

# Test the 'Extra Least' model generation using the correct path
import os
repo_root = '/content/Threshold_Onset'
%cd {repo_root}

model_path = 'output/mini_least_model.json'
if os.path.exists(model_path):
    !python santek_base_model.py generate "Action" --model "{model_path}" --length 10
else:
    print('Model file not found. Please run the training cell above.')

# COMMAND ----------

import os

# Path settings
repo_root = '/content/Threshold_Onset'
model_path = os.path.join(repo_root, 'output/mini_least_model.json')

print("--- Building Semantic Corpus from Project Documentation ---")
corpus_parts = []

# Search the repo for descriptive text files
for root, dirs, files in os.walk(repo_root):
    for file in files:
        if file.endswith(('.md', '.txt')) and '.git' not in root:
            try:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 100:
                        corpus_parts.append(content)
            except:
                continue

final_corpus = "\n\n".join(corpus_parts)
print(f"Final documentation corpus size: {len(final_corpus)} characters.")

if len(final_corpus) > 500:
    %cd {repo_root}
    os.makedirs('output', exist_ok=True)
    os.environ['SANTEK_TRAIN_FAST'] = '1'
    # Clean text for shell safety and truncate for a 'mini' footprint
    clean_corpus = final_corpus[:5000].replace('"', '').replace("'", "")

    print("\n--- Training Extra Least Model on Project Docs ---")
    !python santek_base_model.py train --epochs 5 --corpus "{clean_corpus}" --model "{model_path}"

    print(f"\n[OK] Extra Least Model created at: {model_path}")
    print("\n--- Testing Generation ---")
    !python santek_base_model.py generate "Model" --model "{model_path}" --length 15
else:
    print("[!] Not enough project text found to train.")

# COMMAND ----------

import os
import json
import random

repo_root = '/content/Threshold_Onset'
model_path = os.path.join(repo_root, 'output/mini_least_model.json')
os.makedirs(os.path.dirname(model_path), exist_ok=True)

# The 'Extra Least' Philosophy: Action before Knowledge
# Implementation of a Structural Learning Engine
class ExtraLeastLM:
    def __init__(self):
        self.lookup = {}

    def train(self, text):
        words = text.split()
        for i in range(len(words)-1):
            curr, next_w = words[i], words[i+1]
            if curr not in self.lookup: self.lookup[curr] = []
            if next_w not in self.lookup[curr]:
                self.lookup[curr].append(next_w)

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.lookup, f, indent=2)

    def generate(self, prompt, length=10):
        curr = prompt.split()[-1]
        res = [prompt]
        for _ in range(length):
            options = self.lookup.get(curr, [])
            if not options: break
            curr = random.choice(options)
            res.append(curr)
        return ' '.join(res)

# 1. Build the model on a minimal corpus
print('--- Developing Standalone Extra Least LM ---')
corpus = "Action before Knowledge. Karya happens before Jnana. Structural Learning Engine is active. Phase Zero is frozen. The model is mini. The model is least."

model = ExtraLeastLM()
model.train(corpus)
model.save(model_path)

if os.path.exists(model_path):
    print(f'[OK] Extra Least Model created at: {model_path}')

    # 2. Display the Structural Map (The requested JSON format)
    with open(model_path, 'r') as f:
        print('\n--- Model Structural Map (Knowledge) ---')
        print(f.read())

    # 3. Test Generation
    print('\n--- Testing Generation ---')
    output = model.generate("Action", length=12)
    print(f'Prompt: Action')
    print(f'Output: {output}')
else:
    print('[!] Failed to save model.')

# COMMAND ----------

# MAGIC %md
# MAGIC ## WLAC + Threshold_Onset Combined Model Pipeline
# MAGIC
# MAGIC This section generates multilingual linguistic data from the **WLAC** (World Language Alphabet Collection) concept, combines it with the existing **Threshold_Onset** JSONL corpus, and trains the **SanTEK Base Model** on the unified dataset.
# MAGIC
# MAGIC **Steps:**
# MAGIC 1. Generate WLAC linguistic corpus (languages, scripts, writing systems)
# MAGIC 2. Combine with Threshold_Onset clean JSONL corpus
# MAGIC 3. Train SanTEK Base Model on the combined data
# MAGIC 4. Validate and test generation

# COMMAND ----------

# DBTITLE 1,Step 1: Generate WLAC Linguistic Data
import json
import os
import unicodedata

# ─── Paths (Databricks workspace) ─────────────────────────────
USER_HOME = '/Workspace/Users/labuser14433625_1774766555@vocareum.com/Work'
WLAC_ROOT = os.path.join(USER_HOME, 'WLAC')
THRESHOLD_ROOT = os.path.join(USER_HOME, 'Threshold_Onset')
DATA_DIR = os.path.join(THRESHOLD_ROOT, 'data')
WLAC_OUTPUT = os.path.join(DATA_DIR, 'wlac_generated.jsonl')

print('=== Step 1: Generating WLAC Linguistic Corpus ===')
print(f'Output: {WLAC_OUTPUT}\n')

# ─── WLAC World Language Data (structured linguistic descriptions) ──
# Core writing systems and their representative languages
WRITING_SYSTEMS = {
    'Latin': {
        'languages': ['English', 'Spanish', 'French', 'German', 'Portuguese', 'Italian',
                      'Dutch', 'Polish', 'Romanian', 'Czech', 'Swedish', 'Vietnamese',
                      'Turkish', 'Indonesian', 'Malay', 'Swahili', 'Tagalog', 'Hausa'],
        'char_range': (0x0041, 0x007A),
        'description': 'The Latin script is the most widely used alphabetic writing system in the world, '
                       'originating from the ancient Roman alphabet and now used by thousands of languages across every continent.'
    },
    'Devanagari': {
        'languages': ['Hindi', 'Sanskrit', 'Marathi', 'Nepali', 'Konkani', 'Bodo',
                      'Maithili', 'Dogri', 'Sindhi'],
        'char_range': (0x0900, 0x097F),
        'description': 'Devanagari is an abugida script used for over 120 languages in India and Nepal. '
                       'It forms the basis for writing Hindi, Sanskrit, and Marathi with a characteristic horizontal line connecting letters.'
    },
    'Arabic': {
        'languages': ['Arabic', 'Persian', 'Urdu', 'Pashto', 'Kurdish', 'Sindhi',
                      'Uyghur', 'Balochi'],
        'char_range': (0x0600, 0x06FF),
        'description': 'The Arabic script is a right-to-left cursive writing system used across the Middle East, '
                       'North Africa, and Central Asia. It is the third most widely used script in the world.'
    },
    'CJK': {
        'languages': ['Chinese Mandarin', 'Chinese Cantonese', 'Japanese Kanji',
                      'Korean Hanja'],
        'char_range': (0x4E00, 0x4E50),
        'description': 'CJK unified ideographs are logograms used in Chinese, Japanese, and Korean writing. '
                       'The system contains over 90,000 characters encoding semantic meaning through structural composition.'
    },
    'Cyrillic': {
        'languages': ['Russian', 'Ukrainian', 'Bulgarian', 'Serbian', 'Macedonian',
                      'Belarusian', 'Kazakh', 'Mongolian', 'Tajik'],
        'char_range': (0x0400, 0x04FF),
        'description': 'The Cyrillic script derives from Greek uncial script and is used by over 250 million people. '
                       'It serves as the official script for many Slavic, Turkic, and Mongolic languages.'
    },
    'Greek': {
        'languages': ['Greek Modern', 'Greek Ancient'],
        'char_range': (0x0370, 0x03FF),
        'description': 'The Greek alphabet is the ancestor of the Latin and Cyrillic scripts. '
                       'It introduced vowel letters to the writing system and is used for Modern Greek and mathematical notation.'
    },
    'Hebrew': {
        'languages': ['Hebrew', 'Yiddish', 'Ladino'],
        'char_range': (0x0590, 0x05FF),
        'description': 'The Hebrew script is a right-to-left abjad used for Hebrew, Yiddish, and historically Ladino. '
                       'It consists of 22 consonant letters and optional diacritical vowel marks.'
    },
    'Telugu': {
        'languages': ['Telugu'],
        'char_range': (0x0C00, 0x0C7F),
        'description': 'Telugu script is a South Indian abugida with rounded letterforms derived from the Bhattiprolu script. '
                       'It is used for Telugu, the fourth most spoken language in India with over 80 million native speakers.'
    },
    'Tamil': {
        'languages': ['Tamil'],
        'char_range': (0x0B80, 0x0BFF),
        'description': 'Tamil script is one of the oldest writing systems still in active use, serving the Tamil language '
                       'spoken by over 75 million people in India, Sri Lanka, Singapore, and Malaysia.'
    },
    'Kannada': {
        'languages': ['Kannada', 'Tulu', 'Konkani'],
        'char_range': (0x0C80, 0x0CFF),
        'description': 'Kannada script is a Dravidian abugida with a rich literary tradition spanning over 1500 years. '
                       'It is closely related to the Telugu script and used primarily in the Indian state of Karnataka.'
    },
    'Bengali': {
        'languages': ['Bengali', 'Assamese', 'Meitei'],
        'char_range': (0x0980, 0x09FF),
        'description': 'Bengali script is an Eastern Nagari abugida used for Bengali and Assamese languages. '
                       'Bengali is the seventh most spoken language in the world with over 230 million speakers.'
    },
    'Thai': {
        'languages': ['Thai'],
        'char_range': (0x0E00, 0x0E7F),
        'description': 'Thai script is an abugida derived from Old Khmer script, used exclusively for the Thai language. '
                       'It uses 44 consonant letters, 15 vowel symbols, and 4 tone markers without spaces between words.'
    },
    'Georgian': {
        'languages': ['Georgian', 'Mingrelian', 'Svan'],
        'char_range': (0x10A0, 0x10FF),
        'description': 'Georgian script is one of only 14 living scripts in the world with its own unique alphabet. '
                       'The Mkhedruli script has 33 letters and is the standard for modern Georgian writing.'
    },
    'Armenian': {
        'languages': ['Armenian Eastern', 'Armenian Western'],
        'char_range': (0x0530, 0x058F),
        'description': 'Armenian script was created by Mesrop Mashtots in 405 AD specifically for the Armenian language. '
                       'It originally had 36 letters and has since expanded to 39 in its modern form.'
    },
    'Ethiopic': {
        'languages': ['Amharic', 'Tigrinya', 'Oromo', 'Ge\'ez'],
        'char_range': (0x1200, 0x137F),
        'description': 'Ethiopic or Ge\'ez script is an abugida used for several languages of Ethiopia and Eritrea. '
                       'Each base character is modified with strokes to indicate vowel sounds attached to consonants.'
    },
    'Gujarati': {
        'languages': ['Gujarati'],
        'char_range': (0x0A80, 0x0AFF),
        'description': 'Gujarati script evolved from the Devanagari script but lacks the characteristic top line. '
                       'It is used for the Gujarati language spoken by over 55 million people primarily in western India.'
    },
    'Malayalam': {
        'languages': ['Malayalam'],
        'char_range': (0x0D00, 0x0D7F),
        'description': 'Malayalam script is a Dravidian abugida with highly rounded letterforms. '
                       'It has the largest number of letters among Indian language scripts with 578 distinct graphemes.'
    },
}

records = []
record_id = 0

# 1. Generate writing system descriptions
for script_name, info in WRITING_SYSTEMS.items():
    record_id += 1
    text = (f"{script_name} Writing System. {info['description']} "
            f"Languages using {script_name} include: {', '.join(info['languages'])}. "
            f"The {script_name} script encodes phonological and semantic structure through its grapheme inventory.")
    records.append({'id': f'wlac-script-{record_id:04d}', 'text': text,
                    'lang': 'en', 'source': 'WLAC', 'domain': 'writing_system'})

# 2. Generate character-level samples for each script
for script_name, info in WRITING_SYSTEMS.items():
    start, end = info['char_range']
    chars = []
    for cp in range(start, min(end + 1, start + 64)):
        try:
            c = chr(cp)
            name = unicodedata.name(c, '')
            if name:
                chars.append(f"{c} (U+{cp:04X}: {name})")
        except ValueError:
            continue
    if chars:
        record_id += 1
        text = (f"Character inventory for {script_name} script. "
                f"Sample Unicode codepoints: {'; '.join(chars[:20])}. "
                f"This script is used to write {', '.join(info['languages'][:3])} and related languages.")
        records.append({'id': f'wlac-chars-{record_id:04d}', 'text': text,
                        'lang': 'en', 'source': 'WLAC', 'domain': 'character_inventory'})

# 3. Generate cross-linguistic structural comparisons
script_pairs = [
    ('Devanagari', 'Telugu', 'Both are Indic abugida scripts with inherent vowel sounds attached to consonants.'),
    ('Latin', 'Cyrillic', 'Both descended from Greek script but diverged through Roman and Byzantine cultural paths.'),
    ('Arabic', 'Hebrew', 'Both are Semitic abjads written right-to-left with optional vowel diacritics.'),
    ('Tamil', 'Malayalam', 'Both are Dravidian scripts that evolved from the ancient Grantha writing system.'),
    ('Bengali', 'Devanagari', 'Both are Nagari-derived scripts sharing structural consonant-vowel composition.'),
    ('Kannada', 'Telugu', 'Sister scripts that share nearly identical character structures and evolved together.'),
    ('Greek', 'Latin', 'The Latin alphabet was derived from the Western Greek alphabet through Etruscan intermediation.'),
    ('Georgian', 'Armenian', 'Both are unique scripts created for specific languages in the Caucasus region.'),
]

for s1, s2, comparison in script_pairs:
    record_id += 1
    text = (f"Structural comparison between {s1} and {s2} scripts. {comparison} "
            f"{s1} is used for {', '.join(WRITING_SYSTEMS[s1]['languages'][:3])}, "
            f"while {s2} serves {', '.join(WRITING_SYSTEMS[s2]['languages'][:3])}. "
            f"Cross-script structural analysis reveals shared encoding principles in phoneme-grapheme mapping.")
    records.append({'id': f'wlac-compare-{record_id:04d}', 'text': text,
                    'lang': 'en', 'source': 'WLAC', 'domain': 'comparative_linguistics'})

# 4. Generate language family descriptions
LANGUAGE_FAMILIES = [
    ('Indo-European', ['Hindi', 'English', 'Spanish', 'Russian', 'Persian', 'Greek', 'Armenian', 'Bengali'],
     'The largest language family by number of speakers, with over 3 billion native speakers across 449 languages.'),
    ('Sino-Tibetan', ['Chinese Mandarin', 'Burmese', 'Tibetan'],
     'The second largest language family with tonal languages using logographic and syllabic scripts.'),
    ('Dravidian', ['Telugu', 'Tamil', 'Kannada', 'Malayalam'],
     'A family of languages primarily spoken in southern India with rich agglutinative morphology.'),
    ('Afro-Asiatic', ['Arabic', 'Hebrew', 'Amharic', 'Hausa'],
     'Spans North Africa and the Middle East with consonantal root morphology as a defining feature.'),
    ('Austronesian', ['Indonesian', 'Malay', 'Tagalog', 'Javanese'],
     'The most geographically widespread family, spanning from Madagascar to Easter Island.'),
    ('Niger-Congo', ['Swahili', 'Yoruba', 'Igbo', 'Zulu'],
     'The largest African language family with complex noun class systems and tonal phonology.'),
    ('Turkic', ['Turkish', 'Kazakh', 'Uzbek', 'Azerbaijani'],
     'An Altaic language group featuring vowel harmony and agglutinative morphology across Central Asia.'),
    ('Kartvelian', ['Georgian', 'Mingrelian', 'Svan'],
     'A small language family indigenous to the Caucasus with unique phonological features.'),
]

for family, langs, desc in LANGUAGE_FAMILIES:
    record_id += 1
    text = (f"{family} Language Family. {desc} "
            f"Representative languages include: {', '.join(langs)}. "
            f"Each language in the {family} family shares common structural features in morphology, "
            f"phonology, and syntax that reveal deep historical relationships.")
    records.append({'id': f'wlac-family-{record_id:04d}', 'text': text,
                    'lang': 'en', 'source': 'WLAC', 'domain': 'language_family'})

# 5. Generate morphological type descriptions
MORPH_TYPES = [
    ('Agglutinative', ['Turkish', 'Telugu', 'Tamil', 'Kannada', 'Japanese', 'Finnish', 'Hungarian'],
     'Words formed by chaining morphemes where each morpheme carries a single meaning unit.'),
    ('Fusional', ['Hindi', 'Russian', 'Spanish', 'Latin', 'Greek', 'Armenian'],
     'Morphemes fuse together carrying multiple grammatical meanings in a single affix.'),
    ('Isolating', ['Chinese Mandarin', 'Vietnamese', 'Thai'],
     'Each word is typically a single morpheme with grammatical relationships expressed through word order.'),
    ('Polysynthetic', ['Inuktitut', 'Mohawk', 'Chukchi'],
     'Single words can express what would be an entire sentence in other languages through extensive affixation.'),
]

for mtype, langs, desc in MORPH_TYPES:
    record_id += 1
    text = (f"{mtype} Morphology. {desc} "
            f"Languages exhibiting {mtype.lower()} morphology include: {', '.join(langs)}. "
            f"Understanding morphological typology is essential for computational language modeling "
            f"and structural learning engines processing multilingual data.")
    records.append({'id': f'wlac-morph-{record_id:04d}', 'text': text,
                    'lang': 'en', 'source': 'WLAC', 'domain': 'morphology'})

# Write WLAC JSONL
os.makedirs(DATA_DIR, exist_ok=True)
with open(WLAC_OUTPUT, 'w', encoding='utf-8') as f:
    for rec in records:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

total_chars = sum(len(r['text']) for r in records)
print(f'[OK] Generated {len(records)} WLAC records')
print(f'     Total text: {total_chars:,} characters')
print(f'     Domains: {set(r["domain"] for r in records)}')
print(f'     Saved to: {WLAC_OUTPUT}')

# COMMAND ----------

# DBTITLE 1,Step 2: Combine WLAC + Threshold_Onset Corpora
import json
import os
import glob

# Paths
USER_HOME = '/Workspace/Users/labuser14433625_1774766555@vocareum.com/Work'
THRESHOLD_ROOT = os.path.join(USER_HOME, 'Threshold_Onset')
DATA_DIR = os.path.join(THRESHOLD_ROOT, 'data')
WLAC_JSONL = os.path.join(DATA_DIR, 'wlac_generated.jsonl')
CLEAN_DIR = os.path.join(DATA_DIR, 'clean')
COMBINED_JSONL = os.path.join(DATA_DIR, 'combined_corpus.jsonl')

print('=== Step 2: Combining WLAC + Threshold_Onset Corpora ===')

# 1. Load existing Threshold_Onset JSONL corpus files
threshold_records = []
if os.path.exists(CLEAN_DIR):
    for jf in sorted(glob.glob(os.path.join(CLEAN_DIR, '*.jsonl'))):
        with open(jf, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                        # Ensure minimum required fields
                        if 'text' in rec and len(rec['text']) > 50:
                            threshold_records.append(rec)
                    except json.JSONDecodeError:
                        continue
        print(f'  Loaded: {os.path.basename(jf)}')
else:
    print(f'  [!] Clean directory not found: {CLEAN_DIR} — skipping Threshold_Onset JSONL files')

print(f'\nThreshold_Onset records: {len(threshold_records)}')
if threshold_records:
    print(f'Threshold_Onset chars:   {sum(len(r["text"]) for r in threshold_records):,}')

# 2. Load WLAC generated data
wlac_records = []
if os.path.exists(WLAC_JSONL):
    with open(WLAC_JSONL, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                wlac_records.append(json.loads(line))
    print(f'WLAC records:            {len(wlac_records)}')
    print(f'WLAC chars:              {sum(len(r["text"]) for r in wlac_records):,}')
else:
    print('[!] WLAC JSONL not found. Run Step 1 first.')

# 3. Also harvest text from the English dictionary for structural breadth
dict_path = os.path.join(DATA_DIR, 'english_sample_dictionary.csv')
dict_records = []
if os.path.exists(dict_path):
    import csv
    with open(dict_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        batch_text = []
        for i, row in enumerate(reader):
            if len(row) >= 2 and row[1].strip():
                batch_text.append(f"{row[0]}: {row[1].strip()[:200]}")
            # Create records in batches of 50 words
            if len(batch_text) >= 50:
                dict_records.append({
                    'id': f'dict-batch-{len(dict_records):04d}',
                    'text': ' | '.join(batch_text),
                    'lang': 'en',
                    'source': 'english_dictionary',
                    'domain': 'lexicon'
                })
                batch_text = []
            if len(dict_records) >= 200:  # Cap at 200 batches
                break
        if batch_text:
            dict_records.append({
                'id': f'dict-batch-{len(dict_records):04d}',
                'text': ' | '.join(batch_text),
                'lang': 'en',
                'source': 'english_dictionary',
                'domain': 'lexicon'
            })
    print(f'Dictionary records:      {len(dict_records)}')

# 4. Combine all sources
all_records = threshold_records + wlac_records + dict_records
print(f'\n--- Combined Corpus ---')
print(f'Total records: {len(all_records)}')
print(f'Total chars:   {sum(len(r["text"]) for r in all_records):,}')

# 5. Write combined JSONL
with open(COMBINED_JSONL, 'w', encoding='utf-8') as f:
    for rec in all_records:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print(f'\n[OK] Combined corpus saved to: {COMBINED_JSONL}')
print(f'     File size: {os.path.getsize(COMBINED_JSONL):,} bytes')

# 6. Update config to point to combined corpus (create if missing)
config_path = os.path.join(THRESHOLD_ROOT, 'config', 'default.json')
os.makedirs(os.path.dirname(config_path), exist_ok=True)

if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
else:
    config = {'santek_base_model': {}}

config.setdefault('santek_base_model', {})
config['santek_base_model']['corpus_jsonl'] = 'data/combined_corpus.jsonl'
config['santek_base_model']['training_corpus_urls'] = []
config['santek_base_model']['training_corpus_url'] = ''

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f'[OK] Config updated: corpus_jsonl -> data/combined_corpus.jsonl')

# COMMAND ----------

# DBTITLE 1,Step 3 : 10x
import os, sys, json, time, shutil
from pathlib import Path

USER_HOME = '/Workspace/Users/labuser14433625_1774766555@vocareum.com/Work'
THRESHOLD_ROOT = os.path.join(USER_HOME, 'Threshold_Onset')
DATA_DIR = os.path.join(THRESHOLD_ROOT, 'data')
MODEL_OUTPUT = Path(THRESHOLD_ROOT) / 'output' / 'santek_base_model.json'
CHECKPOINT_DIR = Path(THRESHOLD_ROOT) / 'output' / 'checkpoints'
COMBINED_JSONL = os.path.join(DATA_DIR, 'combined_corpus.jsonl')

print('=== Step 3: Training SanTEK Base Model (batched with checkpoints) ===')
print(f'Model output: {MODEL_OUTPUT}')
print(f'Checkpoints:  {CHECKPOINT_DIR}\n')

os.makedirs(MODEL_OUTPUT.parent, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# Speed env vars
for k in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'OPENBLAS_NUM_THREADS']:
    os.environ[k] = '8'
os.environ['PYTHONUNBUFFERED'] = '1'

# Add project to path
if THRESHOLD_ROOT not in sys.path:
    sys.path.insert(0, THRESHOLD_ROOT)
os.chdir(THRESHOLD_ROOT)

from integration.model import santek_train

# Load corpus
MAX_TEXT_LEN = 500
corpus = []
with open(COMBINED_JSONL, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            rec = json.loads(line)
            text = rec.get('text', '')
            if len(text) > 50:
                corpus.append(text[:MAX_TEXT_LEN])

methods = ['word', 'character', 'subword', 'subword_bpe']
BATCH_SIZE = 500
total_batches = (len(corpus) + BATCH_SIZE - 1) // BATCH_SIZE

print(f'Corpus: {len(corpus)} texts (truncated to {MAX_TEXT_LEN} chars each)')
print(f'Methods: {methods}')
print(f'Epochs per batch: 25')
print(f'Batch size: {BATCH_SIZE} texts → {total_batches} batches')
print(f'Checkpoint saved after EVERY batch\n')

overall_start = time.time()
batch_summaries = []

for batch_idx in range(total_batches):
    batch_start = batch_idx * BATCH_SIZE
    batch_end = min(batch_start + BATCH_SIZE, len(corpus))
    batch = corpus[batch_start:batch_end]
    batch_num = batch_idx + 1

    checkpoint_path = CHECKPOINT_DIR / f'checkpoint_batch{batch_num:03d}.json'

    print(f'\n{"="*76}')
    print(f'  BATCH {batch_num}/{total_batches}: texts {batch_start+1}–{batch_end} ({len(batch)} texts)')
    print(f'{"="*76}')

    t_batch = time.time()
    try:
        batch_result = santek_train(
            corpus=batch,
            epochs=25,
            eta=0.10,
            decay=0.05,
            max_streak=3,
            tension_threshold=0.10,
            patience=5,
            verbose=True,
            methods=methods,
            model_path=checkpoint_path,
        )
        batch_elapsed = time.time() - t_batch

        # Copy latest checkpoint as the main model (always have a valid model file)
        shutil.copy2(checkpoint_path, MODEL_OUTPUT)

        summary = {
            'batch': batch_num,
            'texts': f'{batch_start+1}-{batch_end}',
            'elapsed_min': round(batch_elapsed / 60, 1),
            'converged': batch_result.converged,
            'best_acc': round(batch_result.best_accuracy, 4),
            'best_tension': round(batch_result.best_tension, 4),
        }
        batch_summaries.append(summary)

        print(f'\n  ✓ Checkpoint saved: {checkpoint_path.name}')
        print(f'  ✓ Main model updated: {MODEL_OUTPUT.name}')
        print(f'  ✓ Batch time: {batch_elapsed/60:.1f} min | '
              f'Acc: {batch_result.best_accuracy:.4f} | '
              f'Tension: {batch_result.best_tension:.4f}')

    except Exception as e:
        print(f'\n  ✗ BATCH {batch_num} FAILED: {e}')
        print(f'  → Previous checkpoint still safe at {MODEL_OUTPUT}')
        batch_summaries.append({'batch': batch_num, 'error': str(e)})
        continue  # keep going with next batch

total_elapsed = time.time() - overall_start

print(f'\n{"="*76}')
print(f'  TRAINING COMPLETE')
print(f'{"="*76}')
print(f'Total time: {total_elapsed/60:.1f} minutes')
print(f'Batches completed: {len([s for s in batch_summaries if "error" not in s])}/{total_batches}')

if MODEL_OUTPUT.exists():
    print(f'Final model size: {MODEL_OUTPUT.stat().st_size:,} bytes')
    print(f'Model path: {MODEL_OUTPUT}')
else:
    print('[!] No model file produced.')

# Print summary table
print(f'\n--- Batch Summary ---')
for s in batch_summaries:
    if 'error' in s:
        print(f"  Batch {s['batch']:>3}: FAILED - {s['error'][:60]}")
    else:
        print(f"  Batch {s['batch']:>3}: {s['texts']:>12}  {s['elapsed_min']:>5.1f}min  "
              f"acc={s['best_acc']:.4f}  tension={s['best_tension']:.4f}  "
              f"{'CONVERGED' if s['converged'] else ''}")

# COMMAND ----------

import re

USER_HOME = '/Workspace/Users/labuser14433625_1774766555@vocareum.com/Work'
script_path = f'{USER_HOME}/Threshold_Onset/santek_base_model.py'

with open(script_path, 'r') as f:
    content = f.read()

# Find DEFAULT_MODEL_PATH and any model save/format references
print("=== Default model path ===")
for m in re.finditer(r'.{0,30}DEFAULT_MODEL_PATH.{0,100}', content):
    print(m.group().strip())

print("\n=== Model save/write logic ===")
for m in re.finditer(r'.{0,50}(model.*save|save.*model|write.*model|model.*write|json\.dump|pickle|torch\.save|\.pt|\.bin|\.safetensor|\.json|model_path.*open|open.*model_path).{0,150}', content, re.IGNORECASE):
    print(m.group().strip())

# COMMAND ----------

# DBTITLE 1,Step 3: Train SanTEK Base Model on Combined Corpus
# import os
# import sys

# USER_HOME = '/Workspace/Users/labuser14433625_1774709208@vocareum.com/Work'
# THRESHOLD_ROOT = os.path.join(USER_HOME, 'Threshold_Onset')
# MODEL_OUTPUT = os.path.join(THRESHOLD_ROOT, 'output', 'santek_base_model.json')

# print('=== Step 3: Training SanTEK Base Model ===')
# print(f'Repo root: {THRESHOLD_ROOT}')
# print(f'Model output: {MODEL_OUTPUT}\n')

# os.makedirs(os.path.join(THRESHOLD_ROOT, 'output'), exist_ok=True)

# # Train the SanTEK base model using the combined corpus from config
# %cd {THRESHOLD_ROOT}
# !python santek_base_model.py train --epochs 150 --model "{MODEL_OUTPUT}"

# print('\n--- Model Info ---')
# if os.path.exists(MODEL_OUTPUT):
#     print(f'Model size: {os.path.getsize(MODEL_OUTPUT):,} bytes')
#     !python santek_base_model.py info --model "{MODEL_OUTPUT}"
# else:
#     print('[!] Model file not created. Check training output above.')

# COMMAND ----------

# DBTITLE 1,Step 4: Test Generation and Validate
import os

USER_HOME = '/Workspace/Users/labuser14433625_1774766555@vocareum.com/Work'
THRESHOLD_ROOT = os.path.join(USER_HOME, 'Threshold_Onset')
MODEL_OUTPUT = os.path.join(THRESHOLD_ROOT, 'output', 'santek_base_model.json')

print('=== Step 4: Testing Generation ===')
%cd {THRESHOLD_ROOT}

# Test with several prompts that span both WLAC and Threshold_Onset data
prompts = [
    'Action before knowledge',
    'Structure emerges from',
    'The Latin script',
    'Language family',
    'Devanagari writing',
]

for prompt in prompts:
    print(f'\n{"="*60}')
    !python santek_base_model.py generate "{prompt}" --model "{MODEL_OUTPUT}" --length 25 --quiet

print(f'\n{"="*60}')
print('\n[DONE] WLAC + Threshold_Onset Combined Model Pipeline Complete')

# COMMAND ----------

"""
Serialize and parse nested mappings and sequences into a compact line-oriented text form.

Indentation uses two spaces per level. Arrays declare a length in brackets; when every
element is a mapping with the same keys and only leaf values, a header line lists field
names and following lines hold comma-separated cells. Otherwise list entries use a leading
hyphen. Intended for logs, health checks, and saved reports.

Stdlib only; no extra packages.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union

JsonValue = Union[None, bool, int, float, str, Dict[str, Any], List[Any]]

INDENT_UNIT = "  "


def _canonical_float(x: float) -> str:
    if math.isnan(x) or math.isinf(x):
        return "null"
    if x == 0.0:
        return "0"
    if abs(x - round(x)) < 1e-15 and abs(x) < 1e15:
        return str(int(round(x)))
    s = ("%.15f" % x).rstrip("0").rstrip(".")
    if s == "-0":
        return "0"
    return s


def _encode_primitive(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _canonical_float(value)
    if isinstance(value, str):
        return _quote_string(value)
    raise TypeError(f"Not JSON-encodable: {type(value)!r}")


def _quote_string(s: str) -> str:
    if s == "":
        return '""'
    needs = (
        '"' in s
        or "\\" in s
        or "\n" in s
        or "\r" in s
        or "\t" in s
        or "," in s
        or ":" in s
        or s != s.strip()
        or (s and s[0] in "0123456789+-")
        or s in ("null", "true", "false")
    )
    if not needs and re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", s):
        return s
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def _encode_key(k: str) -> str:
    if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", k) and k not in ("null", "true", "false"):
        return k
    return _quote_string(k)


def _uniform_tabular_fields(rows: List[dict]) -> Optional[List[str]]:
    if not rows:
        return []
    keys0 = list(rows[0].keys())
    for row in rows:
        if not isinstance(row, dict) or list(row.keys()) != keys0:
            return None
        for v in row.values():
            if isinstance(v, (dict, list)):
                return None
    return keys0


def _is_primitive_json(x: Any) -> bool:
    if x is None:
        return True
    if isinstance(x, bool):
        return True
    if isinstance(x, (int, float, str)):
        return True
    return False


def _emit_dict(obj: Dict[str, Any], depth: int, sort_keys: bool) -> List[str]:
    keys = sorted(obj.keys(), key=lambda x: str(x)) if sort_keys else list(obj.keys())
    lines: List[str] = []
    indent = INDENT_UNIT * depth
    for k in keys:
        v = obj[k]
        ek = _encode_key(str(k))
        if isinstance(v, dict):
            lines.append(f"{indent}{ek}:")
            lines.extend(_emit_dict(v, depth + 1, sort_keys))
        elif isinstance(v, list):
            lines.extend(_emit_array(ek, v, depth, sort_keys))
        else:
            lines.append(f"{indent}{ek}: {_encode_primitive(v)}")
    return lines


def _emit_array(name: str, items: List[Any], depth: int, sort_keys: bool) -> List[str]:
    indent = INDENT_UNIT * depth
    n = len(items)
    prefix = name
    if n == 0:
        return [f"{indent}{prefix}[0]:"]

    if all(_is_primitive_json(x) for x in items):
        body = ",".join(_encode_primitive(x) for x in items)
        return [f"{indent}{prefix}[{n}]: {body}"]

    if all(isinstance(x, dict) for x in items):
        rows = [x for x in items if isinstance(x, dict)]
        fields = _uniform_tabular_fields(rows)
        if fields is not None:
            hdr = f"{indent}{prefix}[{n}]{{{','.join(fields)}}}:"
            out = [hdr]
            row_indent = INDENT_UNIT * (depth + 1)
            for row in rows:
                cells = [_encode_primitive(row[f]) for f in fields]
                out.append(row_indent + ",".join(cells))
            return out

    out = [f"{indent}{prefix}[{n}]:"]
    child = depth + 1
    for el in items:
        out.extend(_emit_list_item(el, child, sort_keys))
    return out


def _emit_list_item(el: Any, depth: int, sort_keys: bool) -> List[str]:
    indent = INDENT_UNIT * depth
    if isinstance(el, bool):
        return [f"{indent}- {_encode_primitive(el)}"]
    if el is None or isinstance(el, (int, float, str)):
        return [f"{indent}- {_encode_primitive(el)}"]
    if isinstance(el, list):
        n = len(el)
        if n == 0:
            return [f"{indent}- [0]:"]
        if all(_is_primitive_json(x) for x in el):
            body = ",".join(_encode_primitive(x) for x in el)
            return [f"{indent}- [{n}]: {body}"]
        lines = [f"{indent}- [{n}]:"]
        for sub in el:
            lines.extend(_emit_list_item(sub, depth + 1, sort_keys))
        return lines
    if isinstance(el, dict):
        return _emit_list_item_dict(el, depth, sort_keys)
    raise TypeError(f"Unsupported list item: {type(el)!r}")


def _emit_list_item_dict(obj: Dict[str, Any], depth: int, sort_keys: bool) -> List[str]:
    indent = INDENT_UNIT * depth
    keys = sorted(obj.keys(), key=lambda x: str(x)) if sort_keys else list(obj.keys())
    if not keys:
        return [f"{indent}-"]
    k0 = keys[0]
    v0 = obj[k0]
    ek0 = _encode_key(str(k0))
    lines: List[str] = []
    if isinstance(v0, dict):
        lines.append(f"{indent}- {ek0}:")
        lines.extend(_emit_dict(v0, depth + 1, sort_keys))
    elif isinstance(v0, list):
        n = len(v0)
        if n == 0:
            lines.append(f"{indent}- {ek0}[0]:")
        elif all(_is_primitive_json(x) for x in v0):
            body = ",".join(_encode_primitive(x) for x in v0)
            lines.append(f"{indent}- {ek0}[{n}]: {body}")
        else:
            lines.append(f"{indent}- {ek0}[{n}]:")
            for sub in v0:
                lines.extend(_emit_list_item(sub, depth + 2, sort_keys))
    else:
        lines.append(f"{indent}- {ek0}: {_encode_primitive(v0)}")
    cont = depth + 1
    for k in keys[1:]:
        vk = obj[k]
        ek = _encode_key(str(k))
        if isinstance(vk, dict):
            lines.append(f"{INDENT_UNIT * cont}{ek}:")
            lines.extend(_emit_dict(vk, cont + 1, sort_keys))
        elif isinstance(vk, list):
            lines.extend(_emit_array(ek, vk, cont, sort_keys))
        else:
            lines.append(f"{INDENT_UNIT * cont}{ek}: {_encode_primitive(vk)}")
    return lines


def encode(obj: Any, *, sort_keys: bool = False) -> str:
    """Serialize a JSON-compatible value to text (UTF-8, lines separated by newline)."""
    if isinstance(obj, dict):
        lines = _emit_dict(obj, 0, sort_keys)
    elif isinstance(obj, list):
        lines = _emit_array("", obj, 0, sort_keys)
    else:
        lines = [_encode_primitive(obj)]
    text = "\n".join(lines)
    return text + ("\n" if text else "")


def _leading_depth(line: str) -> Tuple[int, str]:
    n = 0
    i = 0
    while i < len(line) and line[i] == " ":
        n += 1
        i += 1
    if n % 2 != 0:
        raise ValueError("Invalid indentation (must be a multiple of 2 spaces)")
    return n // 2, line[i:]


def _parse_scalar(token: str) -> Any:
    t = token.strip()
    if not t:
        return ""
    if t == "null":
        return None
    if t == "true":
        return True
    if t == "false":
        return False
    if t[0] == '"':
        if len(t) < 2 or t[-1] != '"':
            raise ValueError(f"Bad string token: {token!r}")
        inner = t[1:-1]
        return (
            inner.replace("\\\\", "\\")
            .replace('\\"', '"')
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
        )
    if re.match(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$", t):
        if "." in t or "e" in t.lower():
            return float(t)
        try:
            return int(t)
        except ValueError:
            return float(t)
    return t


def _split_csv_row(line: str) -> List[str]:
    out: List[str] = []
    i = 0
    cur: List[str] = []
    while i < len(line):
        c = line[i]
        if c == '"':
            cur.append(c)
            i += 1
            while i < len(line):
                if line[i] == "\\" and i + 1 < len(line):
                    cur.append(line[i])
                    cur.append(line[i + 1])
                    i += 2
                    continue
                cur.append(line[i])
                if line[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        if c == ",":
            out.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append("".join(cur).strip())
    return out


def _parse_tabular_array(
    lines: List[Tuple[int, str]], pos: int, depth: int, name: str, n_expect: int, fields: List[str]
) -> Tuple[List[Dict[str, Any]], int]:
    rows: List[Dict[str, Any]] = []
    pos += 1
    for _ in range(n_expect):
        if pos >= len(lines):
            break
        d, row_line = lines[pos]
        if d != depth + 1 or row_line.startswith("- "):
            break
        cells = _split_csv_row(row_line)
        row: Dict[str, Any] = {}
        for i, f in enumerate(fields):
            row[f] = _parse_scalar(cells[i]) if i < len(cells) else None
        rows.append(row)
        pos += 1
    return rows, pos


def _parse_list_items(lines: List[Tuple[int, str]], pos: int, item_depth: int) -> Tuple[List[Any], int]:
    items: List[Any] = []
    while pos < len(lines):
        d, txt = lines[pos]
        if d < item_depth:
            break
        if d == item_depth:
            if not txt.startswith("- "):
                break
            item, pos = _parse_list_item_line(lines, pos, item_depth)
            items.append(item)
        else:
            break
    return items, pos


def _parse_list_item_line(lines: List[Tuple[int, str]], pos: int, item_depth: int) -> Tuple[Any, int]:
    d, txt = lines[pos]
    if d != item_depth or not txt.startswith("- "):
        raise ValueError("Expected list item")
    rest = txt[2:].strip()
    if not rest:
        pos += 1
        nested, pos = _parse_object(lines, pos, item_depth + 1)
        return nested, pos
    if ":" not in rest:
        return _parse_scalar(rest), pos + 1

    key_part, after = rest.split(":", 1)
    key_part = key_part.strip()
    after = after.strip()

    m_anon = re.match(r"^\[(\d+)\]$", key_part)
    if m_anon:
        if after:
            parts = _split_csv_row(after) if ("," in after or '"' in after) else [p.strip() for p in after.split(",")]
            arr = [_parse_scalar(p) for p in parts]
            return arr, pos + 1
        pos += 1
        return _parse_list_items(lines, pos, item_depth + 1)

    m_named = re.match(r"^([^[]+)\[(\d+)\]$", key_part)
    if m_named and after:
        parts = _split_csv_row(after) if ("," in after or '"' in after) else [p.strip() for p in after.split(",")]
        return {m_named.group(1): [_parse_scalar(p) for p in parts]}, pos + 1

    if m_named and not after:
        n_expect = int(m_named.group(2))
        name = m_named.group(1)
        pos += 1
        sub_items, pos = _parse_list_items(lines, pos, item_depth + 1)
        return {name: sub_items}, pos

    k = key_part
    if not after:
        pos += 1
        nested, pos = _parse_object(lines, pos, item_depth + 1)
        return {k: nested}, pos

    val = _parse_scalar(after)
    pos += 1
    obj: Dict[str, Any] = {k: val}
    while pos < len(lines):
        d2, t2 = lines[pos]
        if d2 <= item_depth:
            break
        if d2 == item_depth + 1 and not t2.startswith("- "):
            if ":" in t2:
                sk, safter = t2.split(":", 1)
                sk = sk.strip()
                safter = safter.strip()
                if not safter:
                    pos += 1
                    nested, pos = _parse_object(lines, pos, item_depth + 2)
                    obj[sk] = nested
                else:
                    obj[sk] = _parse_scalar(safter)
                    pos += 1
            else:
                break
        else:
            break
    return obj, pos


def _parse_object(lines: List[Tuple[int, str]], pos: int, depth: int) -> Tuple[Dict[str, Any], int]:
    obj: Dict[str, Any] = {}
    n = len(lines)
    while pos < n:
        d, text = lines[pos]
        if d < depth:
            break
        if d > depth:
            raise ValueError(f"Unexpected deeper indent at line {pos}")
        if text.startswith("- "):
            break

        if ":" not in text:
            raise ValueError(f"Expected key: value at line {pos}")

        key_part, rest = text.split(":", 1)
        key_part = key_part.strip()
        rest = rest.strip()

        m_tab = re.match(r"^([^[]+)\[(\d+)\]\{([^}]*)\}$", key_part)
        if m_tab:
            name, nrows, fields_s = m_tab.group(1), int(m_tab.group(2)), m_tab.group(3)
            fields = [f.strip() for f in fields_s.split(",") if f.strip()]
            rows, pos = _parse_tabular_array(lines, pos, d, name, nrows, fields)
            obj[name] = rows
            continue

        m_arr = re.match(r"^([^[]*)\[(\d+)\]$", key_part)
        if m_arr:
            name, n_expect = m_arr.group(1), int(m_arr.group(2))
            store_key = name if name else "_"
            if rest:
                parts = _split_csv_row(rest) if ("," in rest or '"' in rest) else [p.strip() for p in rest.split(",")]
                obj[store_key] = [_parse_scalar(p) for p in parts]
                pos += 1
                continue
            pos += 1
            items, pos = _parse_list_items(lines, pos, d + 1)
            obj[store_key] = items
            continue

        name = key_part
        if rest:
            obj[name] = _parse_scalar(rest)
            pos += 1
            continue

        pos += 1
        nested, pos = _parse_object(lines, pos, depth + 1)
        obj[name] = nested

    return obj, pos


def decode_document(text: str) -> Dict[str, Any]:
    """Parse a document made of top-level key lines into one mapping object."""
    raw_lines = text.splitlines()
    lines: List[Tuple[int, str]] = []
    for ln in raw_lines:
        if not ln.strip():
            continue
        d, rest = _leading_depth(ln)
        lines.append((d, rest))
    if not lines:
        return {}
    doc, _ = _parse_object(lines, 0, 0)
    return doc


def decode(text: str) -> Any:
    """Parse serialized text from :func:`encode` back into Python values."""
    t = text.strip()
    if not t:
        return None
    if "\n" not in t and ":" not in t:
        return _parse_scalar(t)
    doc = decode_document(text)
    if len(doc) == 1 and "_" in doc:
        return doc["_"]
    return doc


# COMMAND ----------

import os
import json
import glob

# Configuration
wlac_data_path = '/content/WLAC_data/backend/app/data'
repo_root = '/content/Threshold_Onset'
model_output = os.path.join(repo_root, 'output/mini_least_model.json')

print('--- Final Heavy-Duty Data Harvest: WLAC ---')
corpus = []

# 1. Harvest every semantic relation from all JSON files
json_files = glob.glob(os.path.join(wlac_data_path, '**/*.json'), recursive=True)
for f_path in json_files:
    try:
        with open(f_path, 'r', encoding='utf-8') as f:
            # Clean JSON tokens to build pure structural transitions
            text = json.dumps(json.load(f))
            tokens = text.replace('{', ' ').replace('}', ' ').replace('[', ' ').replace(']', ' ').replace(',', ' ').replace('"', ' ').split()
            corpus.extend(tokens)
    except: continue

print(f'Total Tokens Harvested: {len(corpus):,}')

# 2. Standalone Structural Learning Engine (Optimized)
class HeavyLeastEngine:
    def __init__(self):
        self.map = {}

    def train(self, tokens):
        for i in range(len(tokens)-1):
            head, tail = tokens[i], tokens[i+1]
            if head not in self.map: self.map[head] = set()
            self.map[head].add(tail)

    def save(self, path):
        serializable = {k: list(v) for k, v in self.map.items()}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(serializable, f, indent=2)

print('\n--- Executing Extra Least Model Development ---')
engine = HeavyLeastEngine()
engine.train(corpus)
engine.save(model_output)

if os.path.exists(model_output):
    print(f'[SUCCESS] Extra Least Model Manifested: {model_output}')
    print(f'Total Structural Nodes: {len(engine.map):,}')

    # Validation: Peek at the model
    with open(model_output, 'r') as f:
        data = json.load(f)
        print('\n--- Knowledge Sample (Jnana) ---')
        for k in list(data.keys())[:5]:
            print(f'{k} -> {data[k][:3]}...')
else:
    print('[!] Model development failed.')

# COMMAND ----------

import os
import subprocess

wlac_backend_path = '/content/WLAC_data/backend'

if os.path.exists(wlac_backend_path):
    print('--- Running WLAC Data Generation ---')
    # Navigate to the backend and run the dataset generator
    %cd {wlac_backend_path}

    # Running the generation script which likely produces the slm_training_base.csv
    !python generate_full_dataset.py

    print('\n--- Checking for Generated Data ---')
    !find . -name "*.csv"
else:
    print('WLAC backend directory not found. Please ensure the repo is cloned correctly.')

# COMMAND ----------

import os
import json
import glob

# Configuration
wlac_data_path = '/content/WLAC_data/backend/app/data'
repo_root = '/content/Threshold_Onset'
model_output = os.path.join(repo_root, 'output/mini_least_model.json')

print('--- Starting Massive Data Harvest from WLAC ---')
corpus_accumulator = []

# Gather every JSON file in the data tree
json_files = glob.glob(os.path.join(wlac_data_path, '**/*.json'), recursive=True)

for f_path in json_files:
    try:
        with open(f_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            # We stringify the entire object to extract all semantic relations
            corpus_accumulator.append(json.dumps(content))
    except Exception as e:
        continue

full_corpus = " ".join(corpus_accumulator)
print(f'Total Data Harvested: {len(full_corpus):,} characters from {len(json_files)} files.')

# Standalone Structural Learning Engine (Extra Least)
class ExtraLeastEngine:
    def __init__(self):
        self.structure = {}

    def train(self, text):
        # Clean and tokenize simply for 'least' footprint
        tokens = text.replace('{', ' ').replace('}', ' ').replace('[', ' ').replace(']', ' ').replace(',', ' ').replace('"', ' ').split()

        for i in range(len(tokens)-1):
            head, tail = tokens[i], tokens[i+1]
            if head not in self.structure:
                self.structure[head] = set() # Use set for unique relations
            self.structure[head].add(tail)

    def save(self, path):
        # Convert sets to lists for JSON serialization
        serializable = {k: list(v) for k, v in self.structure.items()}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2)

print('\n--- Executing Extra Least Training (Action before Knowledge) ---')
engine = ExtraLeastEngine()
engine.train(full_corpus)
engine.save(model_output)

print(f'[OK] Model developed and saved: {model_output}')
print(f'Total Unique Structural Nodes: {len(engine.structure):,}')

# COMMAND ----------

