import numpy as np
import sys
from typing import Any
from .utils import *


def get_param_scalar(params: dict, key: str, default: Any) -> Any:
    """Return a scalar param value regardless of scalar/list/bool input.

    - If value is a list/tuple/ndarray, return its first element.
    - If value is a scalar (including bool), return it as-is.
    - If key is missing, return the provided default (scalar or first element if list-like).
    """
    if key in params:
        value = params[key]
    else:
        value = default

    # Handle list-like
    if isinstance(value, (list, tuple, np.ndarray)):
        if len(value) == 0:
            # fall back to default
            if isinstance(default, (list, tuple, np.ndarray)) and len(default) > 0:
                return default[0]
            return default
        return value[0]

    # Scalar (including bool)
    return value

def get_current_phase_growth_rate(params, timestep):
    """
    Get growth rate for current timestep based on founder-defined phases
    """
    # Accept raw list-of-dicts or wrapped [list-of-dicts]
    raw_phases = params.get('business_growth_phases', [])
    
    # Handle different data structures from UI vs config files
    phases = []
    if isinstance(raw_phases, list) and len(raw_phases) > 0:
        if isinstance(raw_phases[0], list):
            # Config file format: [[{phase1}, {phase2}]]
            phases = raw_phases[0]
        elif isinstance(raw_phases[0], dict):
            # UI format: [{phase1}, {phase2}]
            phases = raw_phases
    
    # Fallback to empty list if no valid phases found
    if not phases:
        return 0.02  # Default 2% growth rate
    
    cumulative_days = 0
    for phase in phases:
        # Handle both string and dict access
        try:
            if isinstance(phase, dict):
                days = phase['days']
                growth_rate = phase['daily_growth_rate']
            else:
                # Skip if phase is not a proper dict
                continue
                
            cumulative_days += days
            if timestep <= cumulative_days:
                return growth_rate / 100  # Convert to decimal
        except (KeyError, TypeError) as e:
            # Skip malformed phase data
            continue
    
    # If beyond all phases, use the last phase's growth rate
    if phases:
        try:
            last_phase = phases[-1]
            if isinstance(last_phase, dict):
                return last_phase['daily_growth_rate'] / 100
        except (KeyError, TypeError, IndexError):
            pass
    
    # Final fallback
    return 0.02  # Default 2% growth rate

def get_milestone_multiplier(params, timestep):
    """
    Get demand multiplier for current timestep based on founder-defined milestones
    """
    if 'business_demand_milestones' not in params:
        return 1.0
    
    milestones_raw = params.get('business_demand_milestones', [])
    if isinstance(milestones_raw, list) and len(milestones_raw) > 0 and isinstance(milestones_raw[0], list):
        milestones = milestones_raw[0]
    else:
        milestones = milestones_raw
    current_multiplier = 1.0
    
    for milestone in milestones:
        if timestep >= milestone['day']:
            current_multiplier = milestone['multiplier']
    
    return current_multiplier

def p_network_demand(params, substep, state_history, prev_state, **kwargs):
    """
    Calculate network resource demand with founder-defined business growth assumptions
    
    Supports multiple growth scenarios:
    - Linear: Simple percentage growth (legacy)
    - Custom phases: Founder-defined growth phases with milestones
    """
    
    current_timestep = prev_state.get('timestep', 1)
    current_utilization = prev_state.get('network_resource_demand_supply_ratio', 0)
    
    # Get growth scenario type (accept scalar or [value])
    growth_scenario = get_param_scalar(params, 'business_growth_scenario', ['linear'])
    
    if growth_scenario == 'custom_phases' and 'business_growth_phases' in params:
        # Founder-defined phased growth
        growth_rate = get_current_phase_growth_rate(params, current_timestep)
        
        # Apply milestone multipliers
        milestone_multiplier = get_milestone_multiplier(params, current_timestep)
        
    else:
        # Legacy linear growth
        # Accept decimal (e.g., 0.02) or percentage (e.g., 2.0)
        ngr = get_param_scalar(params, 'network_resource_demand_growth_rate', [0.02])
        growth_rate = ngr / 100 if ngr > 1 else ngr
        milestone_multiplier = 1.0
    
    # Apply demand saturation when near capacity (Volt Capital approach)
    if current_utilization >= 0.95:
        # Quadratic slowdown to prevent infinite accumulation
        saturation_factor = (0.95 / max(current_utilization, 0.95)) ** 2
        adjusted_growth_rate = growth_rate * saturation_factor
    else:
        adjusted_growth_rate = growth_rate
    
    # Calculate new demand with adjusted growth rate and milestones
    if prev_state['network_resource_demand'] != 0:
        base_demand = (1 + adjusted_growth_rate) * prev_state['network_resource_demand']
        network_resource_demand = base_demand * milestone_multiplier
    else:
        network_resource_demand = params['initial_network_resource_demand']
    
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
    node_apr = prev_state['node_apr']  # Display APR (business + incentives)
    business_apr = prev_state.get('business_apr', prev_state['node_apr'])  # Business APR for controller
    node_apr_error_cum = prev_state['node_apr_error_cum']
    token_staked_supply = prev_state['token_staked_supply']
    dex_tokens = prev_state['dex_tokens']
    dex_usdc = prev_state['dex_usdc']
    dex_token_price_usd = prev_state['dex_token_price']
    business_apr_m1 = state_history[-2][-1].get('business_apr', state_history[-2][-1]['node_apr']) if len(state_history) > 2 else 0
    network_resource_demand = prev_state['network_resource_demand']
    network_resource_provision = prev_state['network_resource_provision']

    # policy logic
    # change amount of nodes based on business APR controller with stabilization features
    timestep = prev_state['timestep']
    
    # First-step guard: no node growth at t=1 only
    if timestep <= 1:
        node_change_amount = 0
        node_apr_error_cum = 0  # Reset integral on startup
    else:
        # Use business APR for controller decisions (fundamental economics)
        business_apr_error = business_apr - apr_threshold
        
        # Deadband: ±2pp around target (avoid micro-adjustments)
        deadband = 2.0
        if abs(business_apr_error) < deadband:
            business_apr_error = 0
        else:
            business_apr_error = business_apr_error - np.sign(business_apr_error) * deadband
            
        # Hysteresis: require ±2-3pp movement to trigger action
        hysteresis = 2.5
        business_apr_error_prev = business_apr_m1 - apr_threshold
        if abs(business_apr_error) < hysteresis and abs(business_apr_error_prev) < hysteresis:
            business_apr_error = 0
        
        # PID error processing
        business_apr_error_scaled = (business_apr_error**2) * np.sign(business_apr_error)
        integral_correction = np.min([apr_threshold / np.abs(business_apr_error + 1e-6)**2, 1])  # Clamp integral windup
        node_apr_error_cum += business_apr_error_scaled * integral_correction
        
        # Clamp integral to prevent windup
        max_integral = 1000  # Reasonable bound for cumulative error
        node_apr_error_cum = np.clip(node_apr_error_cum, -max_integral, max_integral)
        
        business_apr_previous_error = (business_apr_m1/apr_threshold-1)**2 * np.sign(business_apr_m1/apr_threshold-1) if business_apr_m1 > 0 else 0
        node_change_signal = get_pid_controller_signal(apr_controller_kp, apr_controller_ki, apr_controller_kd, 
                                                     error=business_apr_error_scaled, integral=node_apr_error_cum, 
                                                     previous_error=business_apr_previous_error, dt=1)
        
        # Output rate limit: ±1%/day maximum growth rate
        max_daily_growth_rate = 0.01  # 1% per day
        max_change_rate = node_amount * max_daily_growth_rate
        node_change_signal_limited = np.clip(node_change_signal, -max_change_rate, max_change_rate)
        
        # Apply growth cap as final constraint
        node_change_amount = np.min([np.abs(node_change_signal_limited), node_amount*(node_growth_cap/100)]) * np.sign(node_change_signal_limited)
    

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
    # Calculate fundamental token price (AMM mechanics)
    fundamental_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    
    # Apply token market dynamics multiplier if available
    token_market_multiplier = prev_state.get('token_market_multiplier', 1.0)
    dex_token_price = fundamental_token_price * token_market_multiplier
    
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    return {"node_amount": new_node_amount, "node_change_amount": node_change_amount_applied,
            "token_staked_supply": token_staked_supply_new, "dex_tokens": new_dex_tokens,
            "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price,
            "fundamental_token_price": fundamental_token_price,
            "node_apr_error_cum": node_apr_error_cum}

def p_apr_divergence_warning(params, substep, state_history, prev_state, **kwargs):
    """
    Monitor APR trends and issue warnings when controller fails to maintain target.
    Designed to help founders identify when their parameters lead to unsustainable dynamics.
    """
    
    # Only analyze after controller has had time to work
    timestep = prev_state['timestep']
    if timestep < 15:  # Wait 2 weeks for initial stabilization
        return {"apr_divergence_warning": None}
    
    # Parameters
    apr_threshold = get_param_scalar(params, 'apr_threshold', [30])
    warning_tolerance = get_param_scalar(params, 'apr_divergence_warning_tolerance', [10.0])  # 10% default
    trend_window = get_param_scalar(params, 'apr_trend_analysis_window', [14])  # 2 weeks default
    
    # Get current APR
    current_apr = prev_state['node_apr']
    apr_deviation_percent = abs(current_apr - apr_threshold) / apr_threshold * 100
    
    # Analyze APR trend over recent history
    if len(state_history) >= trend_window:
        recent_aprs = [state_history[i][-1]['node_apr'] for i in range(-trend_window, 0)]
        apr_trend = recent_aprs[-1] - recent_aprs[0]  # APR change over window
        apr_trend_per_day = apr_trend / trend_window
        
        # Check if APR is diverging from target
        if apr_deviation_percent > warning_tolerance:
            # Determine severity based on deviation and trend
            if apr_deviation_percent > 50 and abs(apr_trend_per_day) > 1:
                severity = "CRITICAL"
                message = f"🚨 CRITICAL APR DIVERGENCE: Current {current_apr:.1f}% (target {apr_threshold:.1f}%)"
                recommendations = [
                    f"• IMMEDIATE ACTION REQUIRED: {apr_deviation_percent:.1f}% deviation",
                    f"• APR trending {'UP' if apr_trend > 0 else 'DOWN'} by {abs(apr_trend_per_day):.1f}%/day",
                    "• Consider reducing demand growth rate or emission allocation",
                    "• Enable/strengthen constraint mechanisms (utilization controller, dynamic pricing)",
                    "• Consider no-controller natural equilibrium approach"
                ]
            elif apr_deviation_percent > 25:
                severity = "HIGH"  
                message = f"⚠️  HIGH APR DEVIATION: Current {current_apr:.1f}% (target {apr_threshold:.1f}%)"
                recommendations = [
                    f"• Controller struggling with {apr_deviation_percent:.1f}% deviation",
                    f"• APR trending {'UP' if apr_trend > 0 else 'DOWN'} by {abs(apr_trend_per_day):.1f}%/day",
                    "• Monitor closely - may need parameter adjustments",
                    "• Consider enabling constraint mechanisms if not already active"
                ]
            else:
                severity = "MODERATE"
                message = f"⚠️  MODERATE APR DEVIATION: Current {current_apr:.1f}% (target {apr_threshold:.1f}%)"
                recommendations = [
                    f"• {apr_deviation_percent:.1f}% deviation from target",
                    "• Monitor for continued divergence trends"
                ]
            
            warning_data = {
                "severity": severity,
                "message": message, 
                "recommendations": recommendations,
                "current_apr": current_apr,
                "target_apr": apr_threshold,
                "deviation_percent": apr_deviation_percent,
                "trend_per_day": apr_trend_per_day,
                "timestep": timestep
            }
            
            # Print warning to console for immediate visibility
            if timestep % 7 == 0:  # Weekly warnings to avoid spam
                print(f"\n{message}")
                for rec in recommendations:
                    print(f"  {rec}")
                print()
            
            return {"apr_divergence_warning": warning_data}
    
    return {"apr_divergence_warning": None}

def p_network_utilization(params, substep, state_history, prev_state, **kwargs):
    # calculate the network resource utilization for the next day
    
    # parameters
    node_amount = prev_state['node_amount'] if prev_state['timestep'] > 1 else params['initial_node_amount']
    node_resource_provision_rate = params['node_resource_provision_rate']
    node_reliability = params['node_reliability']
    utilization_controller_enabled = get_param_scalar(params, 'utilization_controller_enabled', [False])
    utilization_target = get_param_scalar(params, 'utilization_target', [0.775])
    utilization_tolerance = get_param_scalar(params, 'utilization_tolerance', [0.1])
    utilization_controller_kp = get_param_scalar(params, 'utilization_controller_kp', [1.0])
    utilization_controller_ki = get_param_scalar(params, 'utilization_controller_ki', [0.05])
    utilization_controller_kd = get_param_scalar(params, 'utilization_controller_kd', [0.01])

    # state variables
    network_resource_demand = prev_state['network_resource_demand']
    utilization_error_cum = prev_state.get('utilization_error_cum', 0)
    
    # Get previous utilization for derivative term
    prev_utilization = 0
    if len(state_history) > 2:
        prev_utilization = state_history[-2][-1].get('network_resource_demand_supply_ratio', 0)

    # policy logic
    ### calculate the actual network resource provision
    base_network_resource_provision = node_amount * node_resource_provision_rate * node_reliability
    
    # Apply utilization-based supply controller if enabled
    if utilization_controller_enabled and prev_state['timestep'] > 1:
        # Calculate current utilization without controller first
        current_utilization = network_resource_demand / base_network_resource_provision if base_network_resource_provision > 0 else 0
        current_utilization = min(1.0, current_utilization)  # Cap at 100%
        
        # Calculate utilization error (target - actual)
        utilization_error = utilization_target - current_utilization
        
        # Only apply controller if outside tolerance band
        if abs(utilization_error) > utilization_tolerance:
            # Update cumulative error for integral term
            utilization_error_cum += utilization_error
            
            # Calculate derivative term
            utilization_error_derivative = current_utilization - prev_utilization
            
            # PID controller signal
            controller_signal = (utilization_controller_kp * utilization_error + 
                               utilization_controller_ki * utilization_error_cum + 
                               utilization_controller_kd * utilization_error_derivative)
            
            # Apply controller signal to adjust provision rate
            # Negative signal (high utilization) = increase provision
            # Positive signal (low utilization) = decrease provision
            provision_adjustment = -controller_signal
            
            # Limit adjustment to prevent extreme changes (max ±20% per timestep)
            max_adjustment = 0.2
            provision_adjustment = np.clip(provision_adjustment, -max_adjustment, max_adjustment)
            
            # Apply adjustment to base provision
            network_resource_provision = base_network_resource_provision * (1 + provision_adjustment)
            
            # Ensure provision doesn't go negative or exceed physical node capacity
            max_theoretical_provision = node_amount * node_resource_provision_rate  # Without reliability factor
            network_resource_provision = np.clip(network_resource_provision, 0, max_theoretical_provision)
        else:
            # Within tolerance - no adjustment needed
            network_resource_provision = base_network_resource_provision
    else:
        # Controller disabled - use base provision
        network_resource_provision = base_network_resource_provision
        utilization_error_cum = 0  # Reset if controller disabled
    
    ### calculate the network utilization - cap at 100% (physically impossible to exceed)
    utilization_ratio = network_resource_demand / network_resource_provision if network_resource_provision > 0 else 0
    network_resource_demand_supply_ratio = min(1.0, utilization_ratio)

    return {
        "network_resource_provision": network_resource_provision, 
        "network_resource_demand_supply_ratio": network_resource_demand_supply_ratio,
        "utilization_error_cum": utilization_error_cum
    }

def p_network_revenues(params, substep, state_history, prev_state, **kwargs):
    # calculate the revenue, expenditures, and profits of the network for the next day
    
    # parameters
    base_resource_unit_price = params['resource_unit_price']
    node_revenue_share = params['node_revenue_share']
    buyback_and_burn_revenue_share = params['buyback_and_burn_revenue_share']
    foundation_revenue_share = params['foundation_revenue_share']
    assert node_revenue_share + buyback_and_burn_revenue_share + foundation_revenue_share == 1, f"revenue shares must add up to 1. Current sum is {node_revenue_share + buyback_and_burn_revenue_share + foundation_revenue_share} with values node_revenue_share:{node_revenue_share}, buyback_and_burn_revenue_share:{buyback_and_burn_revenue_share}, foundation_revenue_share:{foundation_revenue_share}"
    
    # Dynamic pricing parameters
    resource_pricing_model = get_param_scalar(params, 'resource_pricing_model', ['fixed'])
    resource_price_adjustment_enabled = get_param_scalar(params, 'resource_price_adjustment_enabled', [False])
    resource_price_utilization_sensitivity = get_param_scalar(params, 'resource_price_utilization_sensitivity', [0.0])
    resource_price_min_multiplier = get_param_scalar(params, 'resource_price_min_multiplier', [0.5])
    resource_price_max_multiplier = get_param_scalar(params, 'resource_price_max_multiplier', [2.0])

    # state variables
    network_resource_provision = prev_state['network_resource_provision']
    network_resource_demand = prev_state['network_resource_demand']
    current_utilization = prev_state['network_resource_demand_supply_ratio']

    # Volt Capital approach: can only sell what network can actually provide
    network_sold_resource = min(network_resource_demand, network_resource_provision)
    
    # Calculate dynamic resource unit price
    if resource_price_adjustment_enabled and resource_pricing_model == 'utilization_based':
        # Utilization-based pricing: price increases with high utilization
        # Formula: price = base_price * (1 + sensitivity * (utilization - 0.5))
        # At 50% utilization: price = base_price
        # At 100% utilization: price = base_price * (1 + sensitivity * 0.5)
        # At 0% utilization: price = base_price * (1 - sensitivity * 0.5)
        
        utilization_deviation = current_utilization - 0.5  # Deviation from 50% baseline
        price_multiplier = 1 + (resource_price_utilization_sensitivity * utilization_deviation)
        
        # Apply min/max bounds
        price_multiplier = np.clip(price_multiplier, resource_price_min_multiplier, resource_price_max_multiplier)
        
        resource_unit_price = base_resource_unit_price * price_multiplier
    else:
        # Fixed pricing model
        resource_unit_price = base_resource_unit_price
        price_multiplier = 1.0

    # policy logic
    ## network economics
    ### calculate the network revenue shares
    network_revenue = network_sold_resource * resource_unit_price
    buyback_and_burn_revenue = network_revenue * buyback_and_burn_revenue_share
    foundation_revenue = network_revenue * foundation_revenue_share
    node_network_revenue = network_revenue * node_revenue_share

    return {
        "network_revenue": network_revenue, 
        "buyback_and_burn_revenue": buyback_and_burn_revenue,
        "foundation_revenue": foundation_revenue, 
        "node_network_revenue": node_network_revenue,
        "resource_unit_price_current": resource_unit_price,
        "resource_price_multiplier": price_multiplier
    }

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

    # Calculate fundamental token price (AMM mechanics)
    fundamental_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    
    # Apply token market dynamics multiplier if available
    token_market_multiplier = prev_state.get('token_market_multiplier', 1.0)
    dex_token_price = fundamental_token_price * token_market_multiplier
    
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc
    
    node_incentive_revenue = -delta_dex_usdc

    node_profit = node_network_revenue + node_incentive_revenue - node_expenditures
    
    # calculate the APR based on the revenue using FUNDAMENTAL price for business metrics
    # This ensures business economics aren't distorted by token speculation
    node_base_cost = node_setup_cost + node_token_stake * fundamental_token_price

    # Calculate total APR (business + incentives) for display
    node_apr = ((node_profit/node_amount*365) / node_base_cost) * 100 if token_staked_supply > 0 else 0
    
    # Calculate business APR (network revenue only, no token incentives) for controller decisions
    # This represents the fundamental economics that drive real node operator decisions
    business_profit = node_network_revenue - node_expenditures
    business_apr = ((business_profit/node_amount*365) / node_base_cost) * 100 if token_staked_supply > 0 else 0


    return {"node_profit": node_profit, "node_incentive_revenue": node_incentive_revenue,
            "node_expenditures": node_expenditures, "node_apr": node_apr, "business_apr": business_apr,
            "dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price,
            "fundamental_token_price": fundamental_token_price}

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
    # Calculate fundamental token price (AMM mechanics)
    fundamental_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    
    # Apply token market dynamics multiplier if available
    token_market_multiplier = prev_state.get('token_market_multiplier', 1.0)
    dex_token_price = fundamental_token_price * token_market_multiplier
    
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    return {"dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price,
            "fundamental_token_price": fundamental_token_price}

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
    # Calculate fundamental token price (AMM mechanics)
    fundamental_token_price = np.abs(delta_dex_usdc / delta_dex_tokens) if delta_dex_tokens != 0 else dex_token_price_usd
    
    # Apply token market dynamics multiplier if available
    token_market_multiplier = prev_state.get('token_market_multiplier', 1.0)
    dex_token_price = fundamental_token_price * token_market_multiplier
    
    new_dex_tokens = dex_tokens + delta_dex_tokens
    new_dex_usdc = dex_usdc + delta_dex_usdc

    token_burned_supply = -delta_dex_tokens
    token_burned_supply_cum_new = token_burned_supply_cum + token_burned_supply

    return {"dex_tokens": new_dex_tokens, "dex_usdc": new_dex_usdc, "dex_token_price": dex_token_price, 
            "fundamental_token_price": fundamental_token_price,
            "token_burned_supply": token_burned_supply, "token_burned_supply_cum": token_burned_supply_cum_new}

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


def p_token_market_dynamics(params, substep, state_history, prev_state, **kwargs):
    """
    Apply token market dynamics separate from business fundamentals
    
    This function adds speculative market behavior, volatility, and market cycles
    that are independent of the underlying business performance. This separation
    allows founders to validate their business model against pure fundamentals
    while still accounting for token market realities.
    """
    
    # Parameters for token market behavior
    token_market_scenario = get_param_scalar(params, 'token_market_scenario', ['stable'])
    token_market_volatility = get_param_scalar(params, 'token_market_volatility', [0.1])
    token_speculation_factor = get_param_scalar(params, 'token_speculation_factor', [1.0])
    token_market_cycle_period = get_param_scalar(params, 'token_market_cycle_period', [180])  # days
    token_market_cycle_amplitude = get_param_scalar(params, 'token_market_cycle_amplitude', [0.3])
    
    # Current state
    current_timestep = prev_state.get('timestep', 1)
    current_fundamental_price = prev_state.get('dex_token_price', 0)
    
    # Skip market dynamics on first timestep
    if current_timestep <= 1:
        return {
            'token_market_multiplier': 1.0,
            'token_speculation_premium': 0.0
        }
    
    # Calculate market cycle component (sinusoidal)
    cycle_phase = (current_timestep % token_market_cycle_period) / token_market_cycle_period * 2 * np.pi
    cycle_multiplier = 1 + (token_market_cycle_amplitude * np.sin(cycle_phase))
    
    # Generate market volatility (random walk with mean reversion)
    # Use timestep as seed for reproducible "randomness"
    np.random.seed(int(current_timestep * 1000) % 2**32)
    volatility_shock = np.random.normal(0, token_market_volatility * 0.1)  # Daily volatility
    
    # Apply different market scenarios
    if token_market_scenario == 'bull_market':
        # Bull market: upward trend with high volatility
        trend_multiplier = 1 + (current_timestep * 0.001)  # 0.1% daily growth trend
        volatility_multiplier = 1.5  # Higher volatility
    elif token_market_scenario == 'bear_market':
        # Bear market: downward trend with moderate volatility
        trend_multiplier = 1 - (current_timestep * 0.0005)  # 0.05% daily decline trend
        volatility_multiplier = 1.2  # Moderate volatility
    elif token_market_scenario == 'high_volatility':
        # Sideways but highly volatile
        trend_multiplier = 1.0
        volatility_multiplier = 2.0
    elif token_market_scenario == 'moderate_volatility':
        # Moderate volatility with small cycles
        trend_multiplier = 1.0
        volatility_multiplier = 1.3
    else:  # 'stable'
        # Stable market with minimal speculation
        trend_multiplier = 1.0
        volatility_multiplier = 0.5
    
    # Calculate total market multiplier
    # Base multiplier from speculation factor
    base_multiplier = token_speculation_factor
    
    # Apply cycle, trend, and volatility
    total_multiplier = (base_multiplier * 
                       cycle_multiplier * 
                       trend_multiplier * 
                       (1 + volatility_shock * volatility_multiplier))
    
    # Prevent extreme values (clamp between 0.1x and 10x fundamental price)
    total_multiplier = np.clip(total_multiplier, 0.1, 10.0)
    
    # Calculate speculation premium (how much above fundamental value)
    speculation_premium = (total_multiplier - 1.0) * 100  # Percentage
    
    return {
        'token_market_multiplier': total_multiplier,
        'token_speculation_premium': speculation_premium
    }

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
                                             
