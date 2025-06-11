"""
Foundation Economics Validation Test
Tests bug fixes for foundation burn rate and bankruptcy protection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from model.policy_functions import p_foundation_economics
from model.sys_params import sys_params

def test_foundation_daily_burn_rate():
    """Test that foundation burn rate is calculated daily, not monthly"""
    
    # Test parameters
    params = {
        'foundation_cash_burn_rate': 1e6  # $1M annual burn rate
    }
    
    # Test state (timestep 100)
    prev_state = {
        'foundation_revenue': 1000,  # $1k daily revenue
        'foundation_cash_reserves': 25e6,  # $25M reserves
        'timestep': 100
    }
    
    # Execute function
    result = p_foundation_economics(params, 1, [], prev_state)
    
    # Daily burn should be annual_rate / 365, not annual_rate / 12
    expected_daily_burn = 1e6 / 365  # ~$2,740 per day
    monthly_burn = 1e6 / 12         # ~$83,333 per month (wrong!)
    
    print(f"✅ Foundation Economics Validation Test")
    print(f"   Annual burn rate: ${params['foundation_cash_burn_rate']:,.0f}")
    print(f"   Expected daily burn: ${expected_daily_burn:,.0f}")
    print(f"   Actual daily burn: ${result['foundation_expenditures']:,.0f}")
    print(f"   Wrong monthly calc: ${monthly_burn:,.0f}")
    
    # Validate daily calculation
    assert abs(result['foundation_expenditures'] - expected_daily_burn) < 1, \
        f"Daily burn should be {expected_daily_burn}, got {result['foundation_expenditures']}"
    
    # Validate cash reserves calculation
    expected_reserves = prev_state['foundation_cash_reserves'] - expected_daily_burn + prev_state['foundation_revenue']
    assert abs(result['foundation_cash_reserves'] - expected_reserves) < 1, \
        f"Cash reserves calculation incorrect"
    
    print(f"   ✅ Daily burn rate calculation: PASSED")
    return True

def test_foundation_bankruptcy_protection():
    """Test that foundation cash reserves cannot go negative"""
    
    # Test parameters
    params = {
        'foundation_cash_burn_rate': 365e3  # $365k annual = $1k daily
    }
    
    # Test state with insufficient reserves
    prev_state = {
        'foundation_revenue': 500,   # $500 daily revenue
        'foundation_cash_reserves': 200,  # Only $200 left
        'timestep': 100
    }
    
    # Execute function
    result = p_foundation_economics(params, 1, [], prev_state)
    
    daily_burn = 365e3 / 365  # $1,000 daily
    net_cash_flow = prev_state['foundation_cash_reserves'] - daily_burn + prev_state['foundation_revenue']
    # = $200 - $1,000 + $500 = -$300 (would be negative without protection)
    
    print(f"\n✅ Foundation Bankruptcy Protection Test")
    print(f"   Initial reserves: ${prev_state['foundation_cash_reserves']:,.0f}")
    print(f"   Daily burn: ${daily_burn:,.0f}")
    print(f"   Daily revenue: ${prev_state['foundation_revenue']:,.0f}")
    print(f"   Net flow (without protection): ${net_cash_flow:,.0f}")
    print(f"   Final reserves (with protection): ${result['foundation_cash_reserves']:,.0f}")
    
    # Validate non-negative reserves
    assert result['foundation_cash_reserves'] >= 0, \
        f"Foundation reserves should never be negative, got {result['foundation_cash_reserves']}"
    
    # Should be exactly 0 due to max(0, ...) protection
    assert result['foundation_cash_reserves'] == 0, \
        f"Foundation reserves should be 0 when protected from negative, got {result['foundation_cash_reserves']}"
    
    print(f"   ✅ Bankruptcy protection: PASSED")
    return True

def test_foundation_positive_cash_flow():
    """Test normal operation with positive cash flow"""
    
    # Test parameters
    params = {
        'foundation_cash_burn_rate': 365e3  # $365k annual = $1k daily
    }
    
    # Test state with sufficient reserves and revenue
    prev_state = {
        'foundation_revenue': 2000,   # $2k daily revenue  
        'foundation_cash_reserves': 1e6,  # $1M reserves
        'timestep': 100
    }
    
    # Execute function
    result = p_foundation_economics(params, 1, [], prev_state)
    
    daily_burn = 365e3 / 365  # $1,000 daily
    expected_reserves = prev_state['foundation_cash_reserves'] - daily_burn + prev_state['foundation_revenue']
    # = $1M - $1k + $2k = $1,001,000
    
    print(f"\n✅ Foundation Positive Cash Flow Test")
    print(f"   Initial reserves: ${prev_state['foundation_cash_reserves']:,.0f}")
    print(f"   Daily burn: ${daily_burn:,.0f}")
    print(f"   Daily revenue: ${prev_state['foundation_revenue']:,.0f}")
    print(f"   Expected reserves: ${expected_reserves:,.0f}")
    print(f"   Actual reserves: ${result['foundation_cash_reserves']:,.0f}")
    
    # Validate reserves calculation
    assert abs(result['foundation_cash_reserves'] - expected_reserves) < 1, \
        f"Foundation reserves should be {expected_reserves}, got {result['foundation_cash_reserves']}"
    
    print(f"   ✅ Positive cash flow: PASSED")
    return True

def run_all_tests():
    """Run all foundation economics validation tests"""
    print("🧪 Foundation Economics Validation Tests")
    print("=" * 50)
    
    try:
        test_foundation_daily_burn_rate()
        test_foundation_bankruptcy_protection() 
        test_foundation_positive_cash_flow()
        
        print("\n" + "=" * 50)
        print("🎉 All Foundation Economics Tests PASSED!")
        print("\n✅ Bug fixes validated:")
        print("   • Foundation burn rate now calculated daily (÷365) instead of monthly (÷12)")
        print("   • Foundation cash reserves protected from going negative")
        print("   • Normal positive cash flow operations working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    run_all_tests() 