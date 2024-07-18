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
            'token_seller_vested_cum': s_token_seller_vested_cum
            }
    },
    {
        'label': 'p_node_changes',
        'policies': {
            'p_node_changes': p_node_changes,
            },
        'variables': {
            'node_amount': s_node_amount,
            'node_change_amount': s_node_change_amount,
            'token_staked_supply': s_token_staked_supply,
            'dex_tokens': s_dex_liquidity_tokens,
            'dex_usdc': s_dex_liquidity_usdc,
            'dex_token_price': s_dex_liquidity_token_price,
            'node_apr_error_cum': s_node_apr_error_cum
            }
    },
    {
        'label': 'p_network_utilization',
        'policies': {
            'p_network_utilization': p_network_utilization,
            },
        'variables': {
            'network_resource_provision': s_network_resource_provision,
            'network_resource_provision_max': s_network_resource_provision_max,
            'network_resource_demand_supply_ratio': s_network_resource_demand_supply_ratio,
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
            'dex_tokens': s_dex_liquidity_tokens,
            'dex_usdc': s_dex_liquidity_usdc,
            'dex_token_price': s_dex_liquidity_token_price
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
            'dex_token_price': s_dex_liquidity_token_price
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
            'token_burned_supply': s_token_burned_supply,
            'token_burned_supply_cum': s_token_burned_supply_cum
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

]