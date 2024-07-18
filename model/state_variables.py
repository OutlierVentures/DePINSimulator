from .sys_params import initial_values


initial_state = {
    # nodes
    'node_amount': 0,
    'node_network_revenue': 0,
    'node_incentive_revenue': 0,
    'node_profit': 0,
    'node_expenditures': 0,
    'node_apr': 0,
    'node_change_amount': initial_values['initial_node_change_amount'],
    
    # network
    'network_resource_demand': 0,
    'network_resource_provision': 0,
    'network_resource_provision_max': 0,
    'network_resource_demand_supply_ratio': 0,
    'network_revenue': 0,
    'buyback_and_burn_revenue': 0,

    
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
    'token_staked_supply': 0,
    'token_incentives_vested': 0,
    'token_incentives_vested_cum': 0,
    'token_seller_vested': 0,
    'token_seller_vested_cum': 0,

    # market making
    'dex_tokens': initial_values['liquidity_token_allocation'] * initial_values['token_initial_total_supply'],
    'dex_usdc': (initial_values['liquidity_token_allocation'] * initial_values['token_initial_total_supply']) * (initial_values['token_initial_valuation'] / initial_values['token_initial_total_supply']),
    'dex_token_price': initial_values['token_initial_valuation'] / initial_values['token_initial_total_supply'],

    # model variables
    'node_apr_error_cum': 0,
}