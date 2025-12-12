"""
Variety Injector Service
Provides randomized seeds and constraints to prevent repetitive LLM outputs.
"""
import json
import os
import random
from pathlib import Path
from typing import Dict, List, Any

# Emotion seeds for thematic variety
EMOTION_POOL = [
    "lingering regret", "quiet fury", "bitter hope", "hollow victory",
    "desperate longing", "cold resignation", "fierce devotion", "buried shame",
    "reluctant acceptance", "smoldering resentment", "fragile trust", "weary determination",
    "consuming guilt", "unexpected tenderness", "silent grief", "defiant joy"
]

# Aesthetic seeds for visual/atmospheric variety
AESTHETIC_POOL = [
    "ash and bronze", "bone and silk", "rust and amber", "frost and obsidian",
    "tarnished gold", "weathered stone", "dried blood", "faded tapestry",
    "cracked porcelain", "iron and incense", "salt and shadow", "moss and ruin",
    "ember and soot", "pearl and venom", "copper and rain", "ivory and char"
]

# Conflict seeds for narrative variety
CONFLICT_POOL = [
    "inheritance dispute", "forbidden knowledge", "broken oath", "stolen birthright",
    "unpayable debt", "mercy misinterpreted", "necessary cruelty", "love across enemy lines",
    "duty versus desire", "truth that destroys", "salvation through sin", "peace through surrender",
    "justice delayed", "revenge incomplete", "loyalty unrewarded", "sacrifice unwitnessed"
]


class VarietyInjector:
    """
    Provides randomized seeds and constraints to LLM prompts to ensure
    variety and avoid common patterns.
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to the data directory relative to this file
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        self.data_dir = Path(data_dir)
        self.name_pools = self._load_name_pools()
        self.event_templates = self._load_event_templates()
        self.banned_words = self._load_banned_words()
        self.game_inspirations = self._load_game_inspirations()
    
    def _load_name_pools(self) -> Dict[str, Dict]:
        """Load all cultural name pools from JSON files."""
        pools = {}
        name_pool_dir = self.data_dir / 'name_pools'
        
        if name_pool_dir.exists():
            for file_path in name_pool_dir.glob('*.json'):
                culture_name = file_path.stem.replace('_names', '')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        pools[culture_name] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load {file_path}: {e}")
        
        return pools
    
    def _load_event_templates(self) -> List[Dict]:
        """Load historical event templates."""
        event_file = self.data_dir / 'event_templates.json'
        
        if event_file.exists():
            try:
                with open(event_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load event templates: {e}")
        
        return []
    
    def _load_banned_words(self) -> List[str]:
        """Load list of banned/overused words."""
        banned_file = self.data_dir / 'banned_lore_words.txt'
        words = []
        
        if banned_file.exists():
            try:
                with open(banned_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and section headers
                        if line and not line.startswith('#') and not line.startswith('##'):
                            words.append(line)
            except Exception as e:
                print(f"Warning: Could not load banned words: {e}")
        
        return words
    
    def _load_game_inspirations(self) -> Dict[str, Dict]:
        """Load game inspiration data."""
        games_file = self.data_dir / 'game_inspirations.json'
        
        if games_file.exists():
            try:
                with open(games_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load game inspirations: {e}")
        
        return {}
    
    def get_generation_seeds(self) -> Dict[str, Any]:
        """
        Generate a randomized set of seeds for a single lore generation run.
        Each call returns different seeds to ensure variety between generations.
        """
        # Select 1-2 random cultural name pools
        available_cultures = list(self.name_pools.keys())
        num_cultures = min(2, len(available_cultures))
        selected_cultures = random.sample(available_cultures, num_cultures) if available_cultures else []
        
        # Select 2-3 random historical event templates
        num_events = min(3, len(self.event_templates))
        selected_events = random.sample(self.event_templates, num_events) if self.event_templates else []
        
        # Select a random game for thematic inspiration
        available_games = list(self.game_inspirations.keys())
        selected_game = random.choice(available_games) if available_games else None
        
        return {
            "name_cultures": selected_cultures,
            "name_pools": {c: self.name_pools[c] for c in selected_cultures},
            "event_inspirations": selected_events,
            "banned_words": self.banned_words,
            "emotion_seed": random.choice(EMOTION_POOL),
            "aesthetic_seed": random.choice(AESTHETIC_POOL),
            "conflict_seed": random.choice(CONFLICT_POOL),
            "game_reference": selected_game,
            "game_details": self.game_inspirations.get(selected_game, {}) if selected_game else {}
        }
    
    def get_sample_names(self, count: int = 5, gender: str = None) -> List[str]:
        """
        Get a random sample of names from the currently selected cultures.
        Useful for providing name suggestions in prompts.
        """
        seeds = self.get_generation_seeds()
        all_names = []
        
        for culture in seeds['name_cultures']:
            pool = self.name_pools.get(culture, {})
            if gender == 'male' and 'male' in pool:
                all_names.extend(pool['male'])
            elif gender == 'female' and 'female' in pool:
                all_names.extend(pool['female'])
            else:
                all_names.extend(pool.get('male', []))
                all_names.extend(pool.get('female', []))
        
        if not all_names:
            return []
        
        return random.sample(all_names, min(count, len(all_names)))
    
    def format_seeds_for_prompt(self, seeds: Dict[str, Any]) -> str:
        """
        Format the seeds into a string suitable for injection into an LLM prompt.
        """
        lines = [
            "=== VARIETY CONSTRAINTS ===",
            "",
            f"Emotional Tone: {seeds['emotion_seed']}",
            f"Aesthetic: {seeds['aesthetic_seed']}",
            f"Core Conflict: {seeds['conflict_seed']}",
            "",
            f"Cultural Inspiration: Draw names and concepts from {', '.join(seeds['name_cultures'])} traditions.",
            "",
        ]
        
        if seeds['event_inspirations']:
            lines.append("Historical Parallels (for inspiration, not copying):")
            for event in seeds['event_inspirations']:
                lines.append(f"  - {event['name']}: {event['description']}")
            lines.append("")
        
        if seeds['game_reference']:
            game = seeds['game_details']
            lines.append(f"Thematic Reference: {game.get('full_name', seeds['game_reference'])}")
            if 'themes' in game:
                lines.append(f"  Themes to consider: {', '.join(game['themes'][:3])}")
            lines.append("")
        
        lines.append("BANNED WORDS/PHRASES (do NOT use these):")
        # Show a sample of banned words
        sample_banned = random.sample(seeds['banned_words'], min(15, len(seeds['banned_words'])))
        lines.append(f"  {', '.join(sample_banned)}")
        lines.append("")
        lines.append("=== END VARIETY CONSTRAINTS ===")
        
        return '\n'.join(lines)
