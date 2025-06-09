import pandas as pd
import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from model.sys_params import sys_params, initial_values
from model.state_variables import initial_state

print("📊 DePIN SIMULATOR: COMPLETE PARAMETER & STATE DOCUMENTATION")
print("="*80)

print("\n🔧 INITIAL VALUES:")
print("-" * 40)
for key, value in initial_values.items():
    if isinstance(value, (int, float)):
        if value >= 1e6:
            print(f"   • {key}: {value:,.0e} ({value:,.0f})")
        else:
            print(f"   • {key}: {value:,.4g}")
    else:
        print(f"   • {key}: {value}")

print("\n🎛️  SYSTEM PARAMETERS:")
print("-" * 40)

# Categorize parameters
categories = {
    "Node Economics": ['initial_node_amount', 'node_setup_cost', 'node_resource_provision_cost', 
                      'node_resource_provision_rate', 'node_reliability', 'node_token_stake', 'node_growth_cap'],
    "APR Control": ['apr_threshold', 'apr_controller_kp', 'apr_controller_ki', 'apr_controller_kd'],
    "Network Economics": ['initial_network_resource_demand', 'resource_unit_price', 'network_resource_demand_growth_rate'],
    "Revenue Sharing": ['node_revenue_share', 'buyback_and_burn_revenue_share', 'foundation_revenue_share', 'foundation_cash_burn_rate'],
    "Token Economics": ['incentive_token_allocation', 'seller_token_allocation', 'idle_token_allocation',
                       'seller_token_vesting_duration', 'incentive_mode', 'incentive_token_vesting_duration',
                       'incentive_early_weight_ratio', 'token_mint_model']
}

for category, params in categories.items():
    print(f"\n{category}:")
    for param in params:
        if param in sys_params:
            values = sys_params[param]
            if isinstance(values, list):
                if len(values) == 1:
                    val = values[0]
                    if isinstance(val, (int, float)):
                        if val >= 1e6:
                            print(f"   • {param}: {val:,.0e} ({val:,.0f})")
                        else:
                            print(f"   • {param}: {val:,.6g}")
                    else:
                        print(f"   • {param}: {val}")
                else:
                    print(f"   • {param}: {values} (multiple scenarios)")
            else:
                print(f"   • {param}: {values}")

print("\n🔄 STATE VARIABLES:")
print("-" * 40)

# Categorize state variables
state_categories = {
    "Node State": ['node_amount', 'node_network_revenue', 'node_incentive_revenue', 'node_profit', 
                   'node_expenditures', 'node_apr', 'node_change_amount', 'node_apr_error_cum'],
    "Network State": ['network_resource_demand', 'network_resource_provision', 'network_resource_provision_max',
                     'network_resource_demand_supply_ratio', 'network_revenue', 'buyback_and_burn_revenue'],
    "Foundation State": ['foundation_revenue', 'foundation_expenditures', 'foundation_cash_reserves'],
    "Token State": ['token_circulating_supply', 'token_total_supply', 'token_burned_supply', 'token_burned_supply_cum',
                   'token_minted_supply', 'token_minted_supply_cum', 'token_staked_supply'],
    "Vesting State": ['token_incentives_vested', 'token_incentives_vested_cum', 'token_seller_vested', 'token_seller_vested_cum'],
    "DEX State": ['dex_tokens', 'dex_usdc', 'dex_token_price'],
    "Cost Function": ['step_cost_data']
}

for category, variables in state_categories.items():
    print(f"\n{category}:")
    for var in variables:
        if var in initial_state:
            val = initial_state[var]
            if isinstance(val, (int, float)):
                if val >= 1e6:
                    print(f"   • {var}: {val:,.0e} (initial: {val:,.0f})")
                elif val == 0:
                    print(f"   • {var}: {val} (initialized to zero)")
                else:
                    print(f"   • {var}: {val:,.6g}")
            else:
                print(f"   • {var}: {val}")

print("\n💰 KEY ECONOMIC RATIOS & CONSTRAINTS:")
print("-" * 40)

# Calculate key ratios
node_count = sys_params['initial_node_amount'][0]
node_stake = sys_params['node_token_stake'][0]
total_initial_stake = node_count * node_stake
total_supply = initial_values['token_initial_total_supply']
node_provision_rate = sys_params['node_resource_provision_rate'][0]
reliability = sys_params['node_reliability'][0]
initial_supply_capacity = node_count * node_provision_rate * reliability
initial_demand = sys_params['initial_network_resource_demand'][0]
demand_growth = sys_params['network_resource_demand_growth_rate'][0]
resource_price = sys_params['resource_unit_price'][0]

print(f"   • Initial Network Capacity: {initial_supply_capacity:,.0e} units/day")
print(f"   • Initial Demand: {initial_demand:,.0e} units/day")
print(f"   • Initial Utilization: {(initial_demand/initial_supply_capacity)*100:.1f}%")
print(f"   • Daily Demand Growth: {demand_growth:.3f}%")
print(f"   • Token Staking Ratio: {(total_initial_stake/total_supply)*100:.1f}% of total supply")
print(f"   • Resource Unit Revenue: ${resource_price:.2e} per unit")
print(f"   • Daily Network Revenue Potential: ${initial_supply_capacity * resource_price:,.0f}")

# Revenue shares validation
node_rev_share = sys_params['node_revenue_share'][0]
burn_share = sys_params['buyback_and_burn_revenue_share'][0]
foundation_share = sys_params['foundation_revenue_share'][0]
total_shares = node_rev_share + burn_share + foundation_share

print(f"\n   Revenue Share Allocation:")
print(f"   • Nodes: {node_rev_share*100:.1f}%")
print(f"   • Buyback & Burn: {burn_share*100:.1f}%") 
print(f"   • Foundation: {foundation_share*100:.1f}%")
print(f"   • Total: {total_shares*100:.1f}% {'✅' if abs(total_shares - 1.0) < 0.001 else '❌'}")

# Token allocation validation
incentive_alloc = sys_params['incentive_token_allocation'][0]
seller_alloc = sys_params['seller_token_allocation'][0]
idle_alloc = sys_params['idle_token_allocation'][0]
liquidity_alloc = initial_values['liquidity_token_allocation']
total_token_alloc = incentive_alloc + seller_alloc + idle_alloc + liquidity_alloc

print(f"\n   Token Allocation:")
print(f"   • Incentives: {incentive_alloc*100:.1f}%")
print(f"   • Sellers: {seller_alloc*100:.1f}%")
print(f"   • Idle: {idle_alloc*100:.1f}%")
print(f"   • Liquidity: {liquidity_alloc*100:.1f}%")
print(f"   • Total: {total_token_alloc*100:.1f}% {'✅' if abs(total_token_alloc - 1.0) < 0.001 else '❌'}")

print("\n⚠️  POTENTIAL RISK FACTORS:")
print("-" * 40)

# Identify potential risks
risks = []

if demand_growth > 0.05:  # >5% daily growth is very aggressive
    risks.append(f"Very high demand growth ({demand_growth:.3f}% daily = {((1+demand_growth/100)**365-1)*100:.0f}% annually)")

apr_threshold = sys_params['apr_threshold'][0]
if apr_threshold > 50:
    risks.append(f"Very high APR threshold ({apr_threshold}%) may be unsustainable")

if initial_demand > initial_supply_capacity:
    risks.append(f"Initial demand exceeds capacity ({(initial_demand/initial_supply_capacity)*100:.0f}% utilization)")

foundation_burn = sys_params['foundation_cash_burn_rate'][0]
foundation_cash = initial_values['initial_foundation_cash_reserves']
runway_months = foundation_cash / (foundation_burn / 12)
if runway_months < 24:
    risks.append(f"Foundation runway only {runway_months:.1f} months without revenue")

if len(risks) > 0:
    for i, risk in enumerate(risks, 1):
        print(f"   {i}. {risk}")
else:
    print("   ✅ No obvious risk factors detected")

print("\n🎯 CRITICAL PARAMETERS FOR NETWORK STABILITY:")
print("-" * 40)
print("   • apr_threshold: Controls node entry/exit behavior")
print("   • node_growth_cap: Limits network expansion rate") 
print("   • network_resource_demand_growth_rate: Drives utilization pressure")
print("   • apr_controller gains (kp, ki, kd): Control system stability")
print("   • node_token_stake: Economic skin in the game")
print("   • revenue shares: Economic incentive alignment")

print("="*80) 