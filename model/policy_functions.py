import numpy as np

def p_token_liquidity_setup(params, substep, state_history, prev_state, **kwargs):
    # set up the token liquidity for the first day

    if prev_state['dex_token_price'] != 0:
        dex_tokens = prev_state['dex_tokens']
        dex_usdc = prev_state['dex_usdc']
        dex_token_price_usd = prev_state['dex_token_price']
    
    else:
        token_valuation = params['token_initial_valuation']
        token_total_supply = prev_state['token_total_supply'] if prev_state['token_total_supply'] != 0 else params['token_initial_total_supply']
        dex_tokens = params['liquidity_token_allocation'] * token_total_supply
        dex_token_price_usd = token_valuation / token_total_supply
        dex_usdc = dex_token_price_usd * dex_tokens

    return {'dex_tokens': dex_tokens, 'dex_usdc': dex_usdc, 'dex_token_price': dex_token_price_usd}

def p_network_demand(params, substep, state_history, prev_state, **kwargs):
    # calculate the network resource demand for the next day
    
    if prev_state['network_resource_demand'] != 0:
        network_resource_demand =  (1+params['network_resource_demand_growth_rate']/100) * prev_state['network_resource_demand']
    else:
        network_resource_demand = params['initial_network_resource_demand']
    
    return {'network_resource_demand': network_resource_demand}

def p_token_vesting(params, substep, state_history, prev_state, **kwargs):
    # calculate the token vesting for the next day
    
    # parameters
    incentive_mode = params['incentive_mode']
    token_initial_total_supply = params['token_initial_total_supply']
    incentive_token_allocation = params['incentive_token_allocation'] * token_initial_total_supply
    seller_token_allocation = params['seller_token_allocation'] * token_initial_total_supply
    liquidity_token_allocation = params['liquidity_token_allocation'] * token_initial_total_supply
    seller_token_vesting_duration = params['seller_token_vesting_duration']
    incentive_token_vesting_duration = params['incentive_token_vesting_duration']
    
    # ensure consistency of token initial allocations
    assert incentive_token_allocation + seller_token_allocation + liquidity_token_allocation == token_initial_total_supply, f"token allocations must add up to a share of {token_initial_total_supply}. Current sum is {incentive_token_allocation + seller_token_allocation + liquidity_token_allocation} with values incentive_token_allocation:{incentive_token_allocation}, seller_token_allocation:{seller_token_allocation}, liquidity_token_allocation:{liquidity_token_allocation}"
    
    # state variables
    token_incentives_vested = prev_state['token_incentives_vested']
    token_incentives_vested_cum = prev_state['token_incentives_vested_cum']
    token_seller_vested = prev_state['token_seller_vested']
    token_seller_vested_cum = prev_state['token_seller_vested_cum']

    # policy logic
    if incentive_mode == 'fixed_rate':
        token_incentives_vested = incentive_token_allocation / incentive_token_vesting_duration if (token_incentives_vested_cum + incentive_token_allocation / incentive_token_vesting_duration) <= incentive_token_allocation else (incentive_token_allocation - token_incentives_vested_cum)
        token_seller_vested = seller_token_allocation / seller_token_vesting_duration if (token_seller_vested_cum + seller_token_allocation / seller_token_vesting_duration) <= seller_token_allocation else (seller_token_allocation - token_seller_vested_cum)

        token_incentives_vested_cum += token_incentives_vested
        token_seller_vested_cum += token_seller_vested

    return {"token_incentives_vested": token_incentives_vested, "token_seller_vested": token_seller_vested, "token_incentives_vested_cum": token_incentives_vested_cum, "token_seller_vested_cum": token_seller_vested_cum}

def p_node_changes(params, substep, state_history, prev_state, **kwargs):
    # calculate the changes in the number of nodes for the next day
    
    # parameters
    node_amount = prev_state['node_amount'] if prev_state['node_amount'] != 0 else params['initial_node_amount']
    apy_threshold = params['apy_threshold']
    node_token_stake = params['node_token_stake']

    # state variables
    node_apy = prev_state['node_apy'] if prev_state['node_apy'] != 0 else apy_threshold
    token_staked_supply = prev_state['token_staked_supply']
    dex_tokens = prev_state['dex_tokens']
    dex_usdc = prev_state['dex_usdc']
    dex_token_price_usd = prev_state['dex_token_price']

    # policy logic
    # change amount of nodes based on APY
    node_change_rate = node_apy / apy_threshold
    new_node_amount = int(node_amount * node_change_rate)
    new_node_amount = new_node_amount if new_node_amount > 0 else 0

    # update tokens staked
    token_staked_supply_new = new_node_amount * node_token_stake
    stake_diff = token_staked_supply_new - token_staked_supply
    
    # update DEX liquidity as tokens need to be bought or sold
    delta_dex_tokens = -stake_diff
    delta_dex_usdc = - (delta_dex_tokens * dex_usdc) / (dex_tokens + delta_dex_tokens) if dex_tokens + delta_dex_tokens > 0 else 0
    dex_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    return {"node_amount": new_node_amount, "node_change_rate": node_change_rate, "token_staked_supply": token_staked_supply_new, "dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price}

def p_network_revenue(params, substep, state_history, prev_state, **kwargs):
    # calculate the revenue, expenditures, and profits of the network for the next day
    
    # parameters
    node_amount = prev_state['node_amount'] if prev_state['node_amount'] != 0 else params['initial_node_amount']
    apy_threshold = params['apy_threshold']
    node_token_stake = params['node_token_stake']
    node_resource_provision_rate = params['node_resource_provision_rate']
    node_resource_provision_cost = params['node_resource_provision_cost']
    node_reliability = params['node_reliability']
    resource_unit_price = params['resource_unit_price']

    # state variables
    node_apy = prev_state['node_apy'] if prev_state['node_apy'] != 0 else apy_threshold
    token_staked_supply = prev_state['token_staked_supply']
    dex_tokens = prev_state['dex_tokens']
    dex_usdc = prev_state['dex_usdc']
    dex_token_price_usd = prev_state['dex_token_price']
    node_resource_provision = prev_state['node_resource_provision']

    # policy logic
    # change amount of nodes based on APY
    node_change_rate = node_apy / apy_threshold
    new_node_amount = int(node_amount * node_change_rate)
    new_node_amount = new_node_amount if new_node_amount > 0 else 0

    # update tokens staked
    token_staked_supply_new = new_node_amount * node_token_stake
    stake_diff = token_staked_supply_new - token_staked_supply
    
    # update DEX liquidity as tokens need to be bought or sold
    delta_dex_tokens = -stake_diff
    delta_dex_usdc = - (delta_dex_tokens * dex_usdc) / (dex_tokens + delta_dex_tokens) if dex_tokens + delta_dex_tokens > 0 else 0
    dex_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    # update resource provision by nodes
    node_resource_provision = new_node_amount * node_resource_provision_rate * node_reliability
    node_expenditures = node_resource_provision * node_resource_provision_cost
    node_revenue = node_resource_provision * resource_unit_price - node_expenditures

    return {"node_amount": new_node_amount, "node_change_rate": node_change_rate, "token_staked_supply": token_staked_supply_new, "dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price}


def p_token_selling(params, substep, state_history, prev_state, **kwargs):
    # let all vested and rewarded tokens be sold
    pass