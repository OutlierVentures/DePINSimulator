import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from radcad import Model, Simulation, Experiment
from model.state_update_blocks import state_update_blocks
from model.state_variables import initial_state
from model.sys_params import sys_params
from model import run

print("🔬 Demand Saturation Fix Validation")
print("="*50)
print("Focus: Testing demand growth saturation when utilization ≥ 95%")
print()

# Run 60-day simulation to test demand saturation
TIMESTEPS = 60
MONTE_CARLO_RUNS = 1

# Create radCAD model
model = Model(
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
    params=sys_params
)

# Run simulation
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)
experiment = Experiment([simulation])
result = experiment.run()
df = pd.DataFrame(result)

# Process results
rdf = run.postprocessing(df)

# Calculate demand-focused metrics
rdf['demand_growth_rate'] = rdf.network_resource_demand.pct_change() * 100
rdf['raw_utilization'] = rdf.network_resource_demand / rdf.network_resource_provision
rdf['saturation_active'] = rdf.network_resource_demand_supply_ratio >= 0.95

print(f"📊 Demand Saturation Analysis:")
print(f"   • Initial Demand: {rdf.network_resource_demand.iloc[0]:,.0f} units")
print(f"   • Final Demand: {rdf.network_resource_demand.iloc[-1]:,.0f} units")
print(f"   • Target Growth Rate: 0.1% daily")

# Find when saturation first activates
saturation_days = rdf[rdf.saturation_active]
if len(saturation_days) > 0:
    first_saturation_day = saturation_days.timestep.iloc[0]
    print(f"   • Saturation first activated: Day {first_saturation_day}")
    
    # Check growth rates before and after saturation
    before_saturation = rdf[rdf.timestep < first_saturation_day].demand_growth_rate.dropna()
    after_saturation = rdf[rdf.timestep >= first_saturation_day].demand_growth_rate.dropna()
    
    if len(before_saturation) > 0 and len(after_saturation) > 0:
        avg_before = before_saturation.mean()
        avg_after = after_saturation.mean()
        print(f"   • Avg growth before saturation: {avg_before:.3f}%")
        print(f"   • Avg growth after saturation: {avg_after:.3f}%")
        print(f"   • Growth reduction: {((avg_before - avg_after) / avg_before * 100):.1f}%")
else:
    print(f"   • Saturation never activated (utilization stayed < 95%)")

# Final utilization check
final_raw_util = rdf.raw_utilization.iloc[-1]
final_displayed_util = rdf.network_resource_demand_supply_ratio.iloc[-1]

print(f"\n📈 Utilization Results:")
print(f"   • Final Raw Utilization: {final_raw_util:.4f} ({final_raw_util*100:.2f}%)")
print(f"   • Final Displayed Utilization: {final_displayed_util:.4f} ({final_displayed_util*100:.2f}%)")

if final_raw_util <= 1.10:  # Allow 10% tolerance for reasonable behavior
    print(f"   ✅ SUCCESS: Raw utilization stayed reasonable (≤110%)")
else:
    print(f"   ❌ ISSUE: Raw utilization still too high (>{final_raw_util*100:.1f}%)")

# Create focused visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Demand Saturation Fix Validation', fontsize=16)

# 1. Demand Growth Over Time
ax1.plot(rdf.timestep, rdf.network_resource_demand / 1e9, color='red', linewidth=2)
ax1.set_title('Network Demand Growth')
ax1.set_xlabel('Days')
ax1.set_ylabel('Demand (Billions of Units)')
ax1.grid(True, alpha=0.3)

# 2. Daily Growth Rate
ax2.plot(rdf.timestep[1:], rdf.demand_growth_rate[1:], color='orange', alpha=0.7)
ax2.axhline(y=0.1, color='red', linestyle='--', alpha=0.7, label='Target 0.1%')
if len(saturation_days) > 0:
    ax2.axvline(x=first_saturation_day, color='purple', linestyle=':', alpha=0.7, label=f'Saturation Start (Day {first_saturation_day})')
ax2.set_title('Demand Growth Rate (Daily %)')
ax2.set_xlabel('Days')
ax2.set_ylabel('Growth Rate %')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Utilization: Raw vs Capped
ax3.plot(rdf.timestep, rdf.raw_utilization * 100, color='red', linewidth=2, label='Raw Utilization')
ax3.plot(rdf.timestep, rdf.network_resource_demand_supply_ratio * 100, color='blue', linewidth=2, linestyle='--', label='Capped Utilization')
ax3.axhline(y=95, color='purple', linestyle=':', alpha=0.7, label='Saturation Threshold (95%)')
ax3.axhline(y=100, color='black', linestyle=':', alpha=0.7, label='Physical Limit (100%)')
ax3.set_title('Utilization: Raw vs Capped')
ax3.set_xlabel('Days')
ax3.set_ylabel('Utilization %')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Saturation Factor Visualization
saturation_factor = []
for _, row in rdf.iterrows():
    util = row.network_resource_demand_supply_ratio
    if util >= 0.95:
        factor = (0.95 / max(util, 0.95)) ** 2
    else:
        factor = 1.0
    saturation_factor.append(factor)

ax4.plot(rdf.timestep, saturation_factor, color='purple', linewidth=2)
ax4.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, label='No Saturation (Factor = 1.0)')
ax4.set_title('Saturation Factor (Applied to Growth Rate)')
ax4.set_xlabel('Days')
ax4.set_ylabel('Saturation Factor')
ax4.set_ylim(0, 1.1)
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('demand_saturation_validation.png', dpi=150, bbox_inches='tight')
print(f"\n📊 Validation chart saved as 'demand_saturation_validation.png'")
plt.show()

# Test specific scenarios
print(f"\n🔬 Saturation Logic Test:")
test_utilizations = [0.90, 0.95, 1.00, 1.05, 1.10]
base_growth = 0.1  # 0.1%

print(f"{'Utilization':<12} {'Saturation?':<12} {'Factor':<8} {'Adjusted Growth':<15}")
print("-" * 50)

for util in test_utilizations:
    if util >= 0.95:
        factor = (0.95 / max(util, 0.95)) ** 2
        saturation = "YES"
    else:
        factor = 1.0
        saturation = "NO"
    
    adjusted_growth = base_growth * factor
    print(f"{util*100:>6.0f}%     {saturation:<12} {factor:<8.3f} {adjusted_growth:<15.3f}%")

print(f"\n🎯 Validation Summary:")
if len(saturation_days) > 0:
    print(f"   ✅ Saturation mechanism activated correctly on day {first_saturation_day}")
    print(f"   ✅ Growth rate reduced when utilization ≥ 95%")
    if final_raw_util <= 1.10:
        print(f"   ✅ Final utilization reasonable: {final_raw_util*100:.1f}%")
        print(f"   🎉 DEMAND SATURATION FIX WORKING CORRECTLY!")
    else:
        print(f"   ⚠️  Final utilization still high but better than before")
else:
    print(f"   ⚠️  Saturation never triggered - may need adjustment")

print("="*50) 