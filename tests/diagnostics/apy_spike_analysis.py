"""
APY Spike Analysis - Diagnostic Tool
Identifies and validates the fix for node APY spikes at simulation start

The issue: node_amount = 0 at timestep 1, causing division by zero in APY calculation
Solution: Initialize node_amount > 0 or add proper guards
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from model.run import postprocessing
from model.sys_params import sys_params
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from radcad import Model, Simulation
import matplotlib.pyplot as plt

def run_apy_analysis():
    """Run simulation and analyze APY behavior in first 30 timesteps"""
    
    print("🔍 APY Spike Analysis - Diagnosing Node Economics Issues")
    print("=" * 60)
    
    # Short simulation for analysis
    timesteps = 30
    params = sys_params.copy()
    params['timesteps'] = [timesteps]
    
    print(f"Initial node_amount: {initial_state['node_amount']}")
    print(f"Initial node_change_amount: {initial_state['node_change_amount']}")
    print(f"Parameters: timesteps={timesteps}")
    
    # Run simulation
    model = Model(initial_state=initial_state, params=params, state_update_blocks=state_update_blocks)
    simulation = Simulation(model=model, timesteps=timesteps, runs=1)
    result = simulation.run()
    df = pd.DataFrame(result)
    
    # Process results
    rdf = postprocessing(df)
    
    # Analysis
    print("\n📊 APY Analysis Results:")
    print("-" * 40)
    
    # First 10 timesteps
    early_data = rdf.head(10)
    print(f"Timesteps 1-10 APY values:")
    for i, row in early_data.iterrows():
        print(f"  Timestep {row['timestep']}: node_amount={row['node_amount']:.0f}, APY={row['node_apr']:.2f}%")
    
    # APY statistics
    max_apr = rdf['node_apr'].max()
    min_apr = rdf['node_apr'].min()
    avg_apr = rdf['node_apr'].mean()
    spike_timesteps = len(rdf[rdf['node_apr'] > 100])
    
    print(f"\n📈 APY Statistics:")
    print(f"  Max APY: {max_apr:.2f}%")
    print(f"  Min APY: {min_apr:.2f}%")
    print(f"  Average APY: {avg_apr:.2f}%")
    print(f"  Timesteps with APY > 100%: {spike_timesteps}")
    
    # Issue identification
    zero_nodes = len(rdf[rdf['node_amount'] == 0])
    print(f"\n🚨 Issue Identification:")
    print(f"  Timesteps with zero nodes: {zero_nodes}")
    
    if zero_nodes > 0:
        print("  ❌ ISSUE CONFIRMED: Division by zero in APY calculation")
    else:
        print("  ✅ No zero node timesteps found")
    
    # Chart the issue
    plt.figure(figsize=(15, 10))
    
    # APY over time
    plt.subplot(2, 2, 1)
    plt.plot(rdf['timestep'], rdf['node_apr'], 'b-', linewidth=2)
    plt.title('Node APY Over Time')
    plt.xlabel('Timestep')
    plt.ylabel('APY (%)')
    plt.grid(True)
    
    # Node amount over time
    plt.subplot(2, 2, 2)
    plt.plot(rdf['timestep'], rdf['node_amount'], 'g-', linewidth=2)
    plt.title('Node Amount Over Time')
    plt.xlabel('Timestep')
    plt.ylabel('Number of Nodes')
    plt.grid(True)
    
    # Zoomed APY (first 10 timesteps)
    plt.subplot(2, 2, 3)
    early_data = rdf.head(10)
    plt.plot(early_data['timestep'], early_data['node_apr'], 'r-o', linewidth=2)
    plt.title('APY - First 10 Timesteps (Zoomed)')
    plt.xlabel('Timestep')
    plt.ylabel('APY (%)')
    plt.grid(True)
    
    # Node economics correlation
    plt.subplot(2, 2, 4)
    plt.scatter(rdf['node_amount'], rdf['node_apr'], alpha=0.6)
    plt.title('APY vs Node Amount')
    plt.xlabel('Node Amount')
    plt.ylabel('APY (%)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('tests/diagnostics/apy_spike_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return rdf

def test_fix_simulation(initial_nodes=100):
    """Test simulation with initial nodes to validate fix"""
    
    print(f"\n🔧 Testing Fix: Initialize with {initial_nodes} nodes")
    print("=" * 50)
    
    # Modified initial state
    test_initial_state = initial_state.copy()
    test_initial_state['node_amount'] = initial_nodes
    
    # Short simulation
    timesteps = 30
    params = sys_params.copy()
    params['timesteps'] = [timesteps]
    
    # Run simulation with fix
    model = Model(initial_state=test_initial_state, params=params, state_update_blocks=state_update_blocks)
    simulation = Simulation(model=model, timesteps=timesteps, runs=1)
    result = simulation.run()
    df = pd.DataFrame(result)
    
    # Process results
    rdf = postprocessing(df)
    
    # Analysis
    max_apr = rdf['node_apr'].max()
    min_apr = rdf['node_apr'].min()
    spike_timesteps = len(rdf[rdf['node_apr'] > 100])
    
    print(f"Fixed simulation results:")
    print(f"  Max APY: {max_apr:.2f}%")
    print(f"  Min APY: {min_apr:.2f}%") 
    print(f"  Timesteps with APY > 100%: {spike_timesteps}")
    
    if spike_timesteps == 0 and max_apr < 50:
        print("  ✅ FIX SUCCESSFUL: No APY spikes detected")
    else:
        print("  ⚠️ Fix needs refinement")
    
    return rdf

if __name__ == "__main__":
    # Run analysis
    original_data = run_apy_analysis()
    
    # Test fix
    fixed_data = test_fix_simulation(initial_nodes=100)
    
    print("\n" + "="*60)
    print("🎯 RECOMMENDATIONS:")
    print("1. Initialize node_amount > 0 in state_variables.py")
    print("2. Add timestep guards in p_node_economics()")
    print("3. Consider gradual node onboarding instead of instant jump")
    print("="*60) 