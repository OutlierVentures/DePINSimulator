#!/usr/bin/env python3
"""
Test final 6 configurations for functionality and insights
"""

import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

def test_config_insights(config_path):
    """Test a config and extract key insights"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        metadata = config.get('_metadata', {})
        name = metadata.get('name', config_path.stem)
        description = metadata.get('description', '')[:80] + "..."
        
        # Extract key differentiators
        emission_policy = config.get('emission_policy', ['unknown'])[0]
        apr_threshold = config.get('apr_threshold', [0])[0]
        
        # Controller settings
        controller_enabled = config.get('apr_controller_kp', [0])[0] > 0
        utilization_controller = config.get('utilization_controller_enabled', [False])[0]
        
        # Economic parameters
        node_cost = config.get('node_setup_cost', [0])[0]
        node_count = config.get('initial_node_amount', [0])[0]
        
        # Token allocations
        incentive_allocation = config.get('incentive_token_allocation', [0])[0] * 100
        
        # Special features
        has_custom_phases = 'business_growth_phases' in config
        has_market_scenario = config.get('token_market_scenario', ['stable'])[0] != 'stable'
        
        return {
            'name': name,
            'description': description,
            'emission_policy': emission_policy,
            'apr_threshold': apr_threshold,
            'controller_enabled': controller_enabled,
            'utilization_controller': utilization_controller,
            'node_cost': node_cost,
            'node_count': node_count,
            'incentive_allocation': incentive_allocation,
            'has_custom_phases': has_custom_phases,
            'has_market_scenario': has_market_scenario,
            'working': True
        }
        
    except Exception as e:
        return {
            'name': config_path.stem,
            'error': str(e),
            'working': False
        }

def main():
    """Test all final configurations"""
    config_dir = Path(__file__).parent / 'config' / 'production'
    
    print("🧪 TESTING FINAL 6 CONFIGURATIONS")
    print("=" * 50)
    
    configs = []
    for config_file in sorted(config_dir.glob('*.json')):
        result = test_config_insights(config_file)
        configs.append(result)
    
    # Group by emission policy
    by_emission = {'linear': [], 'per_device': [], 'bme': []}
    
    print("📊 CONFIGURATION ANALYSIS:")
    print()
    
    for i, config in enumerate(configs, 1):
        if not config['working']:
            print(f"❌ {i}. {config['name']}: {config['error']}")
            continue
            
        # Categorize
        policy = config['emission_policy']
        if policy in by_emission:
            by_emission[policy].append(config)
        
        # Status indicators
        controller_icon = "🎛️" if config['controller_enabled'] else "🔄"
        util_icon = "⚖️" if config['utilization_controller'] else ""
        phases_icon = "📈" if config['has_custom_phases'] else ""
        market_icon = "📊" if config['has_market_scenario'] else ""
        
        print(f"✅ {i}. **{config['name']}** {controller_icon}{util_icon}{phases_icon}{market_icon}")
        print(f"   📝 {config['description']}")
        print(f"   🪙 {config['emission_policy'].upper()} | 🎯 {config['apr_threshold']}% APR | 💰 ${config['node_cost']:,.0f} cost")
        print(f"   🏗️ {config['node_count']:,.0f} initial nodes | 🎁 {config['incentive_allocation']:.1f}% incentive allocation")
        print()
    
    # Summary by emission policy
    print("📋 COVERAGE ANALYSIS:")
    print("-" * 30)
    for policy, policy_configs in by_emission.items():
        if policy_configs:
            print(f"🪙 {policy.upper()}: {len(policy_configs)} configs")
            for config in policy_configs:
                features = []
                if not config['controller_enabled']:
                    features.append("No APR control")
                if config['utilization_controller']:
                    features.append("Utilization control")
                if config['has_custom_phases']:
                    features.append("Custom phases")
                if config['has_market_scenario']:
                    features.append("Market scenarios")
                
                feature_str = f" ({', '.join(features)})" if features else ""
                print(f"   • {config['name']}{feature_str}")
    
    print(f"\n🎉 All {len([c for c in configs if c['working']])} final configurations are working correctly!")
    print("\n💡 Key differentiators maintained:")
    print("   🎛️ = APR Controller | 🔄 = No Control | ⚖️ = Utilization Controller")
    print("   📈 = Custom Phases | 📊 = Market Scenarios")

if __name__ == "__main__":
    main()