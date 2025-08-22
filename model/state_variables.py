from .sys_params import initial_values, sys_params
import warnings


def calculate_expected_initial_apr(params, initial_vals):
    """
    Calculate expected APR at network launch based on initial parameters.
    This provides a realistic starting point instead of 0% APR.
    """
    # Network economics parameters
    initial_demand = params['initial_network_resource_demand'][0]
    node_count = params['initial_node_amount'][0] 
    provision_rate = params['node_resource_provision_rate'][0]
    reliability = params['node_reliability'][0]
    price = params['resource_unit_price'][0]
    node_revenue_share = params['node_revenue_share'][0]
    
    # Token economics parameters  
    incentive_allocation = params['incentive_token_allocation'][0]
    vesting_duration = params['incentive_token_vesting_duration'][0]
    total_supply = initial_vals['token_initial_total_supply']
    total_valuation = initial_vals['token_initial_valuation']
    node_setup_cost = params['node_setup_cost'][0]
    node_token_stake = params['node_token_stake'][0]
    
    # Calculate expected network revenue
    max_provision = node_count * provision_rate * reliability
    sold_resource = min(initial_demand, max_provision)
    network_revenue = sold_resource * price
    node_network_revenue = network_revenue * node_revenue_share
    
    # Calculate expected token incentive revenue
    daily_emissions = (incentive_allocation * total_supply) / vesting_duration
    fundamental_token_price = total_valuation / total_supply
    
    # Simplified assumption: nodes can sell their token allocation at fundamental price
    # (In reality, large sales would impact price, but this gives expected economics)
    node_incentive_revenue = daily_emissions * fundamental_token_price
    
    # Calculate expected daily profit and APR
    # Note: node_expenditures are typically very small (provision costs)
    node_expenditures = sold_resource * params['node_resource_provision_cost'][0]
    node_profit = node_network_revenue + node_incentive_revenue - node_expenditures
    node_base_cost = node_setup_cost + node_token_stake * fundamental_token_price
    
    if node_profit <= 0 or node_base_cost <= 0:
        return 0  # Fallback for edge cases
        
    expected_apr = ((node_profit / node_count * 365) / node_base_cost) * 100
    
    return expected_apr

def calculate_expected_initial_business_apr(params, initial_vals):
    """
    Calculate expected business APR at network launch (network revenue only, no token incentives).
    This represents the fundamental economics that drive real node operator decisions.
    """
    # Network economics parameters
    initial_demand = params['initial_network_resource_demand'][0]
    node_count = params['initial_node_amount'][0] 
    provision_rate = params['node_resource_provision_rate'][0]
    reliability = params['node_reliability'][0]
    price = params['resource_unit_price'][0]
    node_revenue_share = params['node_revenue_share'][0]
    node_setup_cost = params['node_setup_cost'][0]
    node_token_stake = params['node_token_stake'][0]
    
    # Calculate expected network revenue (business only)
    max_provision = node_count * provision_rate * reliability
    sold_resource = min(initial_demand, max_provision)
    network_revenue = sold_resource * price
    node_network_revenue = network_revenue * node_revenue_share
    
    # Calculate business profit (no token incentives)
    node_expenditures = sold_resource * params['node_resource_provision_cost'][0]
    business_profit = node_network_revenue - node_expenditures
    
    # Use fundamental token price for cost basis
    total_supply = initial_vals['token_initial_total_supply']
    total_valuation = initial_vals['token_initial_valuation']
    fundamental_token_price = total_valuation / total_supply
    node_base_cost = node_setup_cost + node_token_stake * fundamental_token_price
    
    if business_profit <= 0 or node_base_cost <= 0:
        return 0  # Fallback for edge cases
        
    expected_business_apr = ((business_profit / node_count * 365) / node_base_cost) * 100
    
    return expected_business_apr


def validate_apr_target_feasibility(params, initial_vals):
    """
    Validate that the APR target is reasonable given the economic parameters.
    Issues warnings for potentially unreasonable target values.
    """
    target_apr = params['apr_threshold'][0]
    expected_apr = calculate_expected_initial_apr(params, initial_vals)
    
    # Calculate deviation from expected economics
    apr_deviation = abs(expected_apr - target_apr)
    deviation_percent = (apr_deviation / max(target_apr, 0.1)) * 100  # Avoid div by zero
    
    # Issue warnings for large deviations
    if deviation_percent > 200:  # Target is 3x+ different from expected
        warnings.warn(
            f"⚠️  SEVERE APR MISMATCH: Target APR ({target_apr:.1f}%) vs Expected ({expected_apr:.1f}%)\n"
            f"    The controller will struggle with this {apr_deviation:.1f}% deviation.\n"
            f"    🔧 SOLUTIONS:\n"
            f"    • REDUCE emission allocation from {params['incentive_token_allocation'][0]*100:.0f}% to ~{max(5, params['incentive_token_allocation'][0]*100 * (target_apr/expected_apr)):.1f}% of token supply\n"
            f"    • Or INCREASE target APR from {target_apr:.0f}% to ~{min(100, expected_apr*.5):.0f}% (more realistic)\n"
            f"    • Or reduce initial demand/revenue parameters",
            UserWarning
        )
    elif deviation_percent > 100:  # Target is 2x+ different from expected  
        warnings.warn(
            f"⚠️  HIGH APR DEVIATION: Target APR ({target_apr:.1f}%) vs Expected ({expected_apr:.1f}%)\n"
            f"    Controller may oscillate with this {apr_deviation:.1f}% difference.\n"
            f"    💡 RECOMMENDATIONS:\n"
            f"    • Monitor early simulation timesteps for stability\n"
            f"    • Consider adjusting target to ~{(expected_apr + target_apr)/2:.0f}% as compromise\n"
            f"    • Or REDUCE emission allocation to ~{max(5, params['incentive_token_allocation'][0]*100 * (target_apr/expected_apr)):.1f}% of token supply",
            UserWarning
        )
    
    # Additional sanity checks
    if target_apr > 200:
        warnings.warn(
            f"APR target ({target_apr:.1f}%) is extremely high and likely unsustainable. "
            f"Consider more realistic targets (15-50%).",
            UserWarning
        )
    elif target_apr < 5:
        warnings.warn(
            f"APR target ({target_apr:.1f}%) is very low and may not attract node operators. "
            f"Consider higher targets (10-25%).",
            UserWarning
        )
    
    return expected_apr


initial_state = {
    # nodes
    'node_amount': sys_params['initial_node_amount'][0],
    'node_network_revenue': 0,
    'node_incentive_revenue': 0,
    'node_profit': 0,
    'node_expenditures': 0,
    'node_apr': calculate_expected_initial_apr(sys_params, initial_values),
    'node_change_amount': initial_values['initial_node_change_amount'],
    
    # network
    'network_resource_demand': sys_params['initial_network_resource_demand'][0],
    'network_resource_provision': 0,
    'network_resource_provision_max': 0,
    'network_resource_demand_supply_ratio': 0,
    'network_revenue': 0,
    'buyback_and_burn_revenue': 0,
    'resource_unit_price_current': initial_values.get('resource_unit_price', 0.00002),
    'resource_price_multiplier': 1.0,

    
    # foundation
    'foundation_revenue': 0,
    'foundation_expenditures': 0,
    'foundation_cash_reserves': initial_values['initial_foundation_cash_reserves'],
    
    # token
    'token_circulating_supply': initial_values['liquidity_token_allocation'],
    'token_total_supply': initial_values['token_initial_total_supply'],
    'token_burned_supply': 0,
    'token_burned_supply_cum': 0,
    'token_minted_supply': 0,
    'token_minted_supply_cum': 0,
    'token_staked_supply': sys_params['initial_node_amount'][0] * sys_params['node_token_stake'][0],
    'token_incentives_vested': 0,
    'token_incentives_vested_cum': 0,
    'token_seller_vested': 0,
    'token_seller_vested_cum': 0,
    'emission_cap_utilization': 0,

    # market making
    'dex_tokens': initial_values['liquidity_token_allocation'] * initial_values['token_initial_total_supply'],
    'dex_usdc': (initial_values['liquidity_token_allocation'] * initial_values['token_initial_total_supply']) * (initial_values['token_initial_valuation'] / initial_values['token_initial_total_supply']),
    'dex_token_price': initial_values['token_initial_valuation'] / initial_values['token_initial_total_supply'],
    'fundamental_token_price': initial_values['token_initial_valuation'] / initial_values['token_initial_total_supply'],
    'token_market_multiplier': 1.0,
    'token_speculation_premium': 0.0,

    # model variables
    'node_apr_error_cum': 0,
    'utilization_error_cum': 0,
    
    # cost function variables
    'step_cost_data': {},
    
    # warning system variables
    'apr_divergence_warning': None,
    
    # business metrics for controller
    'business_apr': calculate_expected_initial_business_apr(sys_params, initial_values),
}