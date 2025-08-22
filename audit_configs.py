#!/usr/bin/env python3
"""
Comprehensive Configuration Audit Script
Tests all configs for functionality and economic insights
"""

import sys
import os
import json
import traceback
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

def test_config(config_path):
    """Test a single configuration file"""
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Extract metadata
        metadata = config.get('_metadata', {})
        name = metadata.get('name', config_path.stem)
        description = metadata.get('description', 'No description')
        
        # Basic validation checks
        issues = []
        
        # Check revenue shares sum to ~1.0
        revenue_shares = [
            config.get('node_revenue_share', [0])[0],
            config.get('foundation_revenue_share', [0])[0], 
            config.get('buyback_and_burn_revenue_share', [0])[0]
        ]
        revenue_sum = sum(revenue_shares)
        if abs(revenue_sum - 1.0) > 0.05:  # Allow 5% tolerance
            issues.append(f"Revenue shares sum to {revenue_sum:.2f}, not 1.0")
        
        # Check APR threshold is reasonable
        apr_threshold = config.get('apr_threshold', [0])[0]
        if apr_threshold < 5 or apr_threshold > 100:
            issues.append(f"APR threshold {apr_threshold}% seems unrealistic")
        
        # Check node setup cost is reasonable
        node_setup_cost = config.get('node_setup_cost', [0])[0]
        if node_setup_cost < 100 or node_setup_cost > 50000:
            issues.append(f"Node setup cost ${node_setup_cost:,.0f} seems unrealistic")
        
        # Check foundation burn rate vs reserves
        burn_rate = config.get('foundation_cash_burn_rate', [0])[0]
        # Note: initial_foundation_cash_reserves might be in initial_values
        
        # Check emission policy settings
        emission_policy = config.get('emission_policy', [''])[0]
        if emission_policy not in ['linear', 'per_device', 'bme']:
            issues.append(f"Unknown emission policy: {emission_policy}")
        
        return {
            'name': name,
            'description': description,
            'config_path': str(config_path),
            'emission_policy': emission_policy,
            'apr_threshold': apr_threshold,
            'node_setup_cost': node_setup_cost,
            'revenue_sum': revenue_sum,
            'issues': issues,
            'loadable': True
        }
        
    except Exception as e:
        return {
            'name': config_path.stem,
            'config_path': str(config_path),
            'issues': [f"Failed to load: {str(e)}"],
            'loadable': False
        }

def audit_all_configs():
    """Audit all configuration files"""
    base_path = Path(__file__).parent / 'config'
    
    results = {
        'production': [],
        'research': [],
        'templates': []
    }
    
    for category in ['production', 'research', 'templates']:
        config_dir = base_path / category
        if not config_dir.exists():
            continue
            
        for config_file in config_dir.glob('*.json'):
            result = test_config(config_file)
            result['category'] = category
            results[category].append(result)
    
    return results

def print_audit_report(results):
    """Print detailed audit report"""
    print("=" * 60)
    print("🔍 DePIN SIMULATOR CONFIGURATION AUDIT REPORT")
    print("=" * 60)
    
    total_configs = sum(len(configs) for configs in results.values())
    loadable_configs = sum(1 for category_configs in results.values() 
                          for config in category_configs if config['loadable'])
    
    print(f"📊 Total Configurations: {total_configs}")
    print(f"✅ Loadable: {loadable_configs}")
    print(f"❌ Broken: {total_configs - loadable_configs}")
    print()
    
    # Detailed breakdown by category
    for category, configs in results.items():
        if not configs:
            continue
            
        print(f"📁 {category.upper()} CONFIGURATIONS:")
        print("-" * 40)
        
        for config in configs:
            status = "✅" if config['loadable'] and not config.get('issues', []) else "⚠️" if config['loadable'] else "❌"
            
            print(f"{status} {config['name']}")
            
            if config['loadable']:
                print(f"   📝 {config.get('description', 'No description')[:80]}...")
                print(f"   🎯 APR Target: {config.get('apr_threshold', '?')}%")
                print(f"   🪙 Emission: {config.get('emission_policy', '?')}")
                print(f"   💰 Node Cost: ${config.get('node_setup_cost', 0):,.0f}")
                
                if config.get('issues'):
                    for issue in config['issues']:
                        print(f"   ⚠️  {issue}")
            else:
                for issue in config.get('issues', []):
                    print(f"   ❌ {issue}")
            print()
    
    return results

def recommend_configs_to_keep(results):
    """Recommend which configs to keep based on insights and functionality"""
    print("🎯 RECOMMENDATIONS:")
    print("=" * 40)
    
    # Collect all working configs
    working_configs = []
    for category_configs in results.values():
        for config in category_configs:
            if config['loadable'] and not config.get('issues'):
                working_configs.append(config)
    
    # Categorize by emission policy and economic focus
    emission_policies = {}
    for config in working_configs:
        policy = config.get('emission_policy', 'unknown')
        if policy not in emission_policies:
            emission_policies[policy] = []
        emission_policies[policy].append(config)
    
    print("📊 Working Configs by Emission Policy:")
    for policy, configs in emission_policies.items():
        print(f"  {policy}: {len(configs)} configs")
        for config in configs:
            print(f"    - {config['name']}")
    print()
    
    # Recommend final set
    recommended = []
    
    # Try to get one of each emission policy
    for policy in ['linear', 'per_device', 'bme']:
        if policy in emission_policies:
            # Pick the one with most insightful name/description
            best = max(emission_policies[policy], 
                      key=lambda x: len(x.get('description', '')))
            recommended.append(best)
    
    # Add any configs with unique economic insights
    unique_names = ['natural_equilibrium', 'conservative_bootstrap', 'business_apr_test']
    for config in working_configs:
        if any(unique in config['name'].lower() for unique in unique_names):
            if config not in recommended:
                recommended.append(config)
    
    # Limit to 6 configs
    recommended = recommended[:6]
    
    print("🌟 RECOMMENDED CONFIGS TO KEEP:")
    for i, config in enumerate(recommended, 1):
        print(f"{i}. {config['name']} ({config.get('emission_policy', '?')})")
        print(f"   📝 {config.get('description', '')[:60]}...")
    
    print(f"\n🗑️  CONFIGS TO REMOVE: {len(working_configs) - len(recommended)} configs")
    
    return recommended

if __name__ == "__main__":
    print("Starting configuration audit...")
    results = audit_all_configs()
    print_audit_report(results)
    recommended = recommend_configs_to_keep(results)