# Dependences
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from tqdm import tqdm
import os
from datetime import datetime

# radCAD
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

# Experiments
from model import run
pd.options.display.float_format = '{:.5f}'.format

from model.sys_params import sys_params, initial_values
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks

# Set the number of timesteps and runs for the simulation
TIMESTEPS = 365*10  # Full 10-year simulation
MONTE_CARLO_RUNS = 1

# Data export configuration
SAVE_DATA = True  # Set to False to disable data export
SHOW_PLOTS = True  # Set to False to disable plot display

model = Model(initial_state=initial_state, params=sys_params, state_update_blocks=state_update_blocks)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)

def create_data_directory():
    """Create organized data directory structure for simulation results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    emission_policy = sys_params['emission_policy'][0]
    
    # Get configuration name if available
    config_name = "unknown"
    if '_metadata' in sys_params:
        config_name = sys_params['_metadata'].get('name', 'unknown').lower().replace(' ', '_')
    
    # Create base data directory
    base_dir = "data"
    os.makedirs(base_dir, exist_ok=True)
    
    # Find next run number for this configuration
    run_number = 1
    config_pattern = f"{config_name}_run_"
    
    if os.path.exists(base_dir):
        existing_dirs = [d for d in os.listdir(base_dir) if d.startswith(config_pattern)]
        if existing_dirs:
            run_numbers = []
            for d in existing_dirs:
                try:
                    num_part = d.replace(config_pattern, '').split('_')[0]
                    run_numbers.append(int(num_part))
                except:
                    continue
            if run_numbers:
                run_number = max(run_numbers) + 1
    
    # Create numbered run directory
    run_name = f"{config_name}_run_{run_number:03d}_{timestamp}"
    sim_dir = os.path.join(base_dir, run_name)
    
    # Create subdirectories for organized data storage
    os.makedirs(os.path.join(sim_dir, "charts"), exist_ok=True)
    os.makedirs(os.path.join(sim_dir, "data"), exist_ok=True) 
    os.makedirs(os.path.join(sim_dir, "reports"), exist_ok=True)
    
    return sim_dir

def save_summary_report(data_dir, df, rdf):
    """Generate and save simulation summary report"""
    emission_policy = sys_params['emission_policy'][0]
    
    # Get run information from directory name
    run_info = os.path.basename(data_dir)
    config_name = sys_params.get('_metadata', {}).get('name', 'Unknown Configuration')
    config_desc = sys_params.get('_metadata', {}).get('description', 'No description available')
    
    summary_text = f"""
DePIN Simulator - Simulation Summary Report
==========================================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Run Directory: {run_info}
Configuration: {config_name}
Description: {config_desc}

Simulation Parameters:
Duration: {TIMESTEPS:,} timesteps ({TIMESTEPS/365:.1f} years)
Monte Carlo Runs: {MONTE_CARLO_RUNS}
Emission Policy: {emission_policy}

Key Final Metrics (at simulation end):
=====================================
Network Metrics:
- Node Count: {rdf.node_amount.iloc[-1]:,.0f} nodes
- Network Utilization: {rdf.network_resource_demand_supply_ratio.iloc[-1]:.1%}
- Network Demand: {rdf.network_resource_demand.iloc[-1]:,.0f} resource units

Token Economics:
- Token Price: ${rdf.dex_token_price.iloc[-1]:.6f}
- Total Token Supply: {rdf.token_total_supply.iloc[-1]:,.0f} tokens
- Circulating Supply: {rdf.token_circulating_supply.iloc[-1]:,.0f} tokens
- Tokens Staked: {rdf.token_staked_supply.iloc[-1]:,.0f} tokens ({rdf.token_staked_supply.iloc[-1]/initial_values['token_initial_total_supply']*100:.1f}%)

Node Economics:
- Node APR: {rdf.node_apr.iloc[-1]:.1f}%
- Node Profit: ${rdf.node_profit.iloc[-1]:,.2f} per day
- Network Revenue: ${rdf.node_network_revenue.iloc[-1]:,.2f} per day
- Incentive Revenue: ${rdf.node_incentive_revenue.iloc[-1]:,.2f} per day

Foundation:
- Cash Reserves: ${rdf.foundation_cash_reserves.iloc[-1]:,.0f}
- Daily Cash Flow: ${(rdf.foundation_revenue.iloc[-1] - rdf.foundation_expenditures.iloc[-1]):,.2f}

APR Analysis:
=============
- Max APR: {rdf.node_apr.max():.1f}%
- Min APR: {rdf.node_apr.min():.1f}%
- Average APR: {rdf.node_apr.mean():.1f}%
- APR Volatility (std): {rdf.node_apr.std():.1f}%
- Timesteps with APR > 100%: {(rdf.node_apr > 100).sum()}

Critical Validation:
===================
- Max timesteps with zero nodes: {(rdf.node_amount == 0).sum()}
- Network utilization >100%: {(rdf.network_resource_demand_supply_ratio > 1.0).sum()} timesteps
- Negative token price: {(rdf.dex_token_price <= 0).sum()} timesteps
- Foundation bankruptcy risk: {'Yes' if rdf.foundation_cash_reserves.min() < 1000000 else 'No'}

Files Generated:
===============
- data/simulation_results.csv: Complete simulation data
- data/simulation_results_raw.csv: Raw radCAD output
- charts/simulation_charts.png: All visualization charts
- reports/summary_report.txt: This summary report
"""
    
    with open(os.path.join(data_dir, "reports", "summary_report.txt"), "w") as f:
        f.write(summary_text)
    
    return summary_text

def main():
    print("🚀 Starting DePIN Simulation...")
    print(f"📊 Simulating {TIMESTEPS:,} timesteps ({TIMESTEPS/365:.1f} years) with {MONTE_CARLO_RUNS} run(s)")
    print("⚡ Cost function analysis included (visualization coming with Streamlit UI)")
    
    # Create data directory if saving is enabled
    if SAVE_DATA:
        data_dir = create_data_directory()
        print(f"📁 Data will be saved to: {data_dir}")
    print()

    # run the simulation with progress bar
    print("🔄 Running simulation...")
    result = simulation.run()
    print("✅ Simulation complete!")
    
    print("📈 Generating charts...")
    df = pd.DataFrame(result)
    
    # Export raw data if saving is enabled
    if SAVE_DATA:
        print("💾 Saving simulation data...")
        df.to_csv(os.path.join(data_dir, "data", "simulation_results_raw.csv"), index=False)
        
        # Also save postprocessed data for the first subset (since we typically have only one)
        rdf = run.postprocessing(df[df['subset'] == 0] if len(df['subset'].unique()) > 0 else df)
        rdf.to_csv(os.path.join(data_dir, "data", "simulation_results.csv"), index=False)
    # get amount of distinct subsets in the simulation
    subsets = df['subset'].unique()

    # prepare the plots
    fig, axarr = plt.subplots(4,4, figsize=(16,12))
    custom_lines = [Line2D([0], [0], linestyle='solid', color='black'),
                    Line2D([0], [0], linestyle='dashed', color='black'),
                    Line2D([0], [0], linestyle=':', color='black'),]

    for subset in subsets:
        subset_df = df[df['subset'] == subset]

        # get the destinctive parameters from sys_params for the subset if they have more than one values in their list
        sweep_params = {key: value for key, value in sys_params.items() if len(value) > 1}
        # compose the legend text for this subset
        legend_text = ''
        for key, value in sweep_params.items():
            # format key
            key_formatted = key.split("network_")[1] if "network_" in key else key
            key_formatted = key_formatted.replace("_"," ")
            
            # construct the legend text
            try:
                legend_text += f'{key_formatted}: {"{:.2e}".format(value[subset])}; '
            except:
                try:
                    legend_text += f'{key_formatted}: {value[subset]}; '
                except:
                    pass
                pass

        rdf = run.postprocessing(subset_df)

        # Network Resource Demand
        axarr[0,0].plot(rdf.timestep, rdf.network_resource_demand, label=legend_text, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,0].set_title('Network Resource Demand / Resource Units')
        axarr[0,0].grid('on', which='both')
        axarr[0,0].legend(loc=1, prop={'size': 5})

         # Network Utilization
        axarr[1,0].plot(rdf.timestep, rdf.network_resource_demand_supply_ratio, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[1,0].set_title('Network Demand / Supply Ratio / -')
        axarr[1,0].grid('on', which='both')

        # Node Amounts
        axarr[2,0].plot(rdf.timestep, rdf.node_amount, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[2,0].set_title('Node Amounts / Nodes')
        axarr[2,0].grid('on', which='both')
        axarr[2,0].set_yscale('log')

        # Node Change Amounts
        axarr[3,0].plot(rdf.timestep, rdf.node_change_amount, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[3,0].set_title('Node Change Amounts / Nodes')
        axarr[3,0].grid('on', which='both')

        # Node APR
        axarr[0,1].plot(rdf.timestep, rdf.node_apr, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,1].set_title('Node APR / %')
        axarr[0,1].set_xlabel('Days')
        axarr[0,1].grid('on', which='both')

        # Node Profit
        axarr[1,1].plot(rdf.timestep, rdf.node_profit, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[1,1].set_title('Node Profit / $')
        axarr[1,1].grid('on', which='both')
        axarr[1,1].set_yscale('log')

        # Node Network and Incentive Revenue 
        axarr[2,1].plot(rdf.timestep, rdf.node_network_revenue, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Network', linestyle='solid')
        axarr[2,1].plot(rdf.timestep, rdf.node_incentive_revenue, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Incentives', linestyle='dashed')
        axarr[2,1].set_title('Node Revenue / $')
        axarr[2,1].legend(custom_lines, ['Network', 'Incentives'])
        axarr[2,1].grid('on', which='both')
        axarr[2,1].set_yscale('log')

        # Node Expenditures
        axarr[3,1].plot(rdf.timestep, rdf.node_expenditures, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[3,1].set_title('Node Expenditures / $')
        axarr[3,1].set_xlabel('Days')
        axarr[3,1].grid('on', which='both')
        axarr[3,1].set_yscale('log')

        # DEX Token Price
        axarr[0,2].plot(rdf.timestep, rdf.dex_token_price, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,2].set_title('DEX Token Price / $')
        axarr[0,2].grid('on', which='both')
        axarr[0,2].set_yscale('log')

        # Liquidity Pool Reserves
        axarr[1,2].plot(rdf.timestep, rdf.dex_tokens, color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='solid')
        axarr[1,2].plot(rdf.timestep, rdf.dex_usdc, color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='dashed')
        axarr[1,2].set_title('Liquidity Pool Reserves / $')
        axarr[1,2].grid('on', which='both')
        axarr[1,2].set_yscale('log')
        axarr[1,2].legend(custom_lines, ['Token', 'USDC'])

        # Token Vesting
        axarr[2,2].plot(rdf.timestep, rdf.token_seller_vested_cum, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Seller Vested', linestyle='solid')
        axarr[2,2].plot(rdf.timestep, rdf.token_incentives_vested_cum, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Incentive Vested', linestyle='dashed')
        axarr[2,2].set_title('Cumulative Token Vesting / Tokens')
        axarr[2,2].legend(custom_lines, ['Seller Vested', 'Incentive Vested'])
        axarr[2,2].grid('on', which='both')

        # Token Staked Supply
        axarr[3,2].plot(rdf.timestep, rdf.token_staked_supply / initial_values['token_initial_total_supply']*100, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[3,2].set_title('Token Staked Supply / %')
        axarr[3,2].set_xlabel('Days')
        axarr[3,2].grid('on', which='both')

        # Foundation Financial Reserves
        axarr[0,3].plot(rdf.timestep, rdf.foundation_cash_reserves, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,3].set_title('Foundation Cash Reserves / $')
        axarr[0,3].grid('on', which='both')

        # Resource Unit Pricing (Dynamic vs Base)
        base_price = sys_params['resource_unit_price'][0]
        if 'resource_unit_price_current' in rdf.columns:
            axarr[1,3].plot(rdf.timestep, rdf.resource_unit_price_current, color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='solid', label='Current Price')
            axarr[1,3].axhline(y=base_price, color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='dashed', alpha=0.7, label='Base Price')
            axarr[1,3].set_title('Resource Unit Price / $ per Unit')
            axarr[1,3].legend(custom_lines, ['Current Price', 'Base Price'])
        else:
            # Fallback to foundation cash flow if resource pricing not available
            axarr[1,3].plot(rdf.timestep, rdf.foundation_revenue - rdf.foundation_expenditures, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
            axarr[1,3].set_title('Foundation Cash Flow / $')
        axarr[1,3].grid('on', which='both')

        # Token Mint & Burn Supply
        axarr[2,3].plot(rdf.timestep, rdf.token_burned_supply_cum / initial_values['token_initial_total_supply']*100, label='Burned', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='solid')
        axarr[2,3].plot(rdf.timestep, rdf.token_minted_supply_cum / initial_values['token_initial_total_supply']*100, label='Minted', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='dashed')
        axarr[2,3].set_title('Token Burn & Mint Supply / %')
        axarr[2,3].legend(custom_lines, ['Burned', 'Minted'])
        axarr[2,3].grid('on', which='both')

        # Token Ecosystem Supply
        axarr[3,3].plot(rdf.timestep, rdf.token_total_supply / initial_values['token_initial_total_supply']*100, label='Total Supply', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='solid')
        axarr[3,3].plot(rdf.timestep, rdf.token_circulating_supply / initial_values['token_initial_total_supply']*100, label='Circulating Supply', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='dashed')
        axarr[3,3].set_title('Token Ecosystem Supply / %')
        axarr[3,3].set_xlabel('Days')
        axarr[3,3].legend(custom_lines, ['Total Supply', 'Circulating Supply'])
        axarr[3,3].grid('on', which='both')

    plt.tight_layout()
    print("🎨 Charts generated successfully!")
    
    # Save charts if enabled
    if SAVE_DATA:
        print("🖼️ Saving charts...")
        plt.savefig(os.path.join(data_dir, "charts", "simulation_charts.png"), dpi=300, bbox_inches='tight')
        
        # Generate and save summary report
        print("📝 Generating summary report...")
        rdf = run.postprocessing(df[df['subset'] == 0] if len(df['subset'].unique()) > 0 else df)
        summary_text = save_summary_report(data_dir, df, rdf)
        
        print(f"✅ All data saved to: {data_dir}")
        print("\n" + "="*50)
        print("KEY SIMULATION RESULTS:")
        print("="*50)
        print(f"Final Node Count: {rdf.node_amount.iloc[-1]:,.0f}")
        print(f"Final Token Price: ${rdf.dex_token_price.iloc[-1]:.6f}")
        print(f"Max APR: {rdf.node_apr.max():.1f}%")
        print(f"Timesteps with APR >100%: {(rdf.node_apr > 100).sum()}")
        print(f"Network Utilization: {rdf.network_resource_demand_supply_ratio.iloc[-1]:.1%}")
        if 'resource_unit_price_current' in rdf.columns:
            base_price = sys_params['resource_unit_price'][0]
            final_price = rdf.resource_unit_price_current.iloc[-1]
            price_change = ((final_price - base_price) / base_price) * 100
            print(f"Resource Price: ${final_price:.6f} ({price_change:+.1f}% vs base)")
        print("="*50)
    
    # Show plots if enabled
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close()



    #rdf = run.postprocessing(df)
    

    # plot results
    """rdf.plot(x='timestep', y=['network_resource_demand', 'dex_tokens', 'dex_usdc', 'dex_token_price',
                            'token_incentives_vested', 'token_seller_vested', 'token_incentives_vested_cum',
                            'token_seller_vested_cum'], subplots=True, layout=(4, 2), figsize=(15, 10), title='DePIN Simulation Results')
    
    rdf.pivot(index='timestep', columns='subset', values=['node_amount']).plot(title='Node Amounts')
    rdf.pivot(index='timestep', columns='subset', values=['dex_token_price']).plot(title='Token Price')
    rdf.plot(x='timestep', y=['node_amount', 'node_change_amount', 'token_staked_supply', 'node_apr',
                                'node_network_revenue', 'node_incentive_revenue', 'node_profit', 'node_expenditures'], subplots=True, layout=(4, 2), figsize=(15, 10), title='DePIN Simulation Results')
    """

if __name__ == "__main__":
    main()

