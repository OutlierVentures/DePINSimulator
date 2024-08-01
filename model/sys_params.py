"""
Model Parameters
"""

initial_values = {
    'initial_foundation_cash_reserves': 2.5e7, # initial cash reserves of the DePIN foundation / $
    'initial_node_change_amount': 0.00, # initial change in node count / nodes
    'token_initial_total_supply': 1e10, # initial total supply of the DePIN token
    'token_initial_valuation': 5e7, # initial valuation of the DePIN token / $
    'liquidity_token_allocation': 0.05, # share of the total token supply allocated to the liquidity pool for the DePIN token
}

sys_params = {
    # DePIN node parameters
    'initial_node_amount': [50000], # initial number of nodes in the DePIN network
    'node_setup_cost': [1000.0], # one-time cost to setup a node. This can be hardware, software, license, etc. costs depending on the DePIN application / $
    'node_resource_provision_cost': [0.000001], # cost to provision one unit of resource by a node per day. Resources can be compute, memory, storage, etc. depending on the DePIN application / $
    'node_resource_provision_rate': [1e6], # daily rate at which resources can be provisioned by a node. Resources can be compute, memory, storage, etc. depending on the DePIN application
    'node_reliability': [0.98], # reliability of a node, which is the probability that the node will be online on the day
    'node_token_stake': [10000], # amount of DePIN tokens that a node operator needs to stake to participate in the DePIN network / tokens
    'node_growth_cap' : [10], # maximum daily growth rate of the number of nodes in the DePIN network / %
    'apr_threshold': [10], # annual percentage yield (APR) threshold that node operators find attractive to participate in the DePIN network / %
    
    # DePIN economic parameters
    'initial_network_resource_demand': [1e10, 1e10], # initial network resource demand in the DePIN network / resource units
    'node_revenue_share': [0.75], # revenue share that the node receives for participating in the DePIN network / -
    'buyback_and_burn_revenue_share': [0.01], # ratio of the revenue that will be used for the buyback and burn mechanism / -
    'foundation_revenue_share': [0.24], # ratio of the revenue that will be kept by the DePIN foundation / -
    'foundation_cash_burn_rate': [25e4], # annual cash burn rate of the DePIN foundation / $
    'resource_unit_price': [0.00000125], # price of one unit of resource in the DePIN network / $
    'network_resource_demand_growth_rate': [0.1], # daily growth rate of the network resource demand / %
    
    # DePIN token parameters
    'incentive_token_allocation': [0.5], # share of the total token supply allocated to the DePIN foundation for incentives
    'seller_token_allocation': [0.35], # share of the total token supply allocated to all token selling parties, such as the investors, advisors, and the team
    'idle_token_allocation': [0.1], # share of the total token supply that is not actively used in the DePIN network
    'seller_token_vesting_duration': [365*3], # duration in days for the seller token vesting schedule
    'incentive_mode': ['fixed_rate','fixed_weighted_rate'],   # mode of token emission from the incentive bucket.
                                                                # It can be 'fixed_rate' or 'fixed_weighted_rate'.
                                                                # Fixed means that the incentives will be emitted at a fixed rate,
                                                                # fixed weighted means that the emissions are predefined,
                                                                # but can be weighted to be higher at the beginning of the simulation
    'incentive_token_vesting_duration': [365*4], # duration in days for the incentive token incentive emissions. Only applicable for 'fixed_rate' and 'fixed_weighted_rate' modes
    'incentive_early_weight_ratio': [0.8], # ratio of the total incentives that will be emitted in the first half of the incentives token emission duration. Only applicable for 'fixed_weighted_rate' mode
    'token_mint_model': ['none'],    # mode of token minting (not implemented yet).
                                        # It can be "none", "mint_fixed_rate", or "mint_fixed_weighted_rate".
                                        # mint_fixed_rate means that the tokens will be minted at a fixed rate,
                                        # mint_fixed_rate_incentive_continuation means that the tokens will be minted at a fixed rate according to the last emission rate of the incentives

    'apr_controller_kp': [2.0], # proportional gain of the APR controller
    'apr_controller_ki': [0.1], # integral gain of the APR controller
    'apr_controller_kd': [0.01], # derivative gain of the APR controller
}