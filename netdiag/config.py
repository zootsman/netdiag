import json
from pathlib import Path
from deepmerge.merger import Merger # Import Merger
from deepmerge import strategy as s # Import strategies

CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_CONFIG_FILE = Path(__file__).parent.parent / "config.default.json" # Relative to netdiag/

# Custom strategy for lists: always replace the list from the next dictionary
def list_replace_strategy(config, path, base, nxt):
    return nxt

# Create a custom merger that replaces lists instead of concatenating them
list_replacer_merger = Merger(
    # type_strategies: apply custom list strategy, use default for dicts
    [(list, list_replace_strategy),
     (dict, s.DictStrategies.strategy_merge)],
    # fallback_strategies: how to handle types not explicitly in type_strategies
    # 'override' will simply take the 'next' value
    ["override"],
    # type_conflict_strategies: how to handle conflicts when types differ
    # 'override' will simply take the 'next' value
    ["override"]
)

def load_default_config():
    """Loads the default configuration from config.default.json."""
    if not DEFAULT_CONFIG_FILE.exists():
        # This should ideally not happen if the file is packaged correctly
        return {} 
    try:
        with open(DEFAULT_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading default config: {e}")
        return {}

def load_config():
    CONFIG_DIR.mkdir(exist_ok=True)
    default_cfg = load_default_config()
    user_cfg = {}

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
        except Exception as e:
            print(f"Error loading user config: {e}")
            # If user config is broken, we might want to back it up and start fresh
            pass
    
    # Use the custom merger to merge default and user config, with user config taking precedence
    merged_cfg = list_replacer_merger.merge(default_cfg, user_cfg)
    return merged_cfg

def save_config(cfg):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)