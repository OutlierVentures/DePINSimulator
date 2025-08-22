"""
DePIN Simulator Configuration Management
======================================

Organized configuration templates for different DePIN network scenarios.

Directory Structure:
- config/templates/: Base template configurations
- config/production/: Production-ready parameter sets  
- config/research/: Research and testing configurations

Usage:
    from config import get_config
    params = get_config('production/conservative_bootstrap')
"""

import os
import json
from typing import Dict, List

def get_config(config_name: str) -> Dict:
    """
    Load configuration by name from the config directory
    
    Args:
        config_name: Path to config file (e.g., 'production/conservative_bootstrap')
        
    Returns:
        Dictionary containing the configuration parameters
    """
    config_path = os.path.join(os.path.dirname(__file__), f"{config_name}.json")
    
    if not os.path.exists(config_path):
        available = list_available_configs()
        raise FileNotFoundError(f"Config '{config_name}' not found. Available: {available}")
    
    with open(config_path, 'r') as f:
        return json.load(f)

def list_available_configs() -> List[str]:
    """List all available configuration files"""
    config_dir = os.path.dirname(__file__)
    configs = []
    
    for root, dirs, files in os.walk(config_dir):
        for file in files:
            if file.endswith('.json') and file != '__init__.json':
                rel_path = os.path.relpath(os.path.join(root, file), config_dir)
                config_name = rel_path.replace('.json', '').replace(os.sep, '/')
                configs.append(config_name)
    
    return sorted(configs)

def print_config_summary(config_name: str):
    """Print a summary of a configuration"""
    config = get_config(config_name)
    
    print(f"\n📋 Configuration: {config_name}")
    print("=" * 50)
    print(f"Initial Nodes: {config['initial_node_amount'][0]:,}")
    print(f"Incentive Allocation: {config['incentive_token_allocation'][0]:.0%}")
    print(f"Vesting Duration: {config['incentive_token_vesting_duration'][0]/365:.1f} years")
    print(f"Emission Policy: {config['emission_policy'][0]}")
    print(f"Target APR: {config['apr_threshold'][0]}%")
    
    if 'description' in config:
        print(f"\nDescription: {config['description']}")
    if 'best_for' in config:
        print(f"Best for: {config['best_for']}")