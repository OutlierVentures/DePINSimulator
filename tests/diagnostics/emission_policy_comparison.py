"""
Emission Policy Comparison Test
Compares linear vs per-device emission policies
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from radcad import Model, Simulation, Experiment
from model.state_update_blocks import state_update_blocks
from model.state_variables import initial_state
from model.sys_params import sys_params, initial_values
from model import run

print("🚀 EMISSION POLICY COMPARISON TEST")
print("="*60)
print("Testing linear vs per-device emission strategies")
print()

# Test parameters
TIMESTEPS = 365  # 1 year test
MONTE_CARLO_RUNS = 1

def run_emission_policy_test(emission_policy_name, custom_params):
    """Run simulation with specific emission policy"""
    print(f"🔄 Running {emission_policy_name} emission policy...")
    
    model = Model(
        initial_state=initial_state,
        state_update_blocks=state_update_blocks,
        params=custom_params
    )
    
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)
    experiment = Experiment([simulation])
    result = experiment.run()
    df = pd.DataFrame(result)
    processed_df = run.postprocessing(df)
    
    return processed_df

# Test 1: Linear Emission (baseline)
print("1️⃣ LINEAR EMISSION TEST (Baseline)")
linear_params = sys_params.copy()
linear_params['emission_policy'] = ['linear']

linear_df = run_emission_policy_test("Linear", linear_params)

# Test 2: Per-Device Emission
print("2️⃣ PER-DEVICE EMISSION TEST")
per_device_params = sys_params.copy()
per_device_params['emission_policy'] = ['per_device']

per_device_df = run_emission_policy_test("Per-Device", per_device_params)

print("✅ Both simulations complete!")
print()

# Analysis
print("📊 EMISSION POLICY COMPARISON RESULTS:")
print("-" * 50)

# Basic metrics
linear_final_nodes = linear_df.node_amount.iloc[-1]
linear_initial_nodes = linear_df.node_amount.iloc[1]
linear_node_growth = ((linear_final_nodes / linear_initial_nodes) - 1) * 100

per_device_final_nodes = per_device_df.node_amount.iloc[-1]
per_device_initial_nodes = per_device_df.node_amount.iloc[1]
per_device_node_growth = ((per_device_final_nodes / per_device_initial_nodes) - 1) * 100

print(f"📈 NODE GROWTH COMPARISON:")
print(f"   • Linear Policy:")
print(f"     - Initial: {linear_initial_nodes:,} nodes")
print(f"     - Final: {linear_final_nodes:,} nodes") 
print(f"     - Growth: {linear_node_growth:.1f}%")
print(f"   • Per-Device Policy:")
print(f"     - Initial: {per_device_initial_nodes:,} nodes")
print(f"     - Final: {per_device_final_nodes:,} nodes")
print(f"     - Growth: {per_device_node_growth:.1f}%")

# Emission analysis
linear_total_emitted = linear_df.token_incentives_vested_cum.iloc[-1]
per_device_total_emitted = per_device_df.token_incentives_vested_cum.iloc[-1]

print(f"\n💰 TOKEN EMISSION COMPARISON:")
print(f"   • Linear Policy: {linear_total_emitted:,.0f} tokens emitted")
print(f"   • Per-Device Policy: {per_device_total_emitted:,.0f} tokens emitted")
print(f"   • Difference: {((per_device_total_emitted / linear_total_emitted) - 1) * 100:.1f}% more with per-device")

# APR stability
linear_apr_std = linear_df.node_apr.std()
per_device_apr_std = per_device_df.node_apr.std()
linear_avg_apr = linear_df.node_apr.mean()
per_device_avg_apr = per_device_df.node_apr.mean()

print(f"\n🎯 APR PERFORMANCE:")
print(f"   • Linear Policy: {linear_avg_apr:.1f}% avg APR (±{linear_apr_std:.2f}% volatility)")
print(f"   • Per-Device Policy: {per_device_avg_apr:.1f}% avg APR (±{per_device_apr_std:.2f}% volatility)")

# Token price impact
linear_token_price_change = ((linear_df.dex_token_price.iloc[-1] / linear_df.dex_token_price.iloc[1]) - 1) * 100
per_device_token_price_change = ((per_device_df.dex_token_price.iloc[-1] / per_device_df.dex_token_price.iloc[1]) - 1) * 100

print(f"\n💎 TOKEN PRICE IMPACT:")
print(f"   • Linear Policy: {linear_token_price_change:.1f}% price change")
print(f"   • Per-Device Policy: {per_device_token_price_change:.1f}% price change")

# Utilization
linear_avg_util = linear_df.network_resource_demand_supply_ratio.mean() * 100
per_device_avg_util = per_device_df.network_resource_demand_supply_ratio.mean() * 100

print(f"\n📊 NETWORK UTILIZATION:")
print(f"   • Linear Policy: {linear_avg_util:.1f}% average utilization")
print(f"   • Per-Device Policy: {per_device_avg_util:.1f}% average utilization")

# Conclusion
print(f"\n🏆 POLICY COMPARISON SUMMARY:")
print("-" * 50)

if per_device_node_growth > linear_node_growth:
    print(f"   ✅ Per-device policy drives higher node growth (+{per_device_node_growth - linear_node_growth:.1f}%)")
else:
    print(f"   ⚠️  Linear policy maintains steadier growth (+{linear_node_growth - per_device_node_growth:.1f}%)")

if per_device_apr_std < linear_apr_std:
    print(f"   ✅ Per-device policy has more stable APR (±{per_device_apr_std:.2f}% vs ±{linear_apr_std:.2f}%)")
else:
    print(f"   ⚠️  Linear policy has more stable APR (±{linear_apr_std:.2f}% vs ±{per_device_apr_std:.2f}%)")

if abs(per_device_token_price_change) < abs(linear_token_price_change):
    print(f"   ✅ Per-device policy has less token price impact")
else:
    print(f"   ⚠️  Linear policy has less token price impact")

# Simple visualization
plt.figure(figsize=(15, 10))

# Node growth
plt.subplot(2, 3, 1)
plt.plot(linear_df.timestep, linear_df.node_amount, label='Linear', color='blue')
plt.plot(per_device_df.timestep, per_device_df.node_amount, label='Per-Device', color='orange') 
plt.title('Node Count Over Time')
plt.legend()
plt.grid(True)

# Daily emissions
plt.subplot(2, 3, 2)
plt.plot(linear_df.timestep, linear_df.token_incentives_vested, label='Linear', color='blue')
plt.plot(per_device_df.timestep, per_device_df.token_incentives_vested, label='Per-Device', color='orange')
plt.title('Daily Token Emissions')
plt.legend()
plt.grid(True)

# APR
plt.subplot(2, 3, 3)
plt.plot(linear_df.timestep, linear_df.node_apr, label='Linear', color='blue')
plt.plot(per_device_df.timestep, per_device_df.node_apr, label='Per-Device', color='orange')
plt.title('Node APR Over Time')
plt.legend()
plt.grid(True)

# Token price
plt.subplot(2, 3, 4)
plt.plot(linear_df.timestep, linear_df.dex_token_price, label='Linear', color='blue')
plt.plot(per_device_df.timestep, per_device_df.dex_token_price, label='Per-Device', color='orange')
plt.title('Token Price Over Time')
plt.legend()
plt.grid(True)

# Cumulative emissions  
plt.subplot(2, 3, 5)
plt.plot(linear_df.timestep, linear_df.token_incentives_vested_cum, label='Linear', color='blue')
plt.plot(per_device_df.timestep, per_device_df.token_incentives_vested_cum, label='Per-Device', color='orange')
plt.title('Cumulative Token Emissions')
plt.legend()
plt.grid(True)

# Utilization
plt.subplot(2, 3, 6)
plt.plot(linear_df.timestep, linear_df.network_resource_demand_supply_ratio * 100, label='Linear', color='blue')
plt.plot(per_device_df.timestep, per_device_df.network_resource_demand_supply_ratio * 100, label='Per-Device', color='orange')
plt.title('Network Utilization (%)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('tests/diagnostics/emission_policy_comparison.png', dpi=150, bbox_inches='tight')
print(f"\n📊 Comparison chart saved as 'tests/diagnostics/emission_policy_comparison.png'")

print("\n" + "="*60)
print("🎯 Next step: Use cost function framework to objectively rank policies!") 