#!/usr/bin/env python3
"""
DePIN Simulator Streamlit UI

Interactive web interface for DePIN token economics modeling.
Provides parameter input, real-time simulation, and organized chart visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Add project root to Python path
sys.path.append(os.path.dirname(__file__))

# Import simulation components
from radcad import Model, Simulation
from model.sys_params import sys_params
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model import run
from config import get_config, list_available_configs

# Page configuration
st.set_page_config(
    page_title="DePIN Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_ui_run_directory(sys_params_like: dict) -> str:
    """Create organized data directory structure for UI simulation results.

    Mirrors the CLI structure: <config_name>_run_<NNN>_<timestamp> with charts/data/reports subdirs.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = "data"
    os.makedirs(base_dir, exist_ok=True)

    # Determine config name if available
    config_name = "custom"
    if '_metadata' in sys_params_like:
        config_name = sys_params_like['_metadata'].get('name', 'custom').lower().replace(' ', '_')

    run_number = 1
    prefix = f"{config_name}_run_"
    existing = [d for d in os.listdir(base_dir) if d.startswith(prefix)]
    if existing:
        nums = []
        for d in existing:
            try:
                part = d.replace(prefix, '').split('_')[0]
                nums.append(int(part))
            except Exception:
                continue
        if nums:
            run_number = max(nums) + 1

    run_name = f"{config_name}_run_{run_number:03d}_{timestamp}"
    run_dir = os.path.join(base_dir, run_name)
    os.makedirs(os.path.join(run_dir, "charts"), exist_ok=True)
    os.makedirs(os.path.join(run_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(run_dir, "reports"), exist_ok=True)
    return run_dir

def save_ui_summary_report(run_dir: str, df_processed: pd.DataFrame, params: dict, timesteps: int, runs: int) -> str:
    """Generate and save a concise summary report for the UI run."""
    config_name = params.get('_metadata', {}).get('name', 'Custom Configuration')
    config_desc = params.get('_metadata', {}).get('description', 'No description available')

    final = df_processed.iloc[-1]
    summary = f"""
DePIN Simulator - Simulation Summary Report
==========================================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Run Directory: {os.path.basename(run_dir)}
Configuration: {config_name}
Description: {config_desc}

Simulation Parameters:
Duration: {timesteps:,} timesteps ({timesteps/365:.1f} years)
Monte Carlo Runs: {runs}
Emission Policy: {params.get('emission_policy', ['unknown'])[0] if isinstance(params.get('emission_policy'), list) else params.get('emission_policy')}

Key Final Metrics (at simulation end):
=====================================
Network Metrics:
- Node Count: {final.get('node_amount', 0):,.0f} nodes
- Network Utilization: {final.get('network_resource_demand_supply_ratio', 0):.1%}
- Network Demand: {final.get('network_resource_demand', 0):,.0f} resource units

Token Economics:
- Token Price: ${final.get('dex_token_price', 0):.6f}
- Total Token Supply: {final.get('token_total_supply', 0):,.0f} tokens
- Circulating Supply: {final.get('token_circulating_supply', 0):,.0f} tokens
- Tokens Staked: {final.get('token_staked_supply', 0):,.0f} tokens

Node Economics:
- Node APR: {final.get('node_apr', 0):.1f}%
- Node Profit: ${final.get('node_profit', 0):,.2f} per day
- Network Revenue: ${final.get('node_network_revenue', 0):,.2f} per day
- Incentive Revenue: ${final.get('node_incentive_revenue', 0):,.2f} per day

Foundation:
- Cash Reserves: ${final.get('foundation_cash_reserves', 0):,.0f}
- Daily Cash Flow: ${(final.get('foundation_revenue', 0) - final.get('foundation_expenditures', 0)):.2f}
"""
    report_path = os.path.join(run_dir, "reports", "summary_report.txt")
    with open(report_path, "w") as f:
        f.write(summary)
    return summary

def save_ui_outputs(run_dir: str, df_raw: pd.DataFrame, df_processed: pd.DataFrame, params: dict, timesteps: int, runs: int):
    """Save raw/processed CSVs, summary report, and params.json for UI runs."""
    df_raw.to_csv(os.path.join(run_dir, "data", "simulation_results_raw.csv"), index=False)
    df_processed.to_csv(os.path.join(run_dir, "data", "simulation_results.csv"), index=False)

    # Save params (ensure JSON serializable)
    try:
        with open(os.path.join(run_dir, "reports", "params.json"), "w") as f:
            json.dump(params, f, indent=2, default=str)
    except Exception:
        pass

    save_ui_summary_report(run_dir, df_processed, params, timesteps, runs)

def save_plotly_fig(fig, filename: str):
    """Optionally export plotly figures as lightweight HTML when enabled."""
    try:
        run_dir = st.session_state.get('run_dir')
        export_enabled = st.session_state.get('export_charts_html', False)
        if run_dir and export_enabled and fig is not None:
            charts_dir = os.path.join(run_dir, "charts")
            os.makedirs(charts_dir, exist_ok=True)
            fig.write_html(os.path.join(charts_dir, filename), include_plotlyjs='cdn', full_html=False)
    except Exception:
        pass

def load_available_configs():
    """Load available configuration files"""
    try:
        all_configs = list_available_configs()
        production_configs = [c for c in all_configs if c.startswith('production/')]
        
        configs = {}
        for config_name in production_configs:
            try:
                config_data = get_config(config_name)
                display_name = config_data.get('_metadata', {}).get('name', config_name.split('/')[-1])
                configs[display_name] = config_name
            except:
                continue
        
        return configs
    except:
        return {}

def create_parameter_inputs():
    """Create parameter input widgets in sidebar"""
    st.sidebar.markdown("## 📊 Configuration")
    
    # Configuration loader
    available_configs = load_available_configs()
    if available_configs:
        selected_config = st.sidebar.selectbox(
            "Load Configuration:",
            options=["Custom"] + list(available_configs.keys()),
            help="Load predefined parameter sets"
        )
        
        if selected_config != "Custom":
            config_name = available_configs[selected_config]
            config_params = get_config(config_name)
            st.sidebar.success(f"✅ Loaded: {selected_config}")
        else:
            config_params = sys_params.copy()
    else:
        config_params = sys_params.copy()
        st.sidebar.warning("No config files found, using defaults")
    
    st.sidebar.markdown("---")
    
    # Core Parameters
    st.sidebar.markdown("### 🏗️ Core Parameters")
    
    initial_nodes = st.sidebar.number_input(
        "Initial Node Amount",
        min_value=100,
        max_value=100000,
        value=int(config_params.get('initial_node_amount', [15000])[0]),
        step=500,
        help="🏗️ Starting number of infrastructure nodes (hardware operators) in your network. Typical range: 1,000-50,000. Higher numbers = more decentralized but harder to bootstrap."
    )
    
    resource_price = st.sidebar.number_input(
        "Resource Unit Price ($)",
        min_value=0.00001,
        max_value=1.0,
        value=float(config_params.get('resource_unit_price', [0.00002])[0]),
        format="%.6f",
        help="💰 Base price customers pay per resource unit (e.g., per GB storage, per compute hour). This determines your network's revenue potential. Compare to AWS/Google pricing for similar services."
    )
    
    demand_growth = st.sidebar.slider(
        "Network Demand Growth Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=float(config_params.get('network_resource_demand_growth_rate', [0.02])[0]) * 100,
        step=0.1,
        help="📈 Daily growth rate of customer demand for your network's resources. 1-5% daily = 37x-148x annual growth. Models user adoption, marketing success, and market expansion."
    )
    
    apr_target = st.sidebar.slider(
        "Target APR (%)",
        min_value=5.0,
        max_value=50.0,
        value=float(config_params.get('apr_threshold', [15])[0]),
        step=1.0,
        help="🎯 Target Annual Percentage Return (APR) that node operators should earn. 15-30% attracts operators without oversupply. Too high = unsustainable token inflation. Too low = insufficient node growth."
    )
    
    # Emission Policy
    emission_policy = st.sidebar.selectbox(
        "Emission Policy",
        options=["linear", "per_device", "bme"],
        index=["linear", "per_device", "bme"].index(config_params.get('emission_policy', ['linear'])[0]),
        help="🪙 How tokens are distributed to node operators:\n• LINEAR: Fixed daily emission (predictable, doesn't respond to growth)\n• PER-DEVICE: Scales with node count (incentivizes network expansion)\n• BME: Usage-driven emission (tokens minted based on actual network usage)"
    )
    
    # Emission policy specific parameters
    if emission_policy == "per_device":
        emission_per_device = st.sidebar.number_input(
            "Emission per Device (daily)",
            min_value=1,
            max_value=1000,
            value=int(config_params.get('emission_per_device_daily', [100])[0]),
            help="📱 Tokens emitted per active node per day. Higher values = faster network growth but more inflation. Calculate based on target node profitability."
        )
    
    if emission_policy == "bme":
        bme_burn_multiplier = st.sidebar.slider(
            "BME Burn Rate Multiplier",
            min_value=0.1,
            max_value=2.0,
            value=float(config_params.get('bme_burn_rate_multiplier', [1.0])[0]),
            step=0.1,
            help="🔥 Controls how much revenue is equivalent to token burns. 1.0 = burn tokens equal to network revenue. Higher = more deflationary."
        )
        
        bme_mint_multiplier = st.sidebar.slider(
            "BME Mint Rate Multiplier",
            min_value=0.1,
            max_value=2.0,
            value=float(config_params.get('bme_mint_rate_multiplier', [1.0])[0]),
            step=0.1,
            help="🪙 Controls token minting rate. 1.0 = mint equals burn (stable supply). >1.0 = inflationary, <1.0 = deflationary."
        )
    
    st.sidebar.markdown("---")
    
    # Essential Business Parameters  
    st.sidebar.markdown("### 💼 Business Parameters")
    
    node_setup_cost = st.sidebar.number_input(
        "Node Setup Cost ($)",
        min_value=100.0,
        max_value=10000.0,
        value=float(config_params.get('node_setup_cost', [1000.0])[0]),
        step=100.0,
        help="💻 Hardware/setup investment required per node - affects payback period"
    )
    
    node_revenue_share = st.sidebar.slider(
        "Node Revenue Share (%)",
        min_value=50.0,
        max_value=85.0,
        value=float(config_params.get('node_revenue_share', [0.75])[0]) * 100,
        step=5.0,
        help="💰 Percentage of network revenue distributed to node operators"
    )
    
    foundation_revenue_share = st.sidebar.slider(
        "Foundation Revenue Share (%)",
        min_value=10.0,
        max_value=40.0,
        value=float(config_params.get('foundation_revenue_share', [0.24])[0]) * 100,
        step=2.0,
        help="🏛️ Percentage of network revenue for foundation operations"
    )
    
    # Calculate remaining for buyback/burn (show as info)
    remaining_revenue = 100.0 - node_revenue_share - foundation_revenue_share
    if remaining_revenue < 0:
        st.sidebar.error(f"⚠️ Revenue shares exceed 100%! Reduce by {-remaining_revenue:.1f}%")
    else:
        st.sidebar.info(f"ℹ️ Remaining for buyback/burn: {remaining_revenue:.1f}%")
    
    initial_network_demand = st.sidebar.number_input(
        "Initial Network Demand",
        min_value=1000000,
        max_value=2000000000,
        value=int(config_params.get('initial_network_resource_demand', [300000000])[0]),
        step=10000000,
        help="🌐 Starting demand level for network resources"
    )
    
    foundation_cash_burn = st.sidebar.number_input(
        "Foundation Daily Burn Rate ($)",
        min_value=10000,
        max_value=10000000,
        value=int(config_params.get('foundation_cash_burn_rate', [1000000])[0]),
        step=100000,
        help="💸 Foundation daily operational expenses"
    )
    
    foundation_cash_reserves = st.sidebar.number_input(
        "Foundation Initial Reserves ($)",
        min_value=1000000,
        max_value=100000000,
        value=int(config_params.get('initial_foundation_cash_reserves', [25000000])[0]),
        step=1000000,
        help="🏦 Foundation starting cash reserves"
    )
    
    st.sidebar.markdown("---")
    
    # Token Economics Parameters
    st.sidebar.markdown("### 🪙 Token Economics")
    
    token_total_supply = st.sidebar.number_input(
        "Total Token Supply",
        min_value=1000000,
        max_value=100000000000,
        value=int(config_params.get('token_initial_total_supply', [10000000000])[0]),
        step=1000000000,
        help="""🪙 **Total Token Supply**
        
The maximum number of tokens that will ever exist in your protocol. This is a fundamental tokenomics parameter that affects:

• **Token Price**: Lower supply = higher price per token (all else equal)
• **Emission Sustainability**: More supply = longer emissions can last
• **Psychology**: Round numbers (1B, 10B) are easier for users to understand
• **Precision**: Higher supply allows more granular rewards

**Real DePIN Examples:**
• Helium (HNT): 223M supply (deflationary)
• Filecoin (FIL): ~2B supply 
• Storj (STORJ): 425M supply
• Our default: 10B (good for utility token with many small transactions)"""
    )
    
    token_initial_valuation = st.sidebar.number_input(
        "Initial Market Cap ($)",
        min_value=100000,
        max_value=1000000000,
        value=int(config_params.get('token_initial_valuation', [50000000])[0]),
        step=1000000,
        help="""💰 **Initial Market Capitalization**
        
The total value of all tokens at launch (token price × total supply). This determines:

• **Starting Token Price**: Market cap ÷ total supply = price per token
• **Node Stake Value**: Higher valuation = more expensive node participation
• **Fundraising Context**: Should align with your actual raise/valuation
• **Liquidity Pool Size**: Affects initial trading depth

**Typical DePIN Valuations at Launch:**
• Small protocols: $1M - $10M
• Medium protocols: $10M - $100M  
• Large protocols: $100M - $1B
• Our default: $50M (reasonable for established DePIN with traction)

**Impact on Node Economics:**
At $50M valuation with 10B tokens = $0.005/token
Node staking 10,000 tokens = $50 stake value"""
    )
    
    incentive_token_allocation = st.sidebar.slider(
        "Incentive Token Allocation (%)",
        min_value=10.0,
        max_value=60.0,
        value=float(config_params.get('incentive_token_allocation', [0.08])[0]) * 100,
        step=2.0,
        help="""🎁 **Incentive Token Allocation**
        
Percentage of total token supply reserved for rewarding node operators. This is critical for network sustainability:

• **Network Growth**: More allocation = stronger incentives = faster growth
• **Emission Duration**: More allocation = longer emissions can last
• **Token Pressure**: More allocation = more selling pressure from node operators
• **Decentralization**: Higher rewards attract more diverse node operators

**Real DePIN Allocations:**
• Conservative: 15-25% (sustainable, longer duration)
• Balanced: 25-40% (growth-focused)
• Aggressive: 40-60% (rapid expansion, shorter runway)
• Our default: 8% (very conservative, long-term sustainability)

**Duration Example:**
With 8% allocation (800M tokens) and 1M tokens/day emission:
• Emission runway = 800 days (2+ years)
• Can adjust emission rate based on network growth needs"""
    )
    
    seller_token_allocation = st.sidebar.slider(
        "Team/Investor Token Allocation (%)",
        min_value=20.0,
        max_value=60.0,
        value=float(config_params.get('seller_token_allocation', [0.4])[0]) * 100,
        step=5.0,
        help="""👥 **Team/Investor Token Allocation**
        
Percentage reserved for team, advisors, and investors. These tokens typically have vesting schedules:

• **Team Alignment**: Ensures long-term commitment from builders
• **Investor Returns**: Compensates early financial supporters  
• **Selling Pressure**: Higher allocation = more potential future selling
• **Community Perception**: Too high allocation can hurt community trust

**Industry Standards:**
• Community-first: 20-30% (high community ownership)
• Balanced: 30-45% (standard for funded protocols)  
• Founder-heavy: 45-60% (higher control, more centralized)
• Our default: 40% (reasonable for funded DePIN protocol)

**Vesting Impact:**
These tokens usually vest over 2-4 years, creating predictable supply increases
that affect token price and dilution calculations."""
    )
    
    # Calculate and show remaining allocations
    liquidity_allocation = 5.0  # Typically fixed at 5%
    remaining_allocation = 100.0 - incentive_token_allocation - seller_token_allocation - liquidity_allocation
    
    if remaining_allocation < 0:
        st.sidebar.error(f"⚠️ Token allocations exceed 95%! (5% reserved for liquidity)")
    else:
        st.sidebar.info(f"""📊 **Allocation Summary:**
• Incentives: {incentive_token_allocation:.1f}%
• Team/Investors: {seller_token_allocation:.1f}%  
• Liquidity Pool: 5.0%
• Treasury/Reserve: {remaining_allocation:.1f}%""")
    
    st.sidebar.markdown("---")
    
    # Advanced Parameters (Collapsible)
    with st.sidebar.expander("🔧 Advanced Parameters"):
        st.markdown("**Network Scaling Controls**")
        
        node_growth_cap = st.slider(
            "Node Growth Cap (% per day)",
            min_value=1.0,
            max_value=10.0,
            value=float(config_params.get('node_growth_cap', [3])[0]),
            step=0.5,
            help="""🚀 **Node Growth Rate Limit**
            
Maximum percentage by which the node count can increase per day. Prevents unrealistic hockey-stick growth:

• **Stability**: Prevents sudden massive node influx that could crash APR
• **Realism**: Real infrastructure takes time to deploy and onboard
• **Market Dynamics**: Gradual growth allows price/demand to adjust naturally

**Typical Values:**
• Conservative: 1-2% per day (realistic for physical infrastructure)
• Moderate: 2-5% per day (balanced growth)  
• Aggressive: 5-10% per day (rapid scaling, higher volatility)
• Our default: 3% per day (allows steady growth without instability)"""
        )
        
        node_token_stake = st.number_input(
            "Node Token Stake",
            min_value=1000,
            max_value=100000,
            value=int(config_params.get('node_token_stake', [10000])[0]),
            step=1000,
            help="""🪙 **Required Token Stake per Node**
            
Amount of tokens each node operator must lock up to participate. This creates economic alignment:

• **Skin in the Game**: Node operators have financial stake in protocol success
• **Security**: Makes it expensive to attack the network
• **Token Demand**: More nodes = more tokens locked up = reduced circulating supply
• **Barrier to Entry**: Higher stake = fewer but more committed operators

**Economic Impact:**
At current token price, 10,000 token stake = specific dollar value
Higher stake = higher barrier but stronger commitment"""
        )
        
        node_reliability = st.slider(
            "Node Reliability (%)",
            min_value=90.0,
            max_value=99.9,
            value=float(config_params.get('node_reliability', [0.98])[0]) * 100,
            step=0.5,
            help="""📡 **Node Uptime/Reliability Factor**
            
Average percentage of time nodes are online and providing services. Affects network capacity:

• **Effective Capacity**: 98% reliability means network can serve 98% of theoretical maximum
• **User Experience**: Lower reliability = more service interruptions
• **Node Economics**: Unreliable nodes earn less, creating natural quality incentives
• **Network Resilience**: Built-in redundancy for node failures

**Typical DePIN Reliability:**
• Physical infrastructure: 95-99% (hardware dependencies)
• Cloud-based services: 99%+ (better redundancy)
• Our default: 98% (realistic for mixed physical/digital DePIN)"""
        )
        
        st.markdown("---")
        
        # Demand Growth Model
        st.markdown("**Demand Growth Model**")
        default_growth_scenario = config_params.get('business_growth_scenario', ['linear'])[0]
        growth_scenario = st.selectbox(
            "Demand Growth Scenario",
            options=["linear", "custom_phases"],
            index=["linear", "custom_phases"].index(default_growth_scenario) if default_growth_scenario in ["linear", "custom_phases"] else 0,
            help="Choose how network demand evolves: linear (single daily percentage) or custom phases with milestones."
        )

        phases_from_cfg = config_params.get('business_growth_phases', []) if isinstance(config_params.get('business_growth_phases', []), list) else []
        milestones_from_cfg = config_params.get('business_demand_milestones', []) if isinstance(config_params.get('business_demand_milestones', []), list) else []

        if growth_scenario == "custom_phases":
            st.caption("Define sequential phases with duration (days) and daily growth rates (%). Add optional milestones to apply temporary multipliers.")
            default_num_phases = len(phases_from_cfg) if phases_from_cfg else 3
            num_phases = st.number_input("Number of Phases", min_value=1, max_value=6, value=int(default_num_phases))
            phases = []
            for i in range(int(num_phases)):
                with st.container():
                    col_a, col_b = st.columns(2)
                    def_days = int(phases_from_cfg[i]['days']) if i < len(phases_from_cfg) and 'days' in phases_from_cfg[i] else 90
                    def_rate = float(phases_from_cfg[i]['daily_growth_rate']) if i < len(phases_from_cfg) and 'daily_growth_rate' in phases_from_cfg[i] else 0.03
                    with col_a:
                        p_days = st.number_input(f"Phase {i+1} Days", min_value=1, max_value=5000, value=int(def_days), key=f"phase_days_{i}")
                    with col_b:
                        p_rate = st.number_input(f"Phase {i+1} Daily Growth (%)", min_value=-5.0, max_value=10.0, value=float(def_rate), step=0.01, key=f"phase_rate_{i}")
                    phases.append({"days": int(p_days), "daily_growth_rate": float(p_rate)})

            st.markdown("---")
            default_num_milestones = len(milestones_from_cfg) if milestones_from_cfg else 0
            num_milestones = st.number_input("Number of Milestones", min_value=0, max_value=6, value=int(default_num_milestones))
            milestones = []
            for j in range(int(num_milestones)):
                with st.container():
                    col_c, col_d = st.columns(2)
                    def_day = int(milestones_from_cfg[j]['day']) if j < len(milestones_from_cfg) and 'day' in milestones_from_cfg[j] else 120
                    def_mult = float(milestones_from_cfg[j]['multiplier']) if j < len(milestones_from_cfg) and 'multiplier' in milestones_from_cfg[j] else 1.2
                    with col_c:
                        m_day = st.number_input(f"Milestone {j+1} Day", min_value=1, max_value=5000, value=int(def_day), key=f"ms_day_{j}")
                    with col_d:
                        m_mult = st.number_input(f"Milestone {j+1} Multiplier", min_value=0.1, max_value=3.0, value=float(def_mult), step=0.05, key=f"ms_mult_{j}")
                    milestones.append({"day": int(m_day), "multiplier": float(m_mult)})
        
        # Token Market Dynamics
        st.markdown("**Token Market Dynamics**")
        token_market_scenario = st.selectbox(
            "Market Scenario",
            options=["stable", "moderate_volatility", "high_volatility", "bull_market", "bear_market"],
            index=["stable", "moderate_volatility", "high_volatility", "bull_market", "bear_market"].index(
                config_params.get('token_market_scenario', ['stable'])[0]
            ),
            help="📊 Models token market behavior separate from business fundamentals:\n• STABLE: Minimal speculation\n• MODERATE/HIGH VOLATILITY: Price swings around fundamental value\n• BULL/BEAR: Sustained trends up/down"
        )
        
        speculation_factor = st.slider(
            "Speculation Factor",
            min_value=0.5,
            max_value=3.0,
            value=float(config_params.get('token_speculation_factor', [1.0])[0]),
            step=0.1,
            help="🎲 Base speculation multiplier. 1.0 = no speculation premium. 2.0 = token trades at 2x fundamental value on average. Models hype cycles and investor sentiment."
        )
        
        # Utilization Controller
        st.markdown("**Utilization Controller**")
        utilization_controller = st.checkbox(
            "Enable Utilization Controller",
            value=config_params.get('utilization_controller_enabled', [False])[0],
            help="🎛️ Automatically adjusts network resource supply to maintain optimal utilization (70-85%). Prevents network congestion and underutilization by dynamically scaling capacity."
        )
        
        if utilization_controller:
            # Handle both decimal (0.8) and percentage (80) formats from config
            config_util_target = config_params.get('utilization_target', [0.775])[0]
            if config_util_target <= 1.0:  # Decimal format (0.8)
                default_util_pct = config_util_target * 100
            else:  # Already percentage format (80)
                default_util_pct = config_util_target
                
            utilization_target = st.slider(
                "Target Utilization (%)",
                min_value=50.0,
                max_value=95.0,
                value=float(default_util_pct),
                step=2.5,
                help="Target network utilization ratio. Optimal range: 70-85%"
            )
        
        # Dynamic Resource Pricing
        st.markdown("**Resource Pricing**")
        dynamic_pricing = st.checkbox(
            "Enable Dynamic Pricing",
            value=config_params.get('resource_price_adjustment_enabled', [False])[0],
            help="💹 Resource prices respond to network utilization. High utilization = higher prices (like Uber surge pricing). Models real-world supply/demand economics."
        )
        
        if dynamic_pricing:
            price_sensitivity = st.slider(
                "Price Sensitivity",
                min_value=0.0,
                max_value=1.0,
                value=float(config_params.get('resource_price_utilization_sensitivity', [0.3])[0]),
                step=0.05,
                help="📈 How aggressively prices respond to utilization. 0.3 = moderate response. 0.8 = highly responsive (big price swings). 0.1 = subtle adjustments."
            )
    
    st.sidebar.markdown("---")
    
    # Simulation Settings
    st.sidebar.markdown("### ⚙️ Simulation Settings")
    
    timesteps = st.sidebar.number_input(
        "Simulation Days",
        min_value=10,
        max_value=3650,
        value=365,
        step=30,
        help="⏱️ Number of days to simulate. 365 = 1 year, 1095 = 3 years. Longer simulations show token economics maturation but take more time to run."
    )
    
    runs = st.sidebar.number_input(
        "Monte Carlo Runs",
        min_value=1,
        max_value=10,
        value=1,
        help="🎲 Number of simulation runs for statistical analysis. Multiple runs show variability in outcomes. Start with 1 for speed, use 3-5 for research."
    )

    save_results = st.sidebar.checkbox(
        "Save results to data/",
        value=True,
        help="When enabled, saves raw and processed data, a summary report, and params.json to a unique run directory under data/."
    )

    export_charts_html = st.sidebar.checkbox(
        "Export charts as HTML",
        value=False,
        help="If enabled (and saving results), exports each chart as a lightweight HTML file to the run's charts/ folder."
    )
    
    # Build parameter dictionary
    params = config_params.copy()
    params.update({
        'initial_node_amount': [initial_nodes],
        'resource_unit_price': [resource_price],
        'network_resource_demand_growth_rate': [demand_growth / 100],
        'apr_threshold': [apr_target],
        'emission_policy': [emission_policy],
        'token_market_scenario': [token_market_scenario],
        'token_speculation_factor': [speculation_factor],
        'utilization_controller_enabled': [bool(utilization_controller)],
        'resource_price_adjustment_enabled': [bool(dynamic_pricing)],
        # New essential business parameters
        'node_setup_cost': [node_setup_cost],
        'node_revenue_share': [node_revenue_share / 100],  # Convert back to decimal
        'foundation_revenue_share': [foundation_revenue_share / 100],  # Convert back to decimal
        'buyback_and_burn_revenue_share': [max(0, remaining_revenue) / 100],  # Calculated automatically
        'initial_network_resource_demand': [initial_network_demand],
        'foundation_cash_burn_rate': [foundation_cash_burn],
        'initial_foundation_cash_reserves': [foundation_cash_reserves],
        # New token economics parameters
        'token_initial_total_supply': [token_total_supply],
        'token_initial_valuation': [token_initial_valuation],
        'incentive_token_allocation': [incentive_token_allocation / 100],
        'seller_token_allocation': [seller_token_allocation / 100],
        'idle_token_allocation': [max(0, remaining_allocation) / 100],
    })

    # Apply demand growth model params
    params['business_growth_scenario'] = [growth_scenario]
    if growth_scenario == 'custom_phases':
        # Store raw lists as the model expects direct list access
        params['business_growth_phases'] = phases
        params['business_demand_milestones'] = milestones
    
    if emission_policy == "per_device":
        params['emission_per_device_daily'] = [emission_per_device]
    
    if emission_policy == "bme":
        params['bme_burn_rate_multiplier'] = [bme_burn_multiplier]
        params['bme_mint_rate_multiplier'] = [bme_mint_multiplier]
    
    if utilization_controller:
        params['utilization_target'] = [utilization_target / 100]
    
    if dynamic_pricing:
        params['resource_price_utilization_sensitivity'] = [price_sensitivity]
        params['resource_pricing_model'] = ['utilization_based']
    
    # Add advanced parameters
    params['node_growth_cap'] = [node_growth_cap]
    params['node_token_stake'] = [node_token_stake]  
    params['node_reliability'] = [node_reliability / 100]  # Convert back to decimal
    
    return params, timesteps, runs, save_results, export_charts_html

def run_simulation(params, timesteps, runs):
    """Run the simulation with given parameters"""
    try:
        model = Model(
            initial_state=initial_state,
            params=params,
            state_update_blocks=state_update_blocks
        )
        simulation = Simulation(model=model, timesteps=timesteps, runs=runs)
        
        with st.spinner(f"Running simulation ({timesteps} days, {runs} run(s))..."):
            result = simulation.run()

        df_raw = pd.DataFrame(result)
        df_processed = run.postprocessing(df_raw)
        return df_processed, df_raw, None
        
    except Exception as e:
        return None, None, str(e)

def create_plotly_chart(df, x_col, y_cols, title, y_title, log_scale=False):
    """Create a Plotly chart with multiple y series"""
    fig = go.Figure()
    
    if isinstance(y_cols, str):
        y_cols = [y_cols]
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, col in enumerate(y_cols):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                mode='lines',
                name=col.replace('_', ' ').title(),
                line=dict(color=colors[i % len(colors)])
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Days",
        yaxis_title=y_title,
        template="plotly_white",
        height=400
    )
    
    # Guard log scale when any series has non-positive values
    if log_scale:
        try:
            has_non_positive = False
            for col in y_cols:
                if col in df.columns:
                    series_min = pd.to_numeric(df[col], errors='coerce').min()
                    if pd.isna(series_min) or series_min <= 0:
                        has_non_positive = True
                        break
            if not has_non_positive:
                fig.update_yaxes(type="log")
        except Exception:
            # Fallback to linear without failing the chart
            pass
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🚀 DePIN Simulator</div>', unsafe_allow_html=True)
    st.markdown("**Decentralized Physical Infrastructure Network Token Economics Modeling**")
    
    # Quick info box
    with st.expander("ℹ️ What is DePIN? (Click to expand)"):
        st.markdown("""
        **DePIN** = **De**centralized **P**hysical **I**nfrastructure **N**etworks
        
        These are token-incentivized networks where people run physical hardware (nodes) to provide real-world services:
        
        - **🗄️ Storage Networks**: Filecoin, Arweave (decentralized storage)
        - **📡 Wireless Networks**: Helium (IoT connectivity), WiFi hotspots  
        - **💻 Compute Networks**: Akash, Render (decentralized computing)
        - **🚗 Mobility Networks**: DIMO (vehicle data), ride-sharing protocols
        
        **Key Challenge**: Design token economics that attract enough hardware operators while keeping the network economically sustainable.
        
        **This Simulator**: Models the relationship between token emissions, node profitability, network demand, and long-term sustainability.
        """)
    
    # Quick start tip
    st.info("💡 **First time?** Select 'Founder Scenario Example' from the sidebar, click 'Run Simulation', then explore the tabs to understand your DePIN economics!")
    
    # Create input controls and get parameters
    params, timesteps, runs, save_results, export_charts_html = create_parameter_inputs()
    
    # Run simulation button
    if st.sidebar.button("▶️ Run Simulation", type="primary"):
        
        # Run simulation
        df, df_raw, error = run_simulation(params, timesteps, runs)
        
        if error:
            st.error(f"❌ Simulation Error: {error}")
            return
        
        if df is None or df.empty:
            st.error("❌ No simulation data generated")
            return
        
        # Save outputs if enabled
        if save_results:
            run_dir = create_ui_run_directory(params)
            save_ui_outputs(run_dir, df_raw if df_raw is not None else df, df, params, timesteps, runs)

        # Store results in session state
        st.session_state['df'] = df
        st.session_state['params'] = params
        st.session_state['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if save_results:
            st.session_state['run_dir'] = run_dir
            st.session_state['export_charts_html'] = export_charts_html
    
    # Display results if available
    if 'df' in st.session_state:
        df = st.session_state['df']
        
        # Success message
        msg = f"✅ Simulation completed successfully! Generated {len(df)} data points"
        if 'run_dir' in st.session_state:
            msg += f" — Saved to {os.path.basename(st.session_state['run_dir'])}"
        st.success(msg)
        
        # Quick metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            final_nodes = df['node_amount'].iloc[-1]
            st.metric("Final Node Count", f"{final_nodes:,.0f}")
        
        with col2:
            final_price = df['dex_token_price'].iloc[-1]
            st.metric("Final Token Price", f"${final_price:.6f}")
        
        with col3:
            max_apr = df['node_apr'].max()
            st.metric("Max APR", f"{max_apr:.1f}%")
        
        with col4:
            final_utilization = df['network_resource_demand_supply_ratio'].iloc[-1]
            st.metric("Final Utilization", f"{final_utilization:.1%}")
        
        # Create tabs for organized visualization
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Network Metrics", 
            "💰 Economics", 
            "🪙 Token Metrics", 
            "🎯 Founder Dashboard",
            "📊 Data Export"
        ])
        
        with tab1:
            st.markdown("### Network Performance Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Network Resource Demand
                fig1 = create_plotly_chart(
                    df, 'timestep', 'network_resource_demand',
                    'Network Resource Demand', 'Resource Units'
                )
                st.plotly_chart(fig1, use_container_width=True)
                save_plotly_fig(fig1, "network_resource_demand.html")
                
                # Network Utilization
                fig2 = create_plotly_chart(
                    df, 'timestep', 'network_resource_demand_supply_ratio',
                    'Network Utilization Ratio', 'Utilization %'
                )
                st.plotly_chart(fig2, use_container_width=True)
                save_plotly_fig(fig2, "network_utilization_ratio.html")
            
            with col2:
                # Node Count
                fig3 = create_plotly_chart(
                    df, 'timestep', 'node_amount',
                    'Node Count Over Time', 'Number of Nodes'
                )
                st.plotly_chart(fig3, use_container_width=True)
                save_plotly_fig(fig3, "node_count.html")
                
                # Node Change Δ (nodes/day)
                if 'node_change_amount' in df.columns:
                    node_change_series = 'node_change_amount'
                else:
                    # Derive delta if not available
                    df['node_change_delta'] = df['node_amount'].diff().fillna(0)
                    node_change_series = 'node_change_delta'
                fig_delta = create_plotly_chart(
                    df, 'timestep', node_change_series,
                    'Daily Node Change (Δ)', 'Nodes / Day'
                )
                st.plotly_chart(fig_delta, use_container_width=True)
                save_plotly_fig(fig_delta, "node_change_delta.html")

                # Resource Pricing (if available)
                if 'resource_unit_price_current' in df.columns:
                    fig4 = create_plotly_chart(
                        df, 'timestep', ['resource_unit_price_current'],
                        'Dynamic Resource Pricing', 'Price per Unit ($)'
                    )
                    # Add base price line
                    base_price = params['resource_unit_price'][0]
                    fig4.add_hline(y=base_price, line_dash="dash", line_color="red", 
                                 annotation_text="Base Price")
                    st.plotly_chart(fig4, use_container_width=True)
                    save_plotly_fig(fig4, "dynamic_resource_pricing.html")
        
        with tab2:
            st.markdown("### Economic Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Node APR
                fig5 = create_plotly_chart(
                    df, 'timestep', 'node_apr',
                    'Node Annual Percentage Return', 'APR (%)'
                )
                # Add target APR line
                target_apr = params['apr_threshold'][0]
                fig5.add_hline(y=target_apr, line_dash="dash", line_color="green",
                             annotation_text="Target APR")
                st.plotly_chart(fig5, use_container_width=True)
                save_plotly_fig(fig5, "node_apr.html")
                
                # Node Profit
                fig6 = create_plotly_chart(
                    df, 'timestep', 'node_profit',
                    'Node Profit', 'Profit ($)', log_scale=True
                )
                st.plotly_chart(fig6, use_container_width=True)
                save_plotly_fig(fig6, "node_profit.html")
            
            with col2:
                # Node Revenue Components
                fig7 = create_plotly_chart(
                    df, 'timestep', ['node_network_revenue', 'node_incentive_revenue'],
                    'Node Revenue Components', 'Revenue ($)'
                )
                st.plotly_chart(fig7, use_container_width=True)
                save_plotly_fig(fig7, "node_revenue_components.html")
                
                # Foundation Cash Reserves
                fig8 = create_plotly_chart(
                    df, 'timestep', 'foundation_cash_reserves',
                    'Foundation Cash Reserves', 'Reserves ($)'
                )
                st.plotly_chart(fig8, use_container_width=True)
                save_plotly_fig(fig8, "foundation_cash_reserves.html")

                # Node Expenditures
                if 'node_expenditures' in df.columns:
                    fig_exp = create_plotly_chart(
                        df, 'timestep', 'node_expenditures',
                        'Node Expenditures', 'Costs ($)'
                    )
                    st.plotly_chart(fig_exp, use_container_width=True)
                    save_plotly_fig(fig_exp, "node_expenditures.html")
        
        with tab3:
            st.markdown("### Token Economics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Token Price (Market vs Fundamental)
                price_cols = ['dex_token_price']
                if 'fundamental_token_price' in df.columns:
                    price_cols.append('fundamental_token_price')
                
                fig9 = create_plotly_chart(
                    df, 'timestep', price_cols,
                    'Token Price: Market vs Fundamental', 'Price ($)', log_scale=True
                )
                st.plotly_chart(fig9, use_container_width=True)
                save_plotly_fig(fig9, "token_price_market_vs_fundamental.html")
                
                # Token Staked Supply
                if 'token_staked_supply' in df.columns and 'token_total_supply' in df.columns:
                    df['staked_percentage'] = (df['token_staked_supply'] / df['token_total_supply']) * 100
                    fig10 = create_plotly_chart(
                        df, 'timestep', 'staked_percentage',
                        'Token Staked Supply', 'Staked (%)'
                    )
                    st.plotly_chart(fig10, use_container_width=True)
                    save_plotly_fig(fig10, "token_staked_percentage.html")
            
            with col2:
                # Token Supply Components
                supply_cols = []
                if 'token_burned_supply_cum' in df.columns:
                    df['burned_percentage'] = (df['token_burned_supply_cum'] / df['token_total_supply'].iloc[0]) * 100
                    supply_cols.append('burned_percentage')
                if 'token_minted_supply_cum' in df.columns:
                    df['minted_percentage'] = (df['token_minted_supply_cum'] / df['token_total_supply'].iloc[0]) * 100
                    supply_cols.append('minted_percentage')
                
                if supply_cols:
                    fig11 = create_plotly_chart(
                        df, 'timestep', supply_cols,
                        'Token Burn & Mint Activity', '% of Initial Supply'
                    )
                    st.plotly_chart(fig11, use_container_width=True)
                    save_plotly_fig(fig11, "token_burn_mint_activity.html")
                
                # Liquidity Pool Reserves
                fig12 = create_plotly_chart(
                    df, 'timestep', ['dex_tokens', 'dex_usdc'],
                    'Liquidity Pool Reserves', 'Tokens / USDC', log_scale=True
                )
                st.plotly_chart(fig12, use_container_width=True)
                save_plotly_fig(fig12, "liquidity_pool_reserves.html")

            # New: Cumulative Token Vesting (Incentives vs Seller)
            st.markdown("#### Cumulative Token Vesting")
            vest_cols = []
            if 'token_incentives_vested_cum' in df.columns:
                vest_cols.append('token_incentives_vested_cum')
            if 'token_seller_vested_cum' in df.columns:
                vest_cols.append('token_seller_vested_cum')
            if vest_cols:
                fig_vest = create_plotly_chart(
                    df, 'timestep', vest_cols,
                    'Cumulative Token Vesting', 'Tokens'
                )
                st.plotly_chart(fig_vest, use_container_width=True)
                save_plotly_fig(fig_vest, "cumulative_token_vesting.html")

            # New: Token Ecosystem Supply (absolute)
            if 'token_total_supply' in df.columns and 'token_circulating_supply' in df.columns:
                fig_supply_abs = create_plotly_chart(
                    df, 'timestep', ['token_total_supply', 'token_circulating_supply'],
                    'Token Ecosystem Supply (Absolute)', 'Tokens'
                )
                st.plotly_chart(fig_supply_abs, use_container_width=True)
                save_plotly_fig(fig_supply_abs, "token_ecosystem_supply_absolute.html")

                # New: Token Ecosystem Supply (% of initial)
                initial_supply = df['token_total_supply'].iloc[0] if df['token_total_supply'].iloc[0] != 0 else 1
                df['total_supply_pct_initial'] = (df['token_total_supply'] / initial_supply) * 100
                df['circulating_supply_pct_initial'] = (df['token_circulating_supply'] / initial_supply) * 100
                fig_supply_pct = create_plotly_chart(
                    df, 'timestep', ['total_supply_pct_initial', 'circulating_supply_pct_initial'],
                    'Token Ecosystem Supply (% of Initial)', '% of Initial'
                )
                st.plotly_chart(fig_supply_pct, use_container_width=True)
                save_plotly_fig(fig_supply_pct, "token_ecosystem_supply_percent.html")
        
        with tab4:
            st.markdown("### 🎯 Founder Dashboard")
            st.markdown("*Protocol optimization scoring and sustainability analysis*")
            
            # Import and calculate optimal control theory metrics
            from model.cost_functions import calculate_step_cost, DePINProtocolTargets, CostWeights
            
            # Calculate protocol score using optimal control theory
            final_data = df.iloc[-1].to_dict()
            previous_data = df.iloc[-2].to_dict() if len(df) > 1 else final_data
            
            # Calculate cost components for the final state
            targets = DePINProtocolTargets()
            weights = CostWeights()
            cost_result = calculate_step_cost(final_data, previous_data, targets, weights)
            
            # Convert cost to score (0-100, where 100 is perfect)
            total_cost = cost_result['total_cost']
            protocol_score = max(0, min(100, 100 * (1 / (1 + total_cost))))
            
            # Protocol Score Header
            st.markdown("### 🏆 Protocol Performance Score")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Large protocol score display
                score_color = "green" if protocol_score >= 75 else "orange" if protocol_score >= 50 else "red"
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border: 2px solid {score_color}; border-radius: 10px; background-color: rgba(255,255,255,0.1);">
                    <h1 style="color: {score_color}; margin: 0; font-size: 3rem;">{protocol_score:.1f}</h1>
                    <p style="margin: 5px 0 0 0; color: {score_color}; font-size: 1.2rem;">Protocol Score</p>
                    <p style="margin: 0; font-size: 0.9rem; color: gray;">Based on Optimal Control Theory J(x₀,π)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric(
                    "Score Grade",
                    "A" if protocol_score >= 90 else "B" if protocol_score >= 75 else "C" if protocol_score >= 60 else "D" if protocol_score >= 40 else "F",
                    help="Letter grade based on protocol performance"
                )
            
            with col3:
                trend = "improving" if len(df) > 10 else "stable"
                st.metric(
                    "Trend",
                    trend.title(),
                    help="Overall protocol performance trend"
                )
            
            # Component Breakdown
            st.markdown("### 📊 Performance Component Analysis")
            st.markdown("*Each component contributes to the overall protocol score based on optimal control theory*")
            
            # Component scores (convert costs to 0-100 scores)
            price_score = max(0, min(100, 100 * (1 / (1 + cost_result['price_stability_cost']))))
            util_score = max(0, min(100, 100 * (1 / (1 + cost_result['utilization_efficiency_cost']))))
            foundation_score = max(0, min(100, 100 * (1 / (1 + cost_result['foundation_sustainability_cost']))))
            node_score = max(0, min(100, 100 * (1 / (1 + cost_result['node_profitability_cost']))))
            decentralization_score = max(0, min(100, 100 * (1 / (1 + cost_result['decentralization_cost']))))
            
            # Component metrics with weights
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🎯 Price Stability** (30% weight)")
                st.progress(price_score / 100)
                st.metric("Score", f"{price_score:.1f}/100", help="Token price stability and predictable growth")
                
                st.markdown("**⚡ Network Efficiency** (25% weight)")
                st.progress(util_score / 100)
                st.metric("Score", f"{util_score:.1f}/100", help="Network utilization and resource efficiency")
            
            with col2:
                st.markdown("**🏛️ Foundation Health** (20% weight)")
                st.progress(foundation_score / 100)
                st.metric("Score", f"{foundation_score:.1f}/100", help="Protocol sustainability and runway")
                
                st.markdown("**💰 Node Economics** (15% weight)")  
                st.progress(node_score / 100)
                st.metric("Score", f"{node_score:.1f}/100", help="Node operator profitability and retention")
            
            with col3:
                st.markdown("**🌐 Decentralization** (10% weight)")
                st.progress(decentralization_score / 100) 
                st.metric("Score", f"{decentralization_score:.1f}/100", help="Network decentralization and node count")
            
            # Key Sustainability Metrics
            st.markdown("### 💼 Business Sustainability Metrics")
            
            # Calculate key founder metrics
            total_revenue = final_data.get('network_revenue', 0)
            foundation_reserves = final_data.get('foundation_cash_reserves', 0)
            foundation_expenditures = final_data.get('foundation_expenditures', 0)
            utilization = final_data.get('network_resource_demand_supply_ratio', 0)
            node_apr = final_data.get('node_apr', 0)
            node_count = final_data.get('node_amount', 0)
            
            # Foundation runway
            monthly_burn = foundation_expenditures * 30 if foundation_expenditures > 0 else 1
            runway_months = foundation_reserves / monthly_burn if monthly_burn > 0 else float('inf')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric(
                    "Foundation Runway",
                    f"{runway_months:.1f} months" if runway_months < 1000 else "∞",
                    help="Time until foundation runs out of funds at current burn rate"
                )
                if runway_months > 24:
                    st.success("✅ Strong financial position")
                elif runway_months > 12:
                    st.warning("⚠️ Monitor cash flow")
                else:
                    st.error("❌ Critical: Low runway")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric(
                    "Network Utilization",
                    f"{utilization:.1%}",
                    help="Network resource utilization efficiency"
                )
                if 0.7 <= utilization <= 0.85:
                    st.success("✅ Optimal range")
                elif 0.5 <= utilization <= 0.95:
                    st.warning("⚠️ Acceptable")
                else:
                    st.error("❌ Needs optimization")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric(
                    "Node Economics",
                    f"{node_apr:.1f}% APR",
                    help="Node operator annual percentage return"
                )
                if 15 <= node_apr <= 30:
                    st.success("✅ Healthy returns")
                elif 10 <= node_apr <= 40:
                    st.warning("⚠️ Monitor trends")
                else:
                    st.error("❌ Unsustainable")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Token Economics Health
            if 'fundamental_token_price' in df.columns:
                token_price = final_data['dex_token_price']
                fundamental_price = final_data['fundamental_token_price']
                speculation_ratio = token_price / fundamental_price if fundamental_price > 0 else 1
                
                st.markdown("### Token Market Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Speculation Premium",
                        f"{((speculation_ratio - 1) * 100):+.1f}%",
                        help="How much market price exceeds fundamental value"
                    )
                
                with col2:
                    st.metric(
                        "Price Stability Ratio",
                        f"{min(speculation_ratio, 1/speculation_ratio):.2f}",
                        help="Closeness to fundamental value (1.0 = perfect)"
                    )
            
            # Protocol Score Over Time
            st.markdown("### 📈 Protocol Performance Over Time")
            
            if len(df) > 1:
                # Calculate protocol score for each timestep
                protocol_scores = []
                for i in range(len(df)):
                    current_state = df.iloc[i].to_dict()
                    prev_state = df.iloc[i-1].to_dict() if i > 0 else current_state
                    step_cost = calculate_step_cost(current_state, prev_state, targets, weights)
                    step_score = max(0, min(100, 100 * (1 / (1 + step_cost['total_cost']))))
                    protocol_scores.append(step_score)
                
                # Create protocol score chart
                fig_score = go.Figure()
                fig_score.add_trace(go.Scatter(
                    x=df['timestep'],
                    y=protocol_scores,
                    mode='lines',
                    name='Protocol Score',
                    line=dict(color='#1f77b4', width=3)
                ))
                
                # Add target zone
                fig_score.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Target (75+)")
                fig_score.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Acceptable (50+)")
                
                fig_score.update_layout(
                    title="Protocol Performance Score Timeline",
                    xaxis_title="Days",
                    yaxis_title="Protocol Score (0-100)",
                    template="plotly_white",
                    height=400,
                    yaxis_range=[0, 100]
                )
                
                st.plotly_chart(fig_score, use_container_width=True)
            
            # Optimization Recommendations
            st.markdown("### 🎯 Optimization Recommendations")
            st.markdown("*Based on optimal control theory analysis of protocol components*")
            
            recommendations = []
            
            # Price stability recommendations
            if price_score < 70:
                recommendations.append("🎯 **Price Stability**: Consider implementing price stabilization mechanisms or reducing speculation factors")
            
            # Utilization recommendations  
            if util_score < 70:
                if utilization < 0.7:
                    recommendations.append("⚡ **Network Efficiency**: Increase demand growth rate or reduce node growth to improve utilization")
                elif utilization > 0.85:
                    recommendations.append("⚡ **Network Efficiency**: Allow faster node growth to meet excess demand")
            
            # Foundation sustainability
            if foundation_score < 70:
                if runway_months < 24:
                    recommendations.append("🏛️ **Foundation Health**: Critical - increase foundation revenue share or reduce operational costs")
                else:
                    recommendations.append("🏛️ **Foundation Health**: Monitor cash flow and diversify revenue streams")
            
            # Node economics
            if node_score < 70:
                if node_apr < 15:
                    recommendations.append("💰 **Node Economics**: Increase node revenue share or reduce setup costs to attract operators")
                elif node_apr > 40:
                    recommendations.append("💰 **Node Economics**: Reduce emissions or increase competition to prevent unsustainable returns")
            
            # Decentralization
            if decentralization_score < 70:
                recommendations.append("🌐 **Decentralization**: Encourage more node participation through incentives or lower barriers to entry")
            
            # Overall protocol score recommendations
            if protocol_score >= 90:
                st.success("🎉 **Excellent!** Your protocol is performing exceptionally well across all metrics!")
            elif protocol_score >= 75:
                st.success("✅ **Strong Performance** - Your protocol is well-optimized with minor areas for improvement")
            elif protocol_score >= 60:
                st.warning("⚠️ **Good Foundation** - Several optimization opportunities identified")
            elif protocol_score >= 40:
                st.warning("🔧 **Needs Attention** - Multiple areas require optimization")
            else:
                st.error("🚨 **Critical Issues** - Protocol requires significant redesign")
            
            if recommendations:
                for rec in recommendations:
                    st.info(rec)
            
            # Advanced Insights
            st.markdown("### 🧠 Advanced Protocol Insights")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Cost Function Details**")
                st.json({
                    "Total Cost": f"{cost_result['total_cost']:.4f}",
                    "Price Stability Cost": f"{cost_result['price_stability_cost']:.4f}",
                    "Utilization Cost": f"{cost_result['utilization_efficiency_cost']:.4f}",
                    "Foundation Cost": f"{cost_result['foundation_sustainability_cost']:.4f}",
                    "Node Profitability Cost": f"{cost_result['node_profitability_cost']:.4f}",
                    "Decentralization Cost": f"{cost_result['decentralization_cost']:.4f}"
                })
            
            with col2:
                st.markdown("**Target Parameters**")
                st.json({
                    "Target Price Growth": f"{targets.target_price_growth_rate:.3f} daily",
                    "Target Utilization": f"{targets.target_utilization_rate:.1%}",
                    "Target Node APR": f"{targets.target_node_apr:.1f}%",
                    "Min Foundation Runway": f"{targets.min_foundation_runway_days} days",
                    "Min Decentralization": f"{targets.min_network_decentralization} nodes"
                })
        
        with tab5:
            st.markdown("### 📊 Data Export & Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download data
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV Data",
                    data=csv_data,
                    file_name=f"depin_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Summary statistics
                st.markdown("#### Summary Statistics")
                key_metrics = ['node_amount', 'dex_token_price', 'node_apr', 'network_resource_demand_supply_ratio']
                summary_data = df[key_metrics].describe()
                st.dataframe(summary_data)
            
            with col2:
                # Configuration used
                st.markdown("#### Configuration Used")
                config_display = {
                    "Emission Policy": params['emission_policy'][0],
                    "Initial Nodes": f"{params['initial_node_amount'][0]:,}",
                    "Resource Price": f"${params['resource_unit_price'][0]:.6f}",
                    "Demand Growth": f"{params['network_resource_demand_growth_rate'][0]*100:.1f}%",
                    "Target APR": f"{params['apr_threshold'][0]:.0f}%",
                    "Simulation Days": timesteps,
                    "Timestamp": st.session_state['timestamp']
                }
                
                for key, value in config_display.items():
                    st.text(f"{key}: {value}")
            
            # Raw data table (last 10 rows)
            st.markdown("#### Raw Data Sample (Last 10 Timesteps)")
            st.dataframe(df.tail(10))
    
    else:
        # Instructions when no simulation has been run
        st.info("👈 Configure parameters in the sidebar and click '▶️ Run Simulation' to begin!")
        
        st.markdown("### 📚 About DePIN Simulator")
        st.markdown("""
        This tool models **Decentralized Physical Infrastructure Networks (DePIN)** token economics using:
        
        - **radCAD Framework**: Advanced dynamical systems modeling
        - **Multiple Emission Policies**: Linear, per-device, and BME (Burn-and-Mint Equilibrium)
        - **Realistic Network Dynamics**: Node growth, utilization-based supply control, dynamic pricing
        - **Founder-Focused Metrics**: Business validation, sustainability analysis, token health scores
        
        **Key Features:**
        - 🎯 Founder validation dashboard with actionable insights
        - 📈 Utilization-based supply controller (prevents network congestion)  
        - 💰 Dynamic resource pricing (market-driven pricing mechanisms)
        - 🪙 Separation of fundamental vs speculative token value
        - 📊 Interactive charts with Plotly visualization
        - 💾 Data export for further analysis
        """)
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🚀 For DePIN Founders")
            st.markdown("""
            - Validate business model assumptions
            - Optimize token emission strategies  
            - Assess network sustainability
            - Plan growth phases and milestones
            """)
        
        with col2:
            st.markdown("#### 🔬 For Researchers")
            st.markdown("""
            - Compare emission policies
            - Analyze network dynamics
            - Study token price mechanisms
            - Export data for publications
            """)
        
        with col3:
            st.markdown("#### 🏗️ For Protocol Designers")
            st.markdown("""
            - Tune economic parameters
            - Model different scenarios
            - Stress-test assumptions
            - Design sustainable tokenomics
            """)

if __name__ == "__main__":
    main()