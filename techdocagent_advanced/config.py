import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field


@dataclass
class AgentConfig:
    """Main configuration for TechDocAgent Advanced."""

    gemini_api_key: str = ""
    embedding_model: str = "models/embedding-001"
    generation_model: str = "gemini-pro"

    project_root: str = "."
    output_dir: str = "./docs"
    memory_db_path: str = ".techdoc_memory.db"
    embeddings_path: str = ".techdoc_embeddings"

    code_extensions: List[str] = field(default_factory=lambda: [
        '.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.go',
        '.rb', '.php', '.rs', '.swift', '.kt', '.m', '.scala'
    ])
    ignore_patterns: List[str] = field(default_factory=lambda: [
        '__pycache__', 'node_modules', '.git', '.venv', 'venv',
        '*.pyc', '*.pyo', 'dist', 'build', '.idea', '.vscode'
    ])
    respect_gitignore: bool = True

    doc_types: List[str] = field(default_factory=lambda: [
        'README', 'API', 'ONBOARDING', 'CHANGELOG', 'ARCHITECTURE'
    ])
    default_doc_type: str = 'README'
    auto_save: bool = True
    output_format: str = 'markdown'

    use_ast_analysis: bool = True
    use_embeddings: bool = True
    max_chunk_size: int = 1000
    min_chunk_size: int = 10

    enable_change_detection: bool = True
    use_git_tracking: bool = True
    incremental_updates: bool = True

    enable_feedback: bool = True
    auto_apply_corrections: bool = False

    temperature: float = 0.7
    max_tokens: int = 8000
    top_p: float = 0.95
    top_k: int = 40

    batch_size: int = 10
    parallel_processing: bool = True
    max_workers: int = 4

    log_level: str = "INFO"
    log_file: Optional[str] = None

    custom_templates_dir: Optional[str] = None

    features: Dict[str, bool] = field(default_factory=lambda: {
        'embeddings': True,
        'change_detection': True,
        'feedback_loop': True,
        'ast_analysis': True,
        'versioning': True,
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create config from dictionary."""

        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if self.features.get('embeddings', True) and not self.gemini_api_key:
            if not os.getenv('GEMINI_API_KEY'):
                errors.append("Gemini API key not configured and embeddings are enabled")

        if not os.path.exists(self.project_root):
            errors.append(f"Project root does not exist: {self.project_root}")

        if not 0.0 <= self.temperature <= 1.0:
            errors.append(f"Temperature must be between 0.0 and 1.0, got {self.temperature}")

        if self.max_tokens < 100:
            errors.append(f"max_tokens too small: {self.max_tokens}")

        if self.min_chunk_size >= self.max_chunk_size:
            errors.append("min_chunk_size must be less than max_chunk_size")

        return errors


class ConfigManager:
    """
    Manages configuration loading, saving, and validation.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config file (optional)
        """
        self.config_path = config_path or self._find_config_file()
        self.config: AgentConfig = AgentConfig()

        if self.config_path and os.path.exists(self.config_path):
            self.load()
        else:
            self._load_from_env()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_paths = [
            '.techdocagent.json',
            '.techdocagent.yaml',
            '.techdocagent.yml',
            'techdocagent.json',
            'config/techdocagent.json',
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def load(self, config_path: Optional[str] = None) -> AgentConfig:
        """
        Load configuration from file.

        Args:
            config_path: Path to config file (uses default if not provided)

        Returns:
            Loaded configuration
        """
        path = config_path or self.config_path

        if not path or not os.path.exists(path):
            print(f"Config file not found: {path}. Using defaults.")
            self._load_from_env()
            return self.config

        ext = Path(path).suffix.lower()

        try:
            with open(path, 'r') as f:
                if ext == '.json':
                    data = json.load(f)
                elif ext in ('.yaml', '.yml'):
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        print("PyYAML not installed. Cannot load YAML config.")
                        return self.config
                else:
                    print(f"Unsupported config format: {ext}")
                    return self.config

            self.config = AgentConfig.from_dict(data)
            self._load_from_env() 

            print(f"Loaded configuration from {path}")

        except Exception as e:
            print(f"Error loading config: {e}")

        return self.config

    def _load_from_env(self):
        """Load configuration from environment variables."""

        if os.getenv('GEMINI_API_KEY'):
            self.config.gemini_api_key = os.getenv('GEMINI_API_KEY')

        if os.getenv('TECHDOC_OUTPUT_DIR'):
            self.config.output_dir = os.getenv('TECHDOC_OUTPUT_DIR')

        if os.getenv('TECHDOC_PROJECT_ROOT'):
            self.config.project_root = os.getenv('TECHDOC_PROJECT_ROOT')

        if os.getenv('TECHDOC_LOG_LEVEL'):
            self.config.log_level = os.getenv('TECHDOC_LOG_LEVEL')

    def save(self, config_path: Optional[str] = None):
        """
        Save configuration to file.

        Args:
            config_path: Path to save config (uses default if not provided)
        """
        path = config_path or self.config_path or '.techdocagent.json'
        ext = Path(path).suffix.lower()

        try:
            with open(path, 'w') as f:
                if ext == '.json':
                    json.dump(self.config.to_dict(), f, indent=2)
                elif ext in ('.yaml', '.yml'):
                    try:
                        import yaml
                        yaml.dump(self.config.to_dict(), f, default_flow_style=False)
                    except ImportError:
                        print("PyYAML not installed. Cannot save YAML config.")
                        return
                else:
                    print(f"Unsupported config format: {ext}")
                    return

            print(f"Saved configuration to {path}")

        except Exception as e:
            print(f"Error saving config: {e}")

    def validate(self) -> bool:
        """
        Validate current configuration.

        Returns:
            True if valid, False otherwise
        """
        errors = self.config.validate()

        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        print("Configuration is valid")
        return True

    def create_default_config(self, output_path: str = '.techdocagent.json'):
        """
        Create a default configuration file.

        Args:
            output_path: Where to save the default config
        """
        default_config = AgentConfig()

        with open(output_path, 'w') as f:
            json.dump(default_config.to_dict(), f, indent=2)

        print(f"Created default configuration at {output_path}")
        print("Please update the configuration with your settings, especially:")
        print("  - gemini_api_key: Your Gemini API key")
        print("  - project_root: Path to your project")
        print("  - output_dir: Where to save documentation")

    def get(self) -> AgentConfig:
        """Get current configuration."""
        return self.config

    def update(self, **kwargs):
        """
        Update configuration with new values.

        Args:
            **kwargs: Configuration fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"Warning: Unknown config field '{key}'")

    def enable_feature(self, feature: str):
        """Enable a feature."""
        self.config.features[feature] = True

    def disable_feature(self, feature: str):
        """Disable a feature."""
        self.config.features[feature] = False

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.config.features.get(feature, False)

    def print_config(self):
        """Print current configuration."""
        print("\n" + "=" * 60)
        print("TechDocAgent Advanced - Configuration")
        print("=" * 60)

        config_dict = self.config.to_dict()

        if config_dict.get('gemini_api_key'):
            config_dict['gemini_api_key'] = '***' + config_dict['gemini_api_key'][-4:]

        for key, value in config_dict.items():
            print(f"{key}: {value}")

        print("=" * 60 + "\n")


def load_config(config_path: Optional[str] = None) -> AgentConfig:
    """
    Convenience function to load configuration.

    Args:
        config_path: Optional path to config file

    Returns:
        AgentConfig instance
    """
    manager = ConfigManager(config_path)
    return manager.config
