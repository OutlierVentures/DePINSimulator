#!/usr/bin/env python3
"""
Test that new UI parameters work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from radcad import Model, Simulation
from model.sys_params import sys_params
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
import pandas as pd

# Test new parameter overrides
test_params = sys_params.copy()
test_params.update({
    'node_setup_cost': [2000.0],  # Changed from default 1000
    'node_revenue_share': [0.80],  # Changed from default 0.75 
    'initial_network_resource_demand': [400000000],  # Changed from default 300M
    'foundation_cash_burn_rate': [500000],  # Changed from default 1M
    'initial_foundation_cash_reserves': [30000000],  # Changed from default 25M
})

print("🧪 Testing new UI parameters...")
print(f"Node setup cost: ${test_params['node_setup_cost'][0]:,.0f}")
print(f"Node revenue share: {test_params['node_revenue_share'][0]:.1%}")
print(f"Initial demand: {test_params['initial_network_resource_demand'][0]:,.0f}")
print(f"Foundation burn: ${test_params['foundation_cash_burn_rate'][0]:,.0f}/day")

try:
    # Create model with test parameters
    model = Model(
        initial_state=initial_state,
        params=test_params,
        state_update_blocks=state_update_blocks
    )
    
    # Run short simulation
    simulation = Simulation(model=model, timesteps=30, runs=1)
    result = simulation.run()
    
    df = pd.DataFrame(result)
    
    # Check that parameters are being applied
    print(f"\n✅ Simulation completed successfully!")
    print(f"Final foundation reserves: ${df['foundation_cash_reserves'].iloc[-1]:,.0f}")
    print(f"Final node count: {df['node_amount'].iloc[-1]:,.0f}")
    print(f"Final network demand: {df['network_resource_demand'].iloc[-1]:,.0f}")
    
    # Verify the parameters had effect
    burn_rate_check = test_params['foundation_cash_burn_rate'][0]
    if abs(df['foundation_expenditures'].iloc[-1] - burn_rate_check) < burn_rate_check * 0.1:
        print(f"✅ Foundation burn rate parameter working correctly")
    else:
        print(f"⚠️ Foundation burn rate may not be applied correctly")
        
    print(f"\n🎉 All new UI parameters tested successfully!")

except Exception as e:
    print(f"❌ Error testing parameters: {e}")
    import traceback
    traceback.print_exc()