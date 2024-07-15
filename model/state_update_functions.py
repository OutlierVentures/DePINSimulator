def s_network_resource_demand(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource demand
    updated_network_resource_demand = policy_input['network_resource_demand']
    return ('network_resource_demand', updated_network_resource_demand)

def s_dex_liquidity_tokens(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the liquidity tokens
    updated_dex_tokens = policy_input['dex_tokens']
    return ('dex_tokens', updated_dex_tokens)

def s_dex_liquidity_usdc(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the liquidity usdc
    updated_dex_usdc = policy_input['dex_usdc']
    return ('dex_usdc', updated_dex_usdc)

def s_dex_liquidity_token_price(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the liquidity token price
    updated_dex_token_price = policy_input['dex_token_price']
    return ('dex_token_price', updated_dex_token_price)

def s_token_incentives_vested(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update token incentives vested
    updated_token_incentives_vested = policy_input['token_incentives_vested']
    return ('token_incentives_vested', updated_token_incentives_vested)

def s_token_seller_vested(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update token seller vested
    updated_token_seller_vested = policy_input['token_seller_vested']
    return ('token_seller_vested', updated_token_seller_vested)

def s_token_incentives_vested_cum(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the token incentives vested cumulative
    updated_token_incentives_vested_cum = policy_input['token_incentives_vested_cum']
    return ('token_incentives_vested_cum', updated_token_incentives_vested_cum)

def s_token_seller_vested_cum(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the token seller vested cumulative
    updated_token_seller_vested_cum = policy_input['token_seller_vested_cum']
    return ('token_seller_vested_cum', updated_token_seller_vested_cum)

def s_node_amount(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update node amount
    updated_node_amount = policy_input['node_amount']
    return ('node_amount', updated_node_amount)

def s_node_resource_provision(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the node resource provision
    updated_node_resource_provision = policy_input['node_resource_provision']
    return ('node_resource_provision', updated_node_resource_provision)

def s_node_network_revenue(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the node revenue
    updated_node_revenue = policy_input['node_revenue']
    return ('node_revenue', updated_node_revenue)

def s_node_expenditures(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the node expenditures
    updated_node_expenditures = policy_input['node_expenditures']
    return ('node_expenditures', updated_node_expenditures)

def s_node_apr(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the node apr
    updated_node_apr = policy_input['node_apr']
    return ('node_apr', updated_node_apr)

def s_node_change_amount(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the node change amount
    updated_node_change_amount = policy_input['node_change_amount']
    return ('node_change_amount', updated_node_change_amount)

def s_foundation_revenue(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the foundation revenue
    updated_foundation_revenue = policy_input['foundation_revenue']
    return ('foundation_revenue', updated_foundation_revenue)

def s_foundation_expenditures(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the foundation expenditures
    updated_foundation_expenditures = policy_input['foundation_expenditures']
    return ('foundation_expenditures', updated_foundation_expenditures)

def s_foundation_cash_reserves(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the foundation cash reserves
    updated_foundation_cash_reserves = policy_input['foundation_cash_reserves']
    return ('foundation_cash_reserves', updated_foundation_cash_reserves)

def s_token_total_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the token total supply
    updated_token_total_supply = policy_input['token_total_supply']
    return ('token_total_supply', updated_token_total_supply)

def s_token_burned_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the token burned supply
    updated_token_burned_supply = policy_input['token_burned_supply']
    return ('token_burned_supply', updated_token_burned_supply)

def s_token_minted_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the token minted supply
    updated_token_minted_supply = policy_input['token_minted_supply']
    return ('token_minted_supply', updated_token_minted_supply)

def s_token_circulating_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the token circulating supply
    updated_token_circulating_supply = policy_input['token_circulating_supply']
    return ('token_circulating_supply', updated_token_circulating_supply)

def s_token_staked_supply(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the token staked supply
    updated_token_staked_supply = policy_input['token_staked_supply']
    return ('token_staked_supply', updated_token_staked_supply)

def s_network_resource_provision(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource provision
    updated_network_resource_provision = policy_input['network_resource_provision']
    return ('network_resource_provision', updated_network_resource_provision)

def s_network_resource_provision_max(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network maximum resource provision
    updated_network_resource_provision_max = policy_input['network_resource_provision_max']
    return ('network_resource_provision_max', updated_network_resource_provision_max)

def s_network_resource_utilization(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network resource utilization
    updated_network_resource_utilization = policy_input['network_resource_utilization']
    return ('network_resource_utilization', updated_network_resource_utilization)

def s_network_revenue(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the network revenue
    updated_network_revenue = policy_input['network_revenue']
    return ('network_revenue', updated_network_revenue)

def s_buyback_and_burn_revenue(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the buyback and burn revenue
    updated_buyback_and_burn_revenue = policy_input['buyback_and_burn_revenue']
    return ('buyback_and_burn_revenue', updated_buyback_and_burn_revenue)

def s_node_profit(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the node profit
    updated_node_profit = policy_input['node_profit']
    return ('node_profit', updated_node_profit)

def s_node_incentive_revenue(params, substep, state_history, prev_state, policy_input, **kwargs):
    # update the node incentive revenue
    updated_node_incentive_revenue = policy_input['node_incentive_revenue']
    return ('node_incentive_revenue', updated_node_incentive_revenue)