from .policy_functions import *
from .state_update_functions import *

state_update_blocks = [
    {
        'label': 'p_token_liquidity_setup',
        'policies': {
            'p_token_liquidity_setup': p_token_liquidity_setup,
            },
        'variables': {
            'dex_tokens': s_dex_liquidity_tokens,
            'dex_usdc': s_dex_liquidity_usdc,
            'dex_token_price': s_dex_liquidity_token_price
            }
    },
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
            'dex_token_price': s_dex_liquidity_token_price
            }
    },
]