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
from model.sys_params import sys_params, initial_values
from model import run

print("🧪 REALISTIC PARAMETER VALIDATION TEST")
print("="*60)
print("Testing network stability with economically viable parameters")
print()

# Run simulation with realistic parameters
TIMESTEPS = 365  # 1 year test
MONTE_CARLO_RUNS = 1

print(f"🔄 Running {TIMESTEPS}-day simulation with realistic parameters...")

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

# Calculate key metrics
initial_nodes = rdf.node_amount.iloc[1]
final_nodes = rdf.node_amount.iloc[-1]
node_retention = final_nodes / initial_nodes
max_utilization = rdf.network_resource_demand_supply_ratio.max()
avg_apr = rdf.node_apr.mean()
apr_target = sys_params['apr_threshold'][0]
final_token_price = rdf.dex_token_price.iloc[-1]
initial_token_price = rdf.dex_token_price.iloc[1]

print(f"\n📊 NETWORK STABILITY RESULTS:")
print("-" * 50)

print(f"   • Initial Nodes: {initial_nodes:,.0f}")
print(f"   • Final Nodes: {final_nodes:,.0f}")
print(f"   • Node Retention: {node_retention*100:.1f}%")

if node_retention > 0.8:
    print(f"   ✅ EXCELLENT: Strong node retention")
elif node_retention > 0.6:
    print(f"   ✅ GOOD: Acceptable node retention")
elif node_retention > 0.4:
    print(f"   ⚠️  MODERATE: Some network contraction")
else:
    print(f"   ❌ POOR: Significant network collapse")

print(f"\n💰 ECONOMIC VIABILITY:")
print("-" * 50)

# Calculate final economics
final_day = rdf.iloc[-1]
revenue_per_node = final_day.node_network_revenue / final_day.node_amount if final_day.node_amount > 0 else 0
costs_per_node = final_day.node_expenditures / final_day.node_amount if final_day.node_amount > 0 else 0
profit_per_node = revenue_per_node - costs_per_node

print(f"   • Revenue per node: ${revenue_per_node:.2f}/day")
print(f"   • Costs per node: ${costs_per_node:.2f}/day")
print(f"   • Profit per node: ${profit_per_node:.2f}/day")

if profit_per_node > 5:
    print(f"   ✅ EXCELLENT: High profitability")
elif profit_per_node > 2:
    print(f"   ✅ GOOD: Sustainable profits")
elif profit_per_node > 0:
    print(f"   ⚠️  MARGINAL: Low but positive profits")
else:
    print(f"   ❌ UNPROFITABLE: Negative profits")

# Payback analysis
node_setup_cost = sys_params['node_setup_cost'][0]
node_stake_value = sys_params['node_token_stake'][0] * final_token_price
total_investment = node_setup_cost + node_stake_value
payback_days = total_investment / profit_per_node if profit_per_node > 0 else float('inf')

print(f"   • Node investment: ${total_investment:.0f}")
if payback_days < 180:
    print(f"   ✅ EXCELLENT: Payback in {payback_days:.0f} days ({payback_days/30:.1f} months)")
elif payback_days < 365:
    print(f"   ✅ GOOD: Payback in {payback_days:.0f} days ({payback_days/30:.1f} months)")
elif payback_days < 730:
    print(f"   ⚠️  ACCEPTABLE: Payback in {payback_days:.0f} days ({payback_days/365:.1f} years)")
else:
    print(f"   ❌ POOR: Payback > 2 years")

print(f"\n📈 UTILIZATION & DEMAND:")
print("-" * 50)

avg_utilization = rdf.network_resource_demand_supply_ratio.mean()
print(f"   • Average utilization: {avg_utilization*100:.1f}%")
print(f"   • Max utilization: {max_utilization*100:.1f}%")

if 0.7 <= avg_utilization <= 0.9:
    print(f"   ✅ OPTIMAL: Utilization in healthy range")
elif 0.5 <= avg_utilization < 0.7:
    print(f"   ⚠️  UNDERUTILIZED: Room for demand growth")
elif 0.9 < avg_utilization <= 1.0:
    print(f"   ⚠️  HIGH UTILIZATION: Near capacity limits")
else:
    print(f"   ❌ PROBLEMATIC: Utilization outside optimal range")

# Demand growth analysis
demand_growth_actual = (rdf.network_resource_demand.iloc[-1] / rdf.network_resource_demand.iloc[1] - 1) * 100
demand_growth_target = sys_params['network_resource_demand_growth_rate'][0]
theoretical_growth = ((1 + demand_growth_target/100) ** (len(rdf)-1) - 1) * 100

print(f"   • Theoretical demand growth: {theoretical_growth:.1f}%")
print(f"   • Actual demand growth: {demand_growth_actual:.1f}%")
print(f"   • Growth efficiency: {demand_growth_actual/theoretical_growth*100:.1f}%")

print(f"\n🎯 APR PERFORMANCE:")
print("-" * 50)

print(f"   • Target APR: {apr_target}%")
print(f"   • Average APR: {avg_apr:.2f}%")
print(f"   • APR error: {abs(avg_apr - apr_target):.2f} percentage points")

below_target = rdf[rdf.node_apr < apr_target]
above_target = rdf[rdf.node_apr > apr_target]

print(f"   • Days below target: {len(below_target)}/{len(rdf)} ({len(below_target)/len(rdf)*100:.1f}%)")
print(f"   • Days above target: {len(above_target)}/{len(rdf)} ({len(above_target)/len(rdf)*100:.1f}%)")

if abs(avg_apr - apr_target) < 2:
    print(f"   ✅ EXCELLENT: APR close to target")
elif abs(avg_apr - apr_target) < 5:
    print(f"   ✅ GOOD: APR reasonably close to target")
else:
    print(f"   ⚠️  POOR: APR significantly off target")

print(f"\n💎 TOKEN ECONOMICS:")
print("-" * 50)

token_price_change = (final_token_price / initial_token_price - 1) * 100
print(f"   • Initial token price: ${initial_token_price:.4f}")
print(f"   • Final token price: ${final_token_price:.4f}")
print(f"   • Price change: {token_price_change:+.1f}%")

if token_price_change > 10:
    print(f"   ✅ EXCELLENT: Strong price appreciation")
elif token_price_change > 0:
    print(f"   ✅ GOOD: Price appreciation")
elif token_price_change > -20:
    print(f"   ⚠️  ACCEPTABLE: Moderate price decline")
else:
    print(f"   ❌ POOR: Significant price decline")

print(f"\n🔧 CONTROLLER STABILITY:")
print("-" * 50)

node_volatility = rdf.node_amount.pct_change().abs().mean() * 100
apr_volatility = rdf.node_apr.diff().abs().mean()

print(f"   • Node count volatility: ±{node_volatility:.2f}% daily")
print(f"   • APR volatility: ±{apr_volatility:.2f}% daily")

if node_volatility < 2:
    print(f"   ✅ EXCELLENT: Very stable node count")
elif node_volatility < 5:
    print(f"   ✅ GOOD: Reasonably stable node count")
else:
    print(f"   ⚠️  UNSTABLE: High node count volatility")

print(f"\n🏆 OVERALL ASSESSMENT:")
print("-" * 50)

# Scoring system
scores = []
scores.append(1 if node_retention > 0.8 else 0.5 if node_retention > 0.6 else 0)
scores.append(1 if profit_per_node > 2 else 0.5 if profit_per_node > 0 else 0)
scores.append(1 if 0.7 <= avg_utilization <= 0.9 else 0.5 if 0.5 <= avg_utilization <= 1.0 else 0)
scores.append(1 if abs(avg_apr - apr_target) < 2 else 0.5 if abs(avg_apr - apr_target) < 5 else 0)
scores.append(1 if token_price_change > 0 else 0.5 if token_price_change > -20 else 0)
scores.append(1 if node_volatility < 2 else 0.5 if node_volatility < 5 else 0)

overall_score = sum(scores) / len(scores)

print(f"   • Node Retention: {'✅' if scores[0] == 1 else '⚠️' if scores[0] == 0.5 else '❌'}")
print(f"   • Economics: {'✅' if scores[1] == 1 else '⚠️' if scores[1] == 0.5 else '❌'}")
print(f"   • Utilization: {'✅' if scores[2] == 1 else '⚠️' if scores[2] == 0.5 else '❌'}")
print(f"   • APR Control: {'✅' if scores[3] == 1 else '⚠️' if scores[3] == 0.5 else '❌'}")
print(f"   • Token Price: {'✅' if scores[4] == 1 else '⚠️' if scores[4] == 0.5 else '❌'}")
print(f"   • Stability: {'✅' if scores[5] == 1 else '⚠️' if scores[5] == 0.5 else '❌'}")

print(f"\n   📊 Overall Score: {overall_score*100:.0f}/100")

if overall_score >= 0.8:
    print(f"   🎉 EXCELLENT: Network parameters are well-calibrated!")
elif overall_score >= 0.6:
    print(f"   ✅ GOOD: Network is stable with minor issues")
elif overall_score >= 0.4:
    print(f"   ⚠️  ACCEPTABLE: Network has some problems")
else:
    print(f"   ❌ POOR: Network parameters need significant adjustment")

# Create comprehensive visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Realistic Parameter Validation Results', fontsize=16)

# 1. Node retention over time
ax1.plot(rdf.timestep, rdf.node_amount, color='blue', linewidth=2)
ax1.axhline(y=initial_nodes * 0.8, color='green', linestyle='--', alpha=0.7, label='80% threshold')
ax1.set_title('Node Count Stability')
ax1.set_xlabel('Days')
ax1.set_ylabel('Number of Nodes')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. APR tracking
ax2.plot(rdf.timestep, rdf.node_apr, color='green', linewidth=2, label='Actual APR')
ax2.axhline(y=apr_target, color='red', linestyle='--', alpha=0.7, label=f'Target ({apr_target}%)')
ax2.fill_between(rdf.timestep, rdf.node_apr - 2, rdf.node_apr + 2, alpha=0.2, color='green', label='±2% band')
ax2.set_title('APR Performance')
ax2.set_xlabel('Days')
ax2.set_ylabel('APR %')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Utilization levels
ax3.plot(rdf.timestep, rdf.network_resource_demand_supply_ratio * 100, color='purple', linewidth=2)
ax3.axhline(y=70, color='green', linestyle=':', alpha=0.7, label='Optimal range')
ax3.axhline(y=90, color='green', linestyle=':', alpha=0.7)
ax3.fill_between(rdf.timestep, 70, 90, alpha=0.2, color='green')
ax3.set_title('Network Utilization')
ax3.set_xlabel('Days')
ax3.set_ylabel('Utilization %')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Node profitability
profit_series = []
for _, row in rdf.iterrows():
    if row.node_amount > 0:
        daily_profit = (row.node_network_revenue + row.node_incentive_revenue - row.node_expenditures) / row.node_amount
        profit_series.append(daily_profit)
    else:
        profit_series.append(0)

ax4.plot(rdf.timestep, profit_series, color='orange', linewidth=2)
ax4.axhline(y=0, color='black', linestyle=':', alpha=0.7, label='Break-even')
ax4.axhline(y=2, color='green', linestyle='--', alpha=0.7, label='$2/day target')
ax4.set_title('Node Profitability')
ax4.set_xlabel('Days')
ax4.set_ylabel('Profit per Node ($/day)')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('tests/diagnostics/realistic_parameter_validation.png', dpi=150, bbox_inches='tight')
print(f"\n📊 Validation chart saved as 'tests/diagnostics/realistic_parameter_validation.png'")
plt.show()

print("="*60) 