"""
Cost Function Framework for DePIN Protocol Optimization
Based on: https://volt.capital/blog/designing-depin-protocols-using-optimal-control-theory

Implements cost function J(x_0, π) to measure policy performance against ideal protocol states.
Lower cost = better policy performance.
"""

import numpy as np
from typing import Dict, Any, List

class DePINProtocolTargets:
    """
    Defines target states for an ideal DePIN protocol
    These represent what we want the protocol to achieve
    """
    
    def __init__(self):
        # Token economics targets
        self.target_price_growth_rate = 0.001  # 0.1% daily growth (sustainable)
        self.target_utilization_rate = 0.85   # 85% network utilization (efficient but not oversupplied)
        self.target_node_apr = 15.0           # 15% APR (attractive for node operators)
        
        # Protocol sustainability targets
        self.min_foundation_runway_days = 730  # 2 years minimum runway
        self.target_token_burn_mint_ratio = 1.0  # Balanced token economics
        
        # Network health targets
        self.min_network_decentralization = 1000  # Minimum viable node count
        self.max_price_volatility = 0.05      # Max 5% daily price swings

class CostWeights:
    """
    Weights for different components of the cost function
    Higher weight = more important for protocol success
    """
    
    def __init__(self):
        # Economic stability (most important)
        self.price_stability_weight = 0.3
        self.utilization_efficiency_weight = 0.25
        
        # Sustainability
        self.foundation_sustainability_weight = 0.2
        self.node_profitability_weight = 0.15
        
        # Network health
        self.decentralization_weight = 0.1
        
        # Ensure weights sum to 1.0
        total = sum([self.price_stability_weight, self.utilization_efficiency_weight,
                    self.foundation_sustainability_weight, self.node_profitability_weight,
                    self.decentralization_weight])
        assert abs(total - 1.0) < 0.001, f"Weights must sum to 1.0, got {total}"


def calculate_price_stability_cost(current_price: float, previous_price: float, 
                                  target_growth_rate: float, max_volatility: float) -> float:
    """
    Measures deviation from stable price growth
    
    Args:
        current_price: Current token price
        previous_price: Previous timestep token price  
        target_growth_rate: Desired daily growth rate
        max_volatility: Maximum acceptable volatility
    
    Returns:
        Cost value (0 = perfect, higher = worse)
    """
    if previous_price <= 0:
        return 0.0
    
    # Calculate actual growth rate
    actual_growth_rate = (current_price - previous_price) / previous_price
    
    # Cost from deviation from target growth
    growth_deviation = abs(actual_growth_rate - target_growth_rate)
    growth_cost = (growth_deviation / target_growth_rate) ** 2
    
    # Cost from excessive volatility
    volatility = abs(actual_growth_rate)
    volatility_cost = max(0, (volatility - max_volatility) / max_volatility) ** 2
    
    return growth_cost + volatility_cost


def calculate_utilization_efficiency_cost(demand_supply_ratio: float, target_utilization: float) -> float:
    """
    Measures deviation from optimal network utilization
    
    Args:
        demand_supply_ratio: Current network demand/supply ratio
        target_utilization: Target utilization rate
    
    Returns:
        Cost value (0 = perfect, higher = worse)
    """
    # Penalize both under-utilization and over-utilization
    deviation = abs(demand_supply_ratio - target_utilization)
    
    # Higher penalty for over-utilization (network can't serve demand)
    if demand_supply_ratio > target_utilization:
        return (deviation / target_utilization) ** 2 * 2  # Double penalty
    else:
        return (deviation / target_utilization) ** 2


def calculate_foundation_sustainability_cost(cash_reserves: float, daily_burn_rate: float, 
                                           min_runway_days: float) -> float:
    """
    Measures foundation financial sustainability
    
    Args:
        cash_reserves: Current foundation cash reserves
        daily_burn_rate: Daily cash burn rate
        min_runway_days: Minimum required runway days
    
    Returns:
        Cost value (0 = sustainable, higher = worse)
    """
    if daily_burn_rate <= 0:
        return 0.0
    
    # Calculate current runway in days
    current_runway = cash_reserves / daily_burn_rate
    
    if current_runway >= min_runway_days:
        return 0.0  # Sustainable
    else:
        # Exponential penalty as runway decreases
        shortage = (min_runway_days - current_runway) / min_runway_days
        return shortage ** 2


def calculate_node_profitability_cost(current_apr: float, target_apr: float) -> float:
    """
    Measures deviation from target node profitability
    
    Args:
        current_apr: Current node APR
        target_apr: Target APR for node operators
    
    Returns:
        Cost value (0 = perfect, higher = worse)
    """
    # Penalize deviation from target APR
    # Higher penalty for too-low APR (nodes leave network)
    deviation = current_apr - target_apr
    
    if deviation < 0:  # Below target
        return (abs(deviation) / target_apr) ** 2 * 2  # Double penalty
    else:  # Above target (expensive but not as critical)
        return (deviation / target_apr) ** 2


def calculate_decentralization_cost(node_count: float, min_nodes: float) -> float:
    """
    Measures network decentralization health
    
    Args:
        node_count: Current number of nodes
        min_nodes: Minimum viable node count
    
    Returns:
        Cost value (0 = well decentralized, higher = worse)
    """
    if node_count >= min_nodes:
        return 0.0  # Sufficient decentralization
    else:
        shortage = (min_nodes - node_count) / min_nodes
        return shortage ** 2


def calculate_step_cost(state: Dict[str, Any], previous_state: Dict[str, Any] = None,
                       targets: DePINProtocolTargets = None, weights: CostWeights = None) -> Dict[str, float]:
    """
    Calculate the step cost for the current state
    This is the main function that evaluates protocol performance
    
    Args:
        state: Current protocol state (radCAD state dict)
        previous_state: Previous timestep state (for price volatility calculation)
        targets: Target protocol states
        weights: Cost function weights
    
    Returns:
        Dictionary with component costs and total cost
    """
    if targets is None:
        targets = DePINProtocolTargets()
    if weights is None:
        weights = CostWeights()
    
    # Extract relevant state variables
    current_price = state.get('dex_token_price', 0)
    previous_price = previous_state.get('dex_token_price', current_price) if previous_state else current_price
    utilization_ratio = state.get('network_resource_demand_supply_ratio', 0)
    foundation_reserves = state.get('foundation_cash_reserves', 0)
    foundation_expenditures = state.get('foundation_expenditures', 0)
    node_apr = state.get('node_apr', 0)
    node_count = state.get('node_amount', 0)
    
    # Calculate component costs
    price_cost = calculate_price_stability_cost(
        current_price, previous_price, 
        targets.target_price_growth_rate, targets.max_price_volatility
    )
    
    utilization_cost = calculate_utilization_efficiency_cost(
        utilization_ratio, targets.target_utilization_rate
    )
    
    foundation_cost = calculate_foundation_sustainability_cost(
        foundation_reserves, foundation_expenditures, targets.min_foundation_runway_days
    )
    
    node_cost = calculate_node_profitability_cost(
        node_apr, targets.target_node_apr
    )
    
    decentralization_cost = calculate_decentralization_cost(
        node_count, targets.min_network_decentralization
    )
    
    # Calculate weighted total cost
    total_cost = (
        price_cost * weights.price_stability_weight +
        utilization_cost * weights.utilization_efficiency_weight +
        foundation_cost * weights.foundation_sustainability_weight +
        node_cost * weights.node_profitability_weight +
        decentralization_cost * weights.decentralization_weight
    )
    
    return {
        'total_cost': total_cost,
        'price_stability_cost': price_cost,
        'utilization_efficiency_cost': utilization_cost,
        'foundation_sustainability_cost': foundation_cost,
        'node_profitability_cost': node_cost,
        'decentralization_cost': decentralization_cost
    }


def calculate_cumulative_cost(cost_history: List[Dict[str, float]]) -> float:
    """
    Calculate J(x_0, π) - the total policy performance over time
    
    Args:
        cost_history: List of step costs over the simulation
    
    Returns:
        Total cumulative cost (lower = better policy)
    """
    return sum(step['total_cost'] for step in cost_history)


# Utility functions for policy comparison
def compare_policies(policy_costs: Dict[str, List[Dict[str, float]]]) -> Dict[str, Any]:
    """
    Compare multiple policies by their cumulative costs
    
    Args:
        policy_costs: Dict mapping policy names to their cost histories
    
    Returns:
        Comparison results with rankings and relative performance
    """
    results = {}
    
    for policy_name, costs in policy_costs.items():
        cumulative = calculate_cumulative_cost(costs)
        avg_step_cost = cumulative / len(costs) if costs else float('inf')
        
        results[policy_name] = {
            'cumulative_cost': cumulative,
            'average_step_cost': avg_step_cost,
            'total_steps': len(costs)
        }
    
    # Rank policies (lower cost = better)
    ranked = sorted(results.items(), key=lambda x: x[1]['cumulative_cost'])
    
    return {
        'policy_performance': results,
        'ranking': [name for name, _ in ranked],
        'best_policy': ranked[0][0] if ranked else None,
        'performance_gap': ranked[-1][1]['cumulative_cost'] - ranked[0][1]['cumulative_cost'] if len(ranked) > 1 else 0
    } 