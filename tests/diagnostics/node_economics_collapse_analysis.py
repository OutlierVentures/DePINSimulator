import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from radcad import Model, Simulation, Experiment
from model.state_update_blocks import state_update_blocks
from model.state_variables import initial_state
from model.sys_params import sys_params
from model import run

print("🔍 NODE ECONOMICS COLLAPSE ANALYSIS")
print("="*60)
print("Deep dive into APR controller and node exit behavior")
print()

# Run simulation focused on node economics
TIMESTEPS = 365  # 1 year
MONTE_CARLO_RUNS = 1

print(f"🔄 Running {TIMESTEPS}-day simulation...")

model = Model(
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
    params=sys_params
)

simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)
experiment = Experiment([simulation])
result = experiment.run()
df = pd.DataFrame(result)
rdf = run.postprocessing(df)

print("✅ Simulation complete!")

# Calculate additional metrics for analysis
rdf['supply_capacity'] = rdf.network_resource_provision
rdf['demand_pressure'] = rdf.network_resource_demand / rdf.network_resource_provision
rdf['raw_utilization'] = rdf.network_resource_demand / rdf.network_resource_provision
rdf['node_change_pct'] = rdf.node_amount.pct_change() * 100
rdf['apr_error'] = rdf.node_apr - sys_params['apr_threshold'][0]

print("\n📊 NODE ECONOMICS DEATH SPIRAL ANALYSIS:")
print("-" * 50)

# Find when network starts collapsing
collapse_threshold = 0.9  # 90% of initial nodes
initial_nodes = rdf.node_amount.iloc[1]  # Skip timestep 0
current_nodes = rdf.node_amount.iloc[-1]
collapse_ratio = current_nodes / initial_nodes

print(f"   • Initial Nodes: {initial_nodes:,.0f}")
print(f"   • Final Nodes: {current_nodes:,.0f}")
print(f"   • Node Retention: {collapse_ratio*100:.1f}%")

if collapse_ratio < 0.5:
    print(f"   ❌ SEVERE COLLAPSE: Lost {(1-collapse_ratio)*100:.1f}% of nodes")
elif collapse_ratio < 0.8:
    print(f"   ⚠️  MODERATE COLLAPSE: Lost {(1-collapse_ratio)*100:.1f}% of nodes")
else:
    print(f"   ✅ STABLE: Only lost {(1-collapse_ratio)*100:.1f}% of nodes")

# Find collapse trigger point
node_loss_threshold = 0.95  # When nodes first drop below 95% of initial
collapse_mask = rdf.node_amount < (initial_nodes * node_loss_threshold)
if collapse_mask.any():
    collapse_start = rdf[collapse_mask].timestep.iloc[0]
    print(f"   • Collapse started: Day {collapse_start}")
    
    # Analyze conditions at collapse start
    collapse_state = rdf[rdf.timestep == collapse_start].iloc[0]
    print(f"   • APR at collapse: {collapse_state.node_apr:.1f}%")
    print(f"   • Utilization at collapse: {collapse_state.network_resource_demand_supply_ratio:.3f} ({collapse_state.network_resource_demand_supply_ratio*100:.1f}%)")
    print(f"   • Demand pressure: {collapse_state.demand_pressure:.2f}x")
else:
    print(f"   • No significant collapse detected")

print(f"\n💰 APR CONTROLLER BEHAVIOR ANALYSIS:")
print("-" * 50)

apr_stats = rdf.node_apr.describe()
apr_threshold = sys_params['apr_threshold'][0]

print(f"   • Target APR: {apr_threshold}%")
print(f"   • Average APR: {apr_stats['mean']:.2f}%")
print(f"   • Min APR: {apr_stats['min']:.2f}%")
print(f"   • Max APR: {apr_stats['max']:.2f}%")
print(f"   • APR Volatility (std): {apr_stats['std']:.2f}%")

# APR error analysis
below_threshold = rdf[rdf.node_apr < apr_threshold]
above_threshold = rdf[rdf.node_apr > apr_threshold]

print(f"   • Days below threshold: {len(below_threshold)}/{len(rdf)} ({len(below_threshold)/len(rdf)*100:.1f}%)")
print(f"   • Days above threshold: {len(above_threshold)}/{len(rdf)} ({len(above_threshold)/len(rdf)*100:.1f}%)")

if len(below_threshold) > 0:
    avg_shortfall = (apr_threshold - below_threshold.node_apr).mean()
    print(f"   • Average shortfall when below: {avg_shortfall:.2f} percentage points")

print(f"\n🔧 PID CONTROLLER PERFORMANCE:")
print("-" * 50)

# Analyze PID controller gains
kp = sys_params['apr_controller_kp'][0]
ki = sys_params['apr_controller_ki'][0] 
kd = sys_params['apr_controller_kd'][0]

print(f"   • Proportional Gain (Kp): {kp}")
print(f"   • Integral Gain (Ki): {ki}")
print(f"   • Derivative Gain (Kd): {kd}")

# Calculate stability metrics
apr_oscillation = rdf.node_apr.diff().abs().mean()
node_change_volatility = rdf.node_change_pct.abs().mean()

print(f"   • APR Oscillation: ±{apr_oscillation:.2f}% (average daily change)")
print(f"   • Node Change Volatility: ±{node_change_volatility:.2f}% (average daily change)")

# Check for oscillatory behavior
sign_changes = (rdf.node_change_pct.diff().fillna(0) != 0).sum()
print(f"   • Direction Changes: {sign_changes} times ({sign_changes/len(rdf)*100:.1f}% of days)")

if node_change_volatility > 5:
    print(f"   ⚠️  HIGH VOLATILITY: Node count changes too aggressively")
elif apr_oscillation > 2:
    print(f"   ⚠️  OSCILLATORY: APR control is unstable")
else:
    print(f"   ✅ STABLE: Controller behavior appears reasonable")

print(f"\n⚖️ ECONOMIC PRESSURE ANALYSIS:")
print("-" * 50)

# Revenue vs costs analysis
final_day = rdf.iloc[-1]
revenue_per_node = final_day.node_network_revenue / final_day.node_amount if final_day.node_amount > 0 else 0
costs_per_node = final_day.node_expenditures / final_day.node_amount if final_day.node_amount > 0 else 0
profit_per_node = revenue_per_node - costs_per_node

print(f"   • Revenue per node: ${revenue_per_node:.2f}/day")
print(f"   • Costs per node: ${costs_per_node:.2f}/day")
print(f"   • Profit per node: ${profit_per_node:.2f}/day")

# Node setup economics
node_setup_cost = sys_params['node_setup_cost'][0]
node_stake_value = sys_params['node_token_stake'][0] * final_day.dex_token_price
total_node_investment = node_setup_cost + node_stake_value
payback_days = total_node_investment / profit_per_node if profit_per_node > 0 else float('inf')

print(f"   • Node setup cost: ${node_setup_cost:.0f}")
print(f"   • Node stake value: ${node_stake_value:.0f} ({sys_params['node_token_stake'][0]:,} tokens @ ${final_day.dex_token_price:.4f})")
print(f"   • Total investment: ${total_node_investment:.0f}")

if payback_days < 365:
    print(f"   ✅ Payback time: {payback_days:.1f} days ({payback_days/30:.1f} months)")
elif payback_days < 1000:
    print(f"   ⚠️  Payback time: {payback_days:.1f} days ({payback_days/365:.1f} years)")
else:
    print(f"   ❌ UNPROFITABLE: Payback > 1000 days (profit = ${profit_per_node:.2f})")

print(f"\n📈 DEMAND-SUPPLY DYNAMICS:")
print("-" * 50)

demand_growth_rate = sys_params['network_resource_demand_growth_rate'][0]
actual_demand_growth = (rdf.network_resource_demand.iloc[-1] / rdf.network_resource_demand.iloc[1] - 1) * 100
theoretical_growth = ((1 + demand_growth_rate/100) ** (len(rdf)-1) - 1) * 100

print(f"   • Theoretical demand growth: {theoretical_growth:.1f}% over {len(rdf)} days")
print(f"   • Actual demand growth: {actual_demand_growth:.1f}%")
print(f"   • Growth efficiency: {actual_demand_growth/theoretical_growth*100:.1f}% (saturation effect)")

supply_change = (rdf.network_resource_provision.iloc[-1] / rdf.network_resource_provision.iloc[1] - 1) * 100
print(f"   • Supply change: {supply_change:.1f}%")

if supply_change < -10:
    print(f"   ❌ SUPPLY COLLAPSE: Supply contracted by {abs(supply_change):.1f}%")
elif supply_change < 0:
    print(f"   ⚠️  SUPPLY DECLINE: Supply down {abs(supply_change):.1f}%")
else:
    print(f"   ✅ SUPPLY GROWTH: Supply up {supply_change:.1f}%")

print(f"\n🎯 ROOT CAUSE ANALYSIS:")
print("-" * 50)

root_causes = []

# Check if demand growth is too aggressive
if demand_growth_rate > 0.05:  # 5% daily
    root_causes.append("Demand growth too aggressive (creates unsustainable utilization pressure)")

# Check if APR threshold is unrealistic
if apr_threshold > 25:
    root_causes.append(f"APR threshold too high ({apr_threshold}% is unsustainable long-term)")

# Check if revenue model is insufficient
max_revenue_potential = rdf.network_resource_provision.max() * sys_params['resource_unit_price'][0]
max_node_revenue = max_revenue_potential * sys_params['node_revenue_share'][0]
if max_node_revenue < initial_nodes * 100:  # $100/day minimum per node
    root_causes.append("Revenue model insufficient (resource price too low)")

# Check if PID controller is too aggressive
if node_change_volatility > 5:
    root_causes.append("PID controller too aggressive (causing instability)")

# Check if token economics create selling pressure
if final_day.dex_token_price < 0.001:  # Token price collapsed
    root_causes.append("Token economics unsustainable (price collapse)")

if len(root_causes) > 0:
    for i, cause in enumerate(root_causes, 1):
        print(f"   {i}. {cause}")
else:
    print("   ✅ No obvious structural issues detected")

# Create visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Node Economics Collapse Analysis', fontsize=16)

# 1. Node count over time
ax1.plot(rdf.timestep, rdf.node_amount, color='blue', linewidth=2)
ax1.axhline(y=initial_nodes * 0.9, color='orange', linestyle='--', alpha=0.7, label='90% of initial')
ax1.axhline(y=initial_nodes * 0.5, color='red', linestyle='--', alpha=0.7, label='50% of initial')
ax1.set_title('Node Count Over Time')
ax1.set_xlabel('Days')
ax1.set_ylabel('Number of Nodes')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. APR vs Target
ax2.plot(rdf.timestep, rdf.node_apr, color='green', linewidth=2, label='Actual APR')
ax2.axhline(y=apr_threshold, color='red', linestyle='--', alpha=0.7, label=f'Target ({apr_threshold}%)')
ax2.fill_between(rdf.timestep, rdf.node_apr, apr_threshold, 
                where=(rdf.node_apr < apr_threshold), alpha=0.3, color='red', label='Below Target')
ax2.set_title('APR Performance')
ax2.set_xlabel('Days')
ax2.set_ylabel('APR %')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Utilization pressure
ax3.plot(rdf.timestep, rdf.raw_utilization, color='red', linewidth=2, label='Raw Utilization')
ax3.plot(rdf.timestep, rdf.network_resource_demand_supply_ratio, color='blue', linewidth=2, linestyle='--', label='Capped Utilization')
ax3.axhline(y=1.0, color='black', linestyle=':', alpha=0.7, label='100% Capacity')
ax3.set_title('Utilization Pressure')
ax3.set_xlabel('Days')
ax3.set_ylabel('Utilization Ratio')
ax3.set_yscale('log')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Economic viability
days_range = rdf.timestep
profit_per_node_series = []
for _, row in rdf.iterrows():
    if row.node_amount > 0:
        daily_profit = (row.node_network_revenue + row.node_incentive_revenue - row.node_expenditures) / row.node_amount
        profit_per_node_series.append(daily_profit)
    else:
        profit_per_node_series.append(0)

ax4.plot(days_range, profit_per_node_series, color='purple', linewidth=2)
ax4.axhline(y=0, color='black', linestyle=':', alpha=0.7, label='Break-even')
ax4.axhline(y=10, color='green', linestyle='--', alpha=0.7, label='$10/day target')
ax4.set_title('Node Profitability')
ax4.set_xlabel('Days')
ax4.set_ylabel('Profit per Node ($/day)')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('tests/diagnostics/node_economics_collapse_analysis.png', dpi=150, bbox_inches='tight')
print(f"\n📊 Analysis chart saved as 'tests/diagnostics/node_economics_collapse_analysis.png'")
plt.show()

print("="*60) 