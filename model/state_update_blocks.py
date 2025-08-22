from .policy_functions import *
from .state_update_functions import *

state_update_blocks = [
    {
        'label': 'p_network_demand',
        'policies': {
            'p_network_demand': p_network_demand,
            },
        'variables': {
            'network_resource_demand': s_network_resource_demand
            }
    },
    {
        'label': 'p_token_vesting',
        'policies': {
            'p_token_vesting': p_token_vesting,
            },
        'variables': {
            'token_incentives_vested': s_token_incentives_vested,
            'token_seller_vested': s_token_seller_vested,
            'token_incentives_vested_cum': s_token_incentives_vested_cum,
            'token_seller_vested_cum': s_token_seller_vested_cum,
            'emission_cap_utilization': s_emission_cap_utilization
            }
    },
    {
        'label': 'p_network_utilization',
        'policies': {
            'p_network_utilization': p_network_utilization,
            },
        'variables': {
            'network_resource_provision': s_network_resource_provision,
            'network_resource_demand_supply_ratio': s_network_resource_demand_supply_ratio,
            'utilization_error_cum': s_utilization_error_cum,
            }
    },
    {
        'label': 'p_network_revenues',
        'policies': {
            'p_network_revenues': p_network_revenues,
            },
        'variables': {
            'network_revenue': s_network_revenue,
            'buyback_and_burn_revenue': s_buyback_and_burn_revenue,
            'foundation_revenue': s_foundation_revenue,
            'node_network_revenue': s_node_network_revenue,
            'resource_unit_price_current': s_resource_unit_price_current,
            'resource_price_multiplier': s_resource_price_multiplier,
            }
    },
    {
        'label': 'p_node_economics',
        'policies': {
            'p_node_economics': p_node_economics,
            },
        'variables': {
            'node_profit': s_node_profit,
            'node_incentive_revenue': s_node_incentive_revenue,
            'node_expenditures': s_node_expenditures,
            'node_apr': s_node_apr,
            'business_apr': s_business_apr,
            'dex_tokens': s_dex_liquidity_tokens,
            'dex_usdc': s_dex_liquidity_usdc,
            'dex_token_price': s_dex_liquidity_token_price,
            'fundamental_token_price': s_fundamental_token_price
            }
    },
    {
        'label': 'p_foundation_economics',
        'policies': {
            'p_foundation_economics': p_foundation_economics,
            },
        'variables': {
            'foundation_revenue': s_foundation_revenue,
            'foundation_cash_reserves': s_foundation_cash_reserves,
            'foundation_expenditures': s_foundation_expenditures
            }
    },
    {
        'label': 'p_token_selling',
        'policies': {
            'p_token_selling': p_token_selling,
            },
        'variables': {
            'dex_tokens': s_dex_liquidity_tokens,
            'dex_usdc': s_dex_liquidity_usdc,
            'dex_token_price': s_dex_liquidity_token_price,
            'fundamental_token_price': s_fundamental_token_price
            }
    },
    {
        'label': 'p_buyback_and_burn',
        'policies': {
            'p_buyback_and_burn': p_buyback_and_burn,
            },
        'variables': {
            'dex_tokens': s_dex_liquidity_tokens,
            'dex_usdc': s_dex_liquidity_usdc,
            'dex_token_price': s_dex_liquidity_token_price,
            'fundamental_token_price': s_fundamental_token_price,
            'token_burned_supply': s_token_burned_supply,
            'token_burned_supply_cum': s_token_burned_supply_cum
            }
    },
    {
        'label': 'p_node_changes',
        'policies': {
            'p_node_changes': p_node_changes,
            'p_apr_divergence_warning': p_apr_divergence_warning,
            },
        'variables': {
            'node_amount': s_node_amount,
            'node_change_amount': s_node_change_amount,
            'token_staked_supply': s_token_staked_supply,
            'dex_tokens': s_dex_liquidity_tokens,
            'dex_usdc': s_dex_liquidity_usdc,
            'dex_token_price': s_dex_liquidity_token_price,
            'fundamental_token_price': s_fundamental_token_price,
            'node_apr_error_cum': s_node_apr_error_cum,
            'apr_divergence_warning': s_apr_divergence_warning
            }
    },
    {
        'label': 'p_ecosystem_metrics',
        'policies': {
            'p_ecosystem_metrics': p_ecosystem_metrics,
            },
        'variables': {
            'token_total_supply': s_token_total_supply,
            'token_circulating_supply': s_token_circulating_supply
            }
    },
    {
        'label': 'p_token_market_dynamics',
        'policies': {
            'p_token_market_dynamics': p_token_market_dynamics,
            },
        'variables': {
            'token_market_multiplier': s_token_market_multiplier,
            'token_speculation_premium': s_token_speculation_premium
            }
    },
    {
        'label': 'p_cost_calculation',
        'policies': {
            'p_calculate_step_cost': p_calculate_step_cost,
            },
        'variables': {
            'step_cost_data': s_step_cost_data
            }
    },

]