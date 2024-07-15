from .sys_params import initial_values


initial_state = {
    # nodes
    'node_amount': 0,
    'node_revenue': 0,
    'node_expenditures': 0,
    'node_apr': 0,
    'node_change_amount': initial_values['initial_node_change_amount'],
    
    # network
    'network_resource_demand': 0,
    'network_resource_provision': 0,
    'network_resource_utilization': 0,
    'network_revenue': 0,
    
    # foundation
    'foundation_revenue': 0,
    'foundation_expenditures': 0,
    'foundation_cash_reserves': initial_values['initial_foundation_cash_reserves'],
    
    # token
    'token_circulating_supply': 0,
    'token_total_supply': 0,
    'token_burned_supply': 0,
    'token_burned_supply_cum': 0,
    'token_minted_supply': 0,
    'token_minted_supply_cum': 0,
    'token_staked_supply': 0,
    'token_staked_supply_cum': 0,
    'token_incentives_vested': 0,
    'token_incentives_vested_cum': 0,
    'token_seller_vested': 0,
    'token_seller_vested_cum': 0,

    # market making
    'dex_tokens': 0,
    'dex_usdc': 0,
    'dex_depth': 0,
    'dex_token_price': 0,
}