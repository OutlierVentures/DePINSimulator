import numpy as np
import sys
from .utils import *

def p_network_demand(params, substep, state_history, prev_state, **kwargs):
    # calculate the network resource demand for the next day with saturation when approaching capacity
    
    # Get base growth rate and current utilization
    base_growth_rate = params['network_resource_demand_growth_rate'] / 100
    current_utilization = prev_state.get('network_resource_demand_supply_ratio', 0)
    
    # Apply demand saturation when near capacity (Volt Capital approach)
    if current_utilization >= 0.95:
        # Quadratic slowdown to prevent infinite accumulation
        saturation_factor = (0.95 / max(current_utilization, 0.95)) ** 2
        adjusted_growth_rate = base_growth_rate * saturation_factor
    else:
        adjusted_growth_rate = base_growth_rate
    
    # Calculate new demand with adjusted growth rate
    if prev_state['network_resource_demand'] != 0:
        network_resource_demand = (1 + adjusted_growth_rate) * prev_state['network_resource_demand']
    else:
        network_resource_demand = params['initial_network_resource_demand']
    
    # REMOVED: Faulty supply-demand balancing logic
    # The original logic was backwards and creating economic unrealism
    # Supply-demand balancing should happen in revenue calculations, not demand generation
    
    return {'network_resource_demand': network_resource_demand}

def p_token_vesting(params, substep, state_history, prev_state, **kwargs):
    # calculate the token vesting for the next day
    
    # parameters
    incentive_mode = params['incentive_mode']
    emission_policy = params['emission_policy']
    token_initial_total_supply = state_history[0][-1]['token_total_supply']
    liquidity_token_allocation = state_history[0][-1]['dex_tokens']
    incentive_token_allocation = params['incentive_token_allocation'] * token_initial_total_supply
    seller_token_allocation = params['seller_token_allocation'] * token_initial_total_supply
    idle_token_allocation = params['idle_token_allocation'] * token_initial_total_supply
    seller_token_vesting_duration = params['seller_token_vesting_duration']
    incentive_token_vesting_duration = params['incentive_token_vesting_duration']
    incentive_early_weight_ratio = params['incentive_early_weight_ratio']
    initial_node_amount = params['initial_node_amount']
    node_token_stake = params['node_token_stake']
    assert seller_token_allocation >= initial_node_amount * node_token_stake, f"seller token allocation must be greater than the initial node amount times the node token stake. Current values are seller_token_allocation:{seller_token_allocation} vs. initial_node_amount x node_token_stake = {initial_node_amount*node_token_stake} with initial_node_amount:{initial_node_amount}, node_token_stake:{node_token_stake}"
    seller_token_allocation -= initial_node_amount * node_token_stake # remove the tokens staked by the nodes from the seller allocation
    
    # ensure consistency of token initial allocations
    assert incentive_token_allocation + seller_token_allocation + initial_node_amount * node_token_stake + idle_token_allocation + liquidity_token_allocation == token_initial_total_supply, f"token allocations must add up to a share of {token_initial_total_supply}. Current sum is {incentive_token_allocation + seller_token_allocation + liquidity_token_allocation} with values incentive_token_allocation:{incentive_token_allocation}, seller_token_allocation:{seller_token_allocation}, liquidity_token_allocation:{liquidity_token_allocation}"
    
    # state variables
    token_incentives_vested = prev_state['token_incentives_vested']
    token_incentives_vested_cum = prev_state['token_incentives_vested_cum']
    token_seller_vested = prev_state['token_seller_vested']
    token_seller_vested_cum = prev_state['token_seller_vested_cum']

    # policy logic for incentive emissions
    if emission_policy == 'per_device':
        # Per-device emission: scale with active node count
        active_nodes = prev_state['node_amount'] if prev_state['timestep'] > 1 else initial_node_amount
        emission_per_device = params['emission_per_device_daily']
        emission_cap = params['emission_device_cap_daily']
        
        # Calculate device-based emission with optional cap
        device_based_emission = active_nodes * emission_per_device
        
        # Apply cap if enabled, otherwise only budget-limited
        if params['emission_cap_enabled']:
            capped_emission = min(device_based_emission, emission_cap)
            emission_cap_utilization = (device_based_emission / emission_cap * 100) if emission_cap > 0 else 0
        else:
            capped_emission = device_based_emission  # Only budget-limited
            emission_cap_utilization = 0  # N/A when cap disabled
        
        # Ensure we don't exceed total incentive allocation
        remaining_incentive_budget = incentive_token_allocation - token_incentives_vested_cum
        token_incentives_vested = min(capped_emission, remaining_incentive_budget) if remaining_incentive_budget > 0 else 0
        token_incentives_vested_cum += token_incentives_vested
        
    elif emission_policy == 'linear':
        # Linear emission: fixed daily emission over vesting period
        emission_cap_utilization = 0  # N/A for linear emission policies
        
        if incentive_mode == 'fixed_rate':
            token_incentives_vested = incentive_token_allocation / incentive_token_vesting_duration if (token_incentives_vested_cum + incentive_token_allocation / incentive_token_vesting_duration) <= incentive_token_allocation else (incentive_token_allocation - token_incentives_vested_cum)
            token_incentives_vested_cum += token_incentives_vested

        elif incentive_mode == 'fixed_weighted_rate':
            token_incentives_vested_increment = (incentive_token_allocation * incentive_early_weight_ratio) / (incentive_token_vesting_duration/2) if prev_state['timestep'] < incentive_token_vesting_duration / 2 else (incentive_token_allocation * (1 - incentive_early_weight_ratio)) / (incentive_token_vesting_duration/2)
            token_incentives_vested = token_incentives_vested_increment if (token_incentives_vested_cum + token_incentives_vested_increment) <= incentive_token_allocation else (incentive_token_allocation - token_incentives_vested_cum)
            token_incentives_vested_cum += token_incentives_vested
            
    elif emission_policy == 'bme':
        # BME emission: usage-driven burn-and-mint equilibrium
        bme_burn_rate_multiplier = params['bme_burn_rate_multiplier']
        bme_mint_rate_multiplier = params['bme_mint_rate_multiplier']
        resource_unit_price = params['resource_unit_price']
        
        # Calculate usage-driven emission based on network activity
        # Use network_sold_resource (from p_network_revenues) for BME calculation
        network_sold_resource = min(prev_state['network_resource_demand'], prev_state['network_resource_provision']) if prev_state['network_resource_provision'] > 0 else 0
        
        # BME logic: burn equivalent = network usage value, mint = burn * multiplier
        burn_equivalent = float(network_sold_resource * resource_unit_price * bme_burn_rate_multiplier)
        bme_emission = float(burn_equivalent * bme_mint_rate_multiplier)
        

        
        # Apply cap if enabled, otherwise only budget-limited
        if params['emission_cap_enabled']:
            emission_cap = params['emission_device_cap_daily']
            capped_emission = min(bme_emission, emission_cap)
            emission_cap_utilization = (bme_emission / emission_cap * 100) if emission_cap > 0 else 0
        else:
            capped_emission = bme_emission  # Only budget-limited
            emission_cap_utilization = 0  # N/A when cap disabled (usage-driven)
        
        # Ensure we don't exceed total incentive allocation
        remaining_incentive_budget = incentive_token_allocation - token_incentives_vested_cum
        token_incentives_vested = float(min(capped_emission, remaining_incentive_budget)) if remaining_incentive_budget > 0 else 0.0
        token_incentives_vested_cum += token_incentives_vested
        

        
    else:
        # Fallback: Default to linear emission for unknown policies
        emission_cap_utilization = 0
        token_incentives_vested = incentive_token_allocation / incentive_token_vesting_duration if (token_incentives_vested_cum + incentive_token_allocation / incentive_token_vesting_duration) <= incentive_token_allocation else (incentive_token_allocation - token_incentives_vested_cum)
        token_incentives_vested_cum += token_incentives_vested

    # seller token vesting (unchanged)
    token_seller_vested = seller_token_allocation / seller_token_vesting_duration if (token_seller_vested_cum + seller_token_allocation / seller_token_vesting_duration) <= seller_token_allocation else (seller_token_allocation - token_seller_vested_cum)
    token_seller_vested_cum += token_seller_vested

    return {"token_incentives_vested": token_incentives_vested, "token_seller_vested": token_seller_vested, "token_incentives_vested_cum": token_incentives_vested_cum, "token_seller_vested_cum": token_seller_vested_cum, "emission_cap_utilization": emission_cap_utilization}

def p_node_changes(params, substep, state_history, prev_state, **kwargs):
    # calculate the changes in the number of nodes for the next day
    
    # parameters
    node_amount = prev_state['node_amount'] if prev_state['node_amount'] != 0 else params['initial_node_amount']
    apr_threshold = params['apr_threshold']
    node_token_stake = params['node_token_stake']
    node_growth_cap = params['node_growth_cap']
    apr_controller_kp = params['apr_controller_kp']
    apr_controller_ki = params['apr_controller_ki']
    apr_controller_kd = params['apr_controller_kd']
    node_reliability = params['node_reliability']

    # state variables
    node_apr = prev_state['node_apr']
    node_apr_error_cum = prev_state['node_apr_error_cum']
    token_staked_supply = prev_state['token_staked_supply']
    dex_tokens = prev_state['dex_tokens']
    dex_usdc = prev_state['dex_usdc']
    dex_token_price_usd = prev_state['dex_token_price']
    node_apr_m1 = state_history[-2][-1]['node_apr'] if len(state_history) > 2 else 0
    network_resource_demand = prev_state['network_resource_demand']
    network_resource_provision = prev_state['network_resource_provision']

    # policy logic
    # change amount of nodes based on APR controller
    node_apr_error = (node_apr - apr_threshold)**2 * np.sign(node_apr - apr_threshold) if prev_state['timestep'] > 1 else 0
    integral_correction = np.min([apr_threshold / np.abs(node_apr - apr_threshold)**4, 1]) # scale the impact of the discrete integrator part down in case of big errors
    node_apr_error_cum += node_apr_error * integral_correction
    node_apr_previous_error = (node_apr_m1/apr_threshold-1)**2 * np.sign(node_apr_m1/apr_threshold-1) if len(state_history) > 2 else 0
    node_change_signal = get_pid_controller_signal(apr_controller_kp, apr_controller_ki, apr_controller_kd, error=node_apr_error, integral=node_apr_error_cum, previous_error=node_apr_previous_error, dt=1)
    node_change_amount = np.min([np.abs(node_change_signal), node_amount*(node_growth_cap/100)]) * np.sign(node_change_signal)
    

    # ensure boundary conditions are held, such as
        # 0. there can't be less than one node
        # 1. there can't be more nodes that there is demand for the delivered resources (disabled at the moment)
        # 2. there can not be bought and staked more tokens than there are in the LP
        # 3. there can not be remove more tokens from the stake than there are staked
    # node minimum amount
    new_node_amount = np.max([int(node_amount + node_change_amount), 1])
    # node maximum amount w.r.t. resource demand
    #new_node_amount = np.min([int(network_resource_demand / (node_reliability * params['node_resource_provision_rate'])), new_node_amount])
    # update tokens staked
    token_staked_supply_new = np.multiply(new_node_amount, node_token_stake, dtype=object)
    # prevent the buy of tokens off the market for the initial nodes as we assume the purchased the tokens beforehand
    stake_diff = token_staked_supply_new - token_staked_supply if prev_state['timestep'] > 1 else 0
    # check if enough tokens are in the LP and change stake_diff and token_staked_supply_new accordingly
    if stake_diff > 0:
        stake_diff = np.min([stake_diff, int(dex_tokens/node_token_stake)*node_token_stake])
    else:
        stake_diff = np.max([stake_diff, -token_staked_supply])
    token_staked_supply_new = token_staked_supply + stake_diff if prev_state['timestep'] > 1 else np.multiply(new_node_amount, node_token_stake, dtype=object)

    # change the node amount accordingly
    new_node_amount = int(token_staked_supply_new / node_token_stake)
    node_change_amount_applied = new_node_amount - node_amount
    # update DEX liquidity as tokens need to be bought or sold
    delta_dex_tokens = -stake_diff
    delta_dex_usdc = - (delta_dex_tokens * dex_usdc) / (dex_tokens + delta_dex_tokens) if dex_tokens + delta_dex_tokens > 0 else 0
    dex_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    return {"node_amount": new_node_amount, "node_change_amount": node_change_amount_applied,
            "token_staked_supply": token_staked_supply_new, "dex_tokens": new_dex_tokens,
            "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price,
            "node_apr_error_cum": node_apr_error_cum}

def p_network_utilization(params, substep, state_history, prev_state, **kwargs):
    # calculate the network resource utilization for the next day
    
    # parameters
    node_amount = prev_state['node_amount'] if prev_state['timestep'] > 1 else params['initial_node_amount']
    node_resource_provision_rate = params['node_resource_provision_rate']
    node_reliability = params['node_reliability']

    # state variables
    network_resource_demand = prev_state['network_resource_demand']

    # policy logic
    ### calculate the actual network resource provision
    network_resource_provision = node_amount * node_resource_provision_rate * node_reliability
    ### calculate the network utilization - cap at 100% (physically impossible to exceed)
    utilization_ratio = network_resource_demand / network_resource_provision if network_resource_provision > 0 else 0
    network_resource_demand_supply_ratio = min(1.0, utilization_ratio)

    return {"network_resource_provision": network_resource_provision, "network_resource_demand_supply_ratio": network_resource_demand_supply_ratio}

def p_network_revenues(params, substep, state_history, prev_state, **kwargs):
    # calculate the revenue, expenditures, and profits of the network for the next day
    
    # parameters
    resource_unit_price = params['resource_unit_price']
    node_revenue_share = params['node_revenue_share']
    buyback_and_burn_revenue_share = params['buyback_and_burn_revenue_share']
    foundation_revenue_share = params['foundation_revenue_share']
    assert node_revenue_share + buyback_and_burn_revenue_share + foundation_revenue_share == 1, f"revenue shares must add up to 1. Current sum is {node_revenue_share + buyback_and_burn_revenue_share + foundation_revenue_share} with values node_revenue_share:{node_revenue_share}, buyback_and_burn_revenue_share:{buyback_and_burn_revenue_share}, foundation_revenue_share:{foundation_revenue_share}"

    # state variables
    network_resource_provision = prev_state['network_resource_provision']
    network_resource_demand = prev_state['network_resource_demand']

    # Volt Capital approach: can only sell what network can actually provide
    network_sold_resource = min(network_resource_demand, network_resource_provision)

    # policy logic
    ## network economics
    ### calculate the network revenue shares
    network_revenue = network_sold_resource * resource_unit_price
    buyback_and_burn_revenue = network_revenue * buyback_and_burn_revenue_share
    foundation_revenue = network_revenue * foundation_revenue_share
    node_network_revenue = network_revenue * node_revenue_share

    return {"network_revenue": network_revenue, "buyback_and_burn_revenue": buyback_and_burn_revenue,
            "foundation_revenue": foundation_revenue, "node_network_revenue": node_network_revenue}

def p_node_economics(params, substep, state_history, prev_state, **kwargs):
    # calculate the revenue, expenditures, and profits of the network for the next day
    
    # parameters
    node_resource_provision_cost = params['node_resource_provision_cost']
    node_setup_cost = params['node_setup_cost']
    node_token_stake = params['node_token_stake']

    # state variables
    token_staked_supply = prev_state['token_staked_supply']
    node_amount = prev_state['node_amount']
    network_resource_provision = prev_state['network_resource_provision']
    token_incentives_vested = prev_state['token_incentives_vested']
    dex_tokens = prev_state['dex_tokens']
    dex_usdc = prev_state['dex_usdc']
    dex_token_price_usd = prev_state['dex_token_price']

    # policy logic
    ## node economics
    ### calculate the network revenue shares
    node_network_revenue = prev_state['node_network_revenue']
    node_expenditures = network_resource_provision * node_resource_provision_cost
    ### calculate the node revenue from incentivized token sales
    #### update DEX liquidity as tokens need to be bought or sold
    delta_dex_tokens = token_incentives_vested
    delta_dex_usdc = - (delta_dex_tokens * dex_usdc) / (dex_tokens + delta_dex_tokens) if dex_usdc - (delta_dex_tokens * dex_usdc) / (dex_tokens + delta_dex_tokens) > 0 else 0
    if dex_usdc - (delta_dex_tokens * dex_usdc) / (dex_tokens + delta_dex_tokens) < 0:
        # don't execute the trade if not enough usdc in the pool
        delta_dex_tokens = 0
        delta_dex_usdc = 0

    dex_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc
    
    node_incentive_revenue = -delta_dex_usdc

    node_profit = node_network_revenue + node_incentive_revenue - node_expenditures
    
    # calculate the APR based on the revenue
    node_base_cost = node_setup_cost + node_token_stake * dex_token_price

    # print node economic variables
    node_apr = ((node_profit/node_amount*365) / node_base_cost) * 100 if token_staked_supply > 0 else 0


    return {"node_profit": node_profit, "node_incentive_revenue": node_incentive_revenue,
            "node_expenditures": node_expenditures, "node_apr": node_apr,
            "dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price}

def p_foundation_economics(params, substep, state_history, prev_state, **kwargs):
    # calculate the revenue, expenditures, and profits of the network for the next day
    
    # parameters
    foundation_cash_burn_rate = params['foundation_cash_burn_rate']

    # state variables
    foundation_revenue = prev_state['foundation_revenue']
    foundation_cash_reserves = prev_state['foundation_cash_reserves']

    # policy logic
    foundation_expenditures = foundation_cash_burn_rate / 365  # Fixed: Daily burn rate, not monthly
    foundation_cash_reserves_new = max(0, foundation_cash_reserves - foundation_expenditures + foundation_revenue)  # Fixed: Prevent negative reserves

    return {"foundation_revenue": foundation_revenue,"foundation_cash_reserves": foundation_cash_reserves_new, "foundation_expenditures": foundation_expenditures}


def p_token_selling(params, substep, state_history, prev_state, **kwargs):
    # let all vested and rewarded tokens be sold
    # parameters

    # state variables
    token_seller_vested = prev_state['token_seller_vested']
    dex_tokens = prev_state['dex_tokens']
    dex_usdc = prev_state['dex_usdc']
    dex_token_price_usd = prev_state['dex_token_price']

    # policy logic
    ## node economics
    ### calculate the token selling by the seller stakeholders
    #### update DEX liquidity as tokens need to be bought or sold
    delta_dex_tokens = token_seller_vested
    delta_dex_usdc = - (delta_dex_tokens * dex_usdc) / (dex_tokens + delta_dex_tokens) if dex_tokens + delta_dex_tokens > 0 else 0
    dex_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    return {"dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price}

def p_buyback_and_burn(params, substep, state_history, prev_state, **kwargs):
    # buyback and burn tokens from the buyback and burn revenue share
    # state variables
    dex_tokens = prev_state['dex_tokens']
    dex_usdc = prev_state['dex_usdc']
    dex_token_price_usd = prev_state['dex_token_price']
    token_burned_supply_cum = prev_state['token_burned_supply_cum']
    buyback_and_burn_revenue = prev_state['buyback_and_burn_revenue']

    # policy logic
    #### update DEX liquidity as tokens need to be bought or sold
    delta_dex_usdc = buyback_and_burn_revenue
    delta_dex_tokens = - (delta_dex_usdc * dex_tokens) / (dex_usdc + delta_dex_usdc) if dex_usdc + delta_dex_usdc > 0 else 0
    dex_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    token_burned_supply = -delta_dex_tokens
    token_burned_supply_cum_new = token_burned_supply_cum + token_burned_supply

    return {"dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price, "token_burned_supply": token_burned_supply, "token_burned_supply_cum": token_burned_supply_cum_new}

def p_ecosystem_metrics(params, substep, state_history, prev_state, **kwargs):
    # calculate the circulating supply and total supply of the token

    # parameters
    token_initial_total_supply = state_history[0][-1]['token_total_supply']
    liquidity_token_allocation = state_history[0][-1]['dex_tokens']
    idle_token_allocation = params['idle_token_allocation'] * token_initial_total_supply
    incentive_token_allocation = params['incentive_token_allocation'] * token_initial_total_supply
    seller_token_allocation = params['seller_token_allocation'] * token_initial_total_supply

    # state variables
    dex_tokens = prev_state['dex_tokens']
    token_staked_supply = prev_state['token_staked_supply']
    token_burned_supply_cum = prev_state['token_burned_supply_cum']
    token_minted_supply_cum = prev_state['token_minted_supply_cum']

    # policy logic
    token_total_supply = seller_token_allocation + incentive_token_allocation + idle_token_allocation + liquidity_token_allocation - token_burned_supply_cum + token_minted_supply_cum
    token_circulating_supply = dex_tokens + token_staked_supply + idle_token_allocation

    return {"token_total_supply": token_total_supply, "token_circulating_supply": token_circulating_supply}


def p_calculate_step_cost(params, substep, state_history, prev_state, **kwargs):
    """
    Calculate cost function at each timestep for policy evaluation
    Based on optimal control theory framework
    """
    from .cost_functions import calculate_step_cost
    
    # Get previous state for price volatility calculation
    previous_state = None
    if len(state_history) >= 2:
        previous_state = state_history[-2][-1]  # Get the state dict from previous timestep
    
    # Calculate step cost using the cost function framework
    cost_data = calculate_step_cost(prev_state, previous_state)
    
    return {'step_cost_data': cost_data}
                                             
