"""
Configuration Loader for DePIN Simulator
========================================

Utility script to easily load and apply different configuration templates.
Run this script to see available configurations or load a specific one.

Usage Examples:
    python config_loader.py                              # List all available configs
    python config_loader.py list                         # List all available configs  
    python config_loader.py show production/conservative_bootstrap  # Show config details
    python config_loader.py apply production/conservative_bootstrap # Apply config and run simulation
"""

import sys
import json
import os
from config import get_config, list_available_configs, print_config_summary

def apply_config_to_sys_params(config_name: str):
    """Apply a configuration to model/sys_params.py"""
    config = get_config(config_name)
    
    # Read current sys_params.py
    sys_params_path = "model/sys_params.py"
    
    print(f"🔄 Applying configuration '{config_name}' to {sys_params_path}")
    
    # Create backup
    backup_path = f"{sys_params_path}.backup"
    with open(sys_params_path, 'r') as f:
        original_content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(original_content)
    print(f"📁 Backup created: {backup_path}")
    
    # Convert JSON booleans to Python booleans
    def json_to_python(obj):
        if isinstance(obj, dict):
            return {k: json_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [json_to_python(v) for v in obj]
        elif obj is True:
            return True
        elif obj is False:
            return False
        else:
            return obj
    
    python_config = json_to_python(config)
    
    # Generate new sys_params content
    new_content = f'''"""
DePIN Simulator Model Parameters - Applied from {config_name}
{config.get('_metadata', {}).get('description', 'Auto-generated configuration')}
"""

# Configuration metadata
CONFIG_INFO = {config.get('_metadata', {})}

# Initial state values for the simulation
initial_values = {{
    # Foundation financial reserves at network launch
    'initial_foundation_cash_reserves': 2.5e7,  # $25M initial cash reserves
    
    # Initial node count change (always zero at start)
    'initial_node_change_amount': 0.00,  # No change on day 1
    
    # Token supply and valuation at launch
    'token_initial_total_supply': 1e10,  # 10B total token supply
    'token_initial_valuation': 5e7,     # $50M initial market cap
    
    # DEX liquidity allocation (5% of supply for price discovery)
    'liquidity_token_allocation': 0.05,  # 500M tokens in initial liquidity pool
}}

# Main system parameters - loaded from {config_name}
sys_params = {repr(python_config)}

# Parameter validation and constraints
def validate_params():
    """Validate that parameters meet economic constraints"""
    
    # Revenue shares must sum to 1.0
    revenue_sum = (sys_params['node_revenue_share'][0] + 
                   sys_params['buyback_and_burn_revenue_share'][0] + 
                   sys_params['foundation_revenue_share'][0])
    assert abs(revenue_sum - 1.0) < 1e-6, f"Revenue shares must sum to 1.0, got {{revenue_sum}}"
    
    # Token allocations must sum to 1.0
    token_sum = (sys_params['incentive_token_allocation'][0] + 
                 sys_params['seller_token_allocation'][0] + 
                 sys_params['idle_token_allocation'][0] + 
                 initial_values['liquidity_token_allocation'])
    assert abs(token_sum - 1.0) < 1e-6, f"Token allocations must sum to 1.0, got {{token_sum}}"
    
    # Economic viability checks
    node_setup = sys_params['node_setup_cost'][0]
    node_stake_value = sys_params['node_token_stake'][0] * (initial_values['token_initial_valuation'] / initial_values['token_initial_total_supply'])
    total_investment = node_setup + node_stake_value
    
    # Rough profitability check (should be validated with full simulation)
    daily_capacity = sys_params['node_resource_provision_rate'][0] * sys_params['node_reliability'][0]
    max_daily_revenue = daily_capacity * sys_params['resource_unit_price'][0] * sys_params['node_revenue_share'][0]
    daily_costs = daily_capacity * sys_params['node_resource_provision_cost'][0]
    max_daily_profit = max_daily_revenue - daily_costs
    
    if max_daily_profit > 0:
        payback_days = total_investment / max_daily_profit
        print(f"✅ Economic validation: Max payback period {{payback_days:.0f}} days")
    else:
        print(f"⚠️  Economic warning: Node economics may be unprofitable")
    
    # Emission policy validation
    emission_policy = sys_params['emission_policy'][0]
    if emission_policy == 'per_device':
        initial_nodes = sys_params['initial_node_amount'][0]
        per_device_rate = sys_params['emission_per_device_daily'][0]
        device_cap = sys_params['emission_device_cap_daily'][0]
        initial_daily_emission = min(initial_nodes * per_device_rate, device_cap)
        total_incentive_tokens = sys_params['incentive_token_allocation'][0] * initial_values['token_initial_total_supply']
        estimated_emission_days = total_incentive_tokens / initial_daily_emission if initial_daily_emission > 0 else float('inf')
        print(f"✅ Per-device emission: {{initial_daily_emission:,.0f}} tokens/day initially, ~{{estimated_emission_days:.0f}} day budget")
    
    return True

# Run validation on import
if __name__ == "__main__":
    validate_params()
    print("✅ All parameter validations passed")
    print(f"📋 Configuration: {config_name}")
    if '_metadata' in config:
        print(f"📝 Description: {{config['_metadata'].get('description', 'N/A')}}")
'''
    
    # Write new sys_params.py
    with open(sys_params_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Configuration applied successfully!")
    print(f"🔄 To restore original: mv {backup_path} {sys_params_path}")
    
    return config

def main():
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'list'):
        # List all configurations
        print("🎯 Available DePIN Simulator Configurations:")
        print("=" * 60)
        
        configs = list_available_configs()
        for config_name in configs:
            try:
                config = get_config(config_name)
                metadata = config.get('_metadata', {})
                print(f"\n📋 {config_name}")
                print(f"   {metadata.get('description', 'No description')}")
                if 'best_for' in metadata:
                    print(f"   🎯 Best for: {metadata['best_for']}")
                
                # Show key parameters
                print(f"   • Initial nodes: {config['initial_node_amount'][0]:,}")
                print(f"   • Incentive allocation: {config['incentive_token_allocation'][0]:.0%}")
                print(f"   • Vesting duration: {config['incentive_token_vesting_duration'][0]/365:.1f} years")
                print(f"   • Emission policy: {config['emission_policy'][0]}")
                print(f"   • Target APR: {config['apr_threshold'][0]}%")
            except Exception as e:
                print(f"\n❌ Error loading {config_name}: {e}")
        
        print(f"\n📖 Usage:")
        print(f"   python config_loader.py show <config_name>    # Show detailed config")  
        print(f"   python config_loader.py apply <config_name>   # Apply config to sys_params.py")
        
    elif len(sys.argv) == 3 and sys.argv[1] == 'show':
        # Show specific configuration
        config_name = sys.argv[2]
        try:
            print_config_summary(config_name)
            config = get_config(config_name)
            print(f"\n📄 Full Configuration:")
            print(json.dumps(config, indent=2))
        except Exception as e:
            print(f"❌ Error: {e}")
            
    elif len(sys.argv) == 3 and sys.argv[1] == 'apply':
        # Apply configuration
        config_name = sys.argv[2]
        try:
            config = apply_config_to_sys_params(config_name)
            print(f"\n🚀 Ready to run simulation with '{config_name}' configuration!")
            print(f"💻 Run: python DePIN_Simulator.py")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Invalid usage")
        print("Usage: python config_loader.py [list|show|apply] [config_name]")

if __name__ == "__main__":
    main()