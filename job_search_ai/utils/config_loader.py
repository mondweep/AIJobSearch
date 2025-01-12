import yaml
from pathlib import Path

class ConfigLoader:
    @staticmethod
    def load_config():
        """Load search configuration from YAML file"""
        config_path = Path(__file__).parent.parent / 'config' / 'search_config.yaml'
        
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            
        return config

    @staticmethod
    def get_search_criteria():
        """Get search criteria from config"""
        config = ConfigLoader.load_config()
        return config['search_criteria']

    @staticmethod
    def get_filters():
        """Get filter configurations from config"""
        config = ConfigLoader.load_config()
        return config['filters']
