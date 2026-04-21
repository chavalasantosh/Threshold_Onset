"""
Brain Loader — Sovereign Language Brain (SLB) Integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loads the pre-computed Layers 3 and 4 into RAM for instant O(1) lookup.
Bypasses the need to re-run THRESHOLD_ONSET Phase 0-10 on every query.
"""

import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAIN_DIR = os.path.join(ROOT, "output", "brain")

class SovereignBrain:
    def __init__(self):
        self.manifest = {}
        self.escape_map = {}
        self.hash_to_text = {}
        self.word_to_hash = {}
        self.is_loaded = False
        
    def load(self):
        manifest_path = os.path.join(BRAIN_DIR, "sovereign_brain.json")
        escape_path = os.path.join(BRAIN_DIR, "layer3_escape_map.json")
        surface_path = os.path.join(BRAIN_DIR, "layer4_surface.json")
        
        if not all(os.path.exists(p) for p in [manifest_path, escape_path, surface_path]):
            return False
            
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f)
                
            with open(escape_path, "r", encoding="utf-8") as f:
                self.escape_map = json.load(f)
                
            with open(surface_path, "r", encoding="utf-8") as f:
                surface = json.load(f)
                self.hash_to_text = surface.get("hash_to_text", {})
                self.word_to_hash = surface.get("word_to_hash", {})
                
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"[!] Brain load error: {e}")
            return False
        
    def get_escape_seed(self, query_tokens):
        """
        O(1) Instant Lookup of the Escape Boundary for a sequence of tokens.
        Finds the word in the query with the lowest escape_concentration (most mobile).
        Returns:
            best_word: The most mobile input word
            escape_boundary_word: Its top escape target
            tension: The tension class
        """
        if not self.is_loaded:
            return None, None, "Neutral"
            
        best_word = None
        lowest_concentration = 1.0 # 1.0 means trapped, 0.0 means free
        escape_boundary_word = None
        tension = "Neutral"
        
        for token in query_tokens:
            word = ''.join(c for c in token if c.isalnum() or c in "-'").lower()
            if not word:
                continue
                
            word_data = self.escape_map.get(word)
            if word_data:
                conc = word_data.get("escape_concentration", 1.0)
                if conc <= lowest_concentration:
                    lowest_concentration = conc
                    best_word = word
                    escape_boundary_word = word_data.get("top_escape")
                    tension = word_data.get("tension_class", "Neutral")
                    
        return best_word, escape_boundary_word, tension
