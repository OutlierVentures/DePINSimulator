"""
DePIN Simulator Model Parameters - Applied from production/realistic_economics
More realistic business APR (~8%) with 15% target, testing business APR controller
"""

# Configuration metadata
CONFIG_INFO = {'name': 'Realistic Economics Test', 'description': 'More realistic business APR (~8%) with 15% target, testing business APR controller', 'best_for': 'Testing controller with realistic early-stage DePIN economics', 'version': '1.0', 'based_on': 'business_apr_test'}

# Initial state values for the simulation
initial_values = {
    # Foundation financial reserves at network launch
    'initial_foundation_cash_reserves': 2.5e7,  # $25M initial cash reserves
    
    # Initial node count change (always zero at start)
    'initial_node_change_amount': 0.00,  # No change on day 1
    
    # Token supply and valuation at launch
    'token_initial_total_supply': 1e10,  # 10B total token supply
    'token_initial_valuation': 5e7,     # $50M initial market cap
    
    # DEX liquidity allocation (5% of supply for price discovery)
    'liquidity_token_allocation': 0.05,  # 500M tokens in initial liquidity pool
}

# Main system parameters - loaded from production/realistic_economics
sys_params = {'_metadata': {'name': 'Realistic Economics Test', 'description': 'More realistic business APR (~8%) with 15% target, testing business APR controller', 'best_for': 'Testing controller with realistic early-stage DePIN economics', 'version': '1.0', 'based_on': 'business_apr_test'}, 'initial_node_amount': [15000], 'node_setup_cost': [1000.0], 'node_resource_provision_cost': [1e-06], 'node_resource_provision_rate': [100000], 'node_reliability': [0.98], 'node_token_stake': [10000], 'node_growth_cap': [3], '_comment_realistic_target': '=== REALISTIC TARGET APR ===', 'apr_threshold': [15], 'apr_controller_kp': [0.5], 'apr_controller_ki': [0.02], 'apr_controller_kd': [0.001], '_comment_reduced_economics': '=== REDUCED BUSINESS REVENUE ===', 'initial_network_resource_demand': [300000000], 'resource_unit_price': [1e-05], '_comment_custom_growth': '=== CUSTOM DEMAND GROWTH PHASES ===', 'network_resource_demand_growth_rate': [0.0005], 'business_growth_phases': [[{'days': 90, 'daily_growth_rate': 0.05, 'description': 'Early launch phase - slow organic growth'}, {'days': 180, 'daily_growth_rate': 0.03, 'description': 'Growth acceleration phase'}, {'days': 365, 'daily_growth_rate': 0.02, 'description': 'Mature network steady growth'}]], 'demand_growth_milestones': [[{'day': 120, 'multiplier': 1.2, 'description': 'Partnership milestone boost'}]], 'node_revenue_share': [0.75], 'buyback_and_burn_revenue_share': [0.01], 'foundation_revenue_share': [0.24], 'foundation_cash_burn_rate': [1000000], '_comment_token_heavy': '=== TOKEN-HEAVY EARLY ECONOMICS ===', 'incentive_token_allocation': [0.08], 'seller_token_allocation': [0.4], 'idle_token_allocation': [0.47], 'seller_token_vesting_duration': [1095], 'incentive_mode': ['fixed_rate'], 'incentive_token_vesting_duration': [1460], 'incentive_early_weight_ratio': [0.8], 'token_mint_model': ['none'], 'emission_policy': ['linear'], 'emission_per_device_daily': [100], 'emission_device_cap_daily': [500000], 'emission_cap_enabled': [True], 'bme_burn_rate_multiplier': [1.0], 'bme_mint_rate_multiplier': [1.0], '_comment_constraints': '=== MARKET CONSTRAINTS ===', 'resource_pricing_model': ['utilization_based'], 'resource_price_utilization_sensitivity': [0.3], 'resource_price_adjustment_enabled': [True], 'resource_price_min_multiplier': [0.7], 'resource_price_max_multiplier': [2.0], 'utilization_controller_enabled': [False], 'utilization_target': [0.8], 'utilization_tolerance': [0.15]}

# Parameter validation and constraints
def validate_params():
    """Validate that parameters meet economic constraints"""
    
    # Revenue shares must sum to 1.0
    revenue_sum = (sys_params['node_revenue_share'][0] + 
                   sys_params['buyback_and_burn_revenue_share'][0] + 
                   sys_params['foundation_revenue_share'][0])
    assert abs(revenue_sum - 1.0) < 1e-6, f"Revenue shares must sum to 1.0, got {revenue_sum}"
    
    # Token allocations must sum to 1.0
    token_sum = (sys_params['incentive_token_allocation'][0] + 
                 sys_params['seller_token_allocation'][0] + 
                 sys_params['idle_token_allocation'][0] + 
                 initial_values['liquidity_token_allocation'])
    assert abs(token_sum - 1.0) < 1e-6, f"Token allocations must sum to 1.0, got {token_sum}"
    
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
        print(f"✅ Economic validation: Max payback period {payback_days:.0f} days")
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
        print(f"✅ Per-device emission: {initial_daily_emission:,.0f} tokens/day initially, ~{estimated_emission_days:.0f} day budget")
    
    return True

# Run validation on import
if __name__ == "__main__":
    validate_params()
    print("✅ All parameter validations passed")
    print(f"📋 Configuration: production/realistic_economics")
    if '_metadata' in config:
        print(f"📝 Description: {config['_metadata'].get('description', 'N/A')}")
