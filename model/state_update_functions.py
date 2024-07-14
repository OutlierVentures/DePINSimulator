def s_network_resource_demand(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_network_resource_demand = policy_input['network_resource_demand']
    return ('network_resource_demand', updated_network_resource_demand)

def s_dex_liquidity_tokens(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_dex_tokens = policy_input['dex_tokens']
    return ('dex_tokens', updated_dex_tokens)

def s_dex_liquidity_usdc(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_dex_usdc = policy_input['dex_usdc']
    return ('dex_usdc', updated_dex_usdc)

def s_dex_liquidity_token_price(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_dex_token_price = policy_input['dex_token_price']
    return ('dex_token_price', updated_dex_token_price)

def s_token_incentives_vested(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_incentives_vested = policy_input['token_incentives_vested']
    return ('token_incentives_vested', updated_token_incentives_vested)

def s_token_seller_vested(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_seller_vested = policy_input['token_seller_vested']
    return ('token_seller_vested', updated_token_seller_vested)

def s_token_incentives_vested_cum(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_incentives_vested_cum = policy_input['token_incentives_vested_cum']
    return ('token_incentives_vested_cum', updated_token_incentives_vested_cum)

def s_token_seller_vested_cum(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_seller_vested_cum = policy_input['token_seller_vested_cum']
    return ('token_seller_vested_cum', updated_token_seller_vested_cum)

def s_node_amount(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_node_amount = policy_input['node_amount']
    return ('node_amount', updated_node_amount)

def s_node_resource_provision(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_node_resource_provision = policy_input['node_resource_provision']
    return ('node_resource_provision', updated_node_resource_provision)

def s_node_revenue(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_node_revenue = policy_input['node_revenue']
    return ('node_revenue', updated_node_revenue)

def s_node_expenditures(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_node_expenditures = policy_input['node_expenditures']
    return ('node_expenditures', updated_node_expenditures)

def s_node_apy(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_node_apy = policy_input['node_apy']
    return ('node_apy', updated_node_apy)

def s_node_change_rate(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_node_change_rate = policy_input['node_change_rate']
    return ('node_change_rate', updated_node_change_rate)

def s_foundation_revenue(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_foundation_revenue = policy_input['foundation_revenue']
    return ('foundation_revenue', updated_foundation_revenue)

def s_foundation_expenditures(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_foundation_expenditures = policy_input['foundation_expenditures']
    return ('foundation_expenditures', updated_foundation_expenditures)

def s_foundation_cash_reserves(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_foundation_cash_reserves = policy_input['foundation_cash_reserves']
    return ('foundation_cash_reserves', updated_foundation_cash_reserves)

def s_token_total_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_total_supply = policy_input['token_total_supply']
    return ('token_total_supply', updated_token_total_supply)

def s_token_burned_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_burned_supply = policy_input['token_burned_supply']
    return ('token_burned_supply', updated_token_burned_supply)

def s_token_minted_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_minted_supply = policy_input['token_minted_supply']
    return ('token_minted_supply', updated_token_minted_supply)

def s_token_circulating_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_circulating_supply = policy_input['token_circulating_supply']
    return ('token_circulating_supply', updated_token_circulating_supply)

def s_token_staked_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_token_staked_supply = policy_input['token_staked_supply']
    return ('token_staked_supply', updated_token_staked_supply)
