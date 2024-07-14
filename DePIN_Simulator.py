# Dependences
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# radCAD
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

# Experiments
from model import run
pd.options.display.float_format = '{:.5f}'.format

from model.sys_params import sys_params
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks

# Set the number of timesteps and runs for the simulation
TIMESTEPS = 365 * 6
RUNS = 1
MONTE_CARLO_RUNS = 1

model = Model(initial_state=initial_state, params=sys_params, state_update_blocks=state_update_blocks)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)

def main():
    result = simulation.run()
    df = pd.DataFrame(result)
    rdf = run.postprocessing(df)

    return df, rdf

if __name__ == "__main__":
    df, rdf = main()

    print(rdf.tail())

    # plot results
    rdf.plot(x='timestep', y=['network_resource_demand', 'dex_tokens', 'dex_usdc', 'dex_token_price', 'token_incentives_vested', 'token_seller_vested', 'token_incentives_vested_cum', 'token_seller_vested_cum'], subplots=True, layout=(4, 2), figsize=(15, 10), title='DePIN Simulation Results')
    rdf.plot(x='timestep', y=['node_amount', 'node_change_rate', 'token_staked_supply'], subplots=True, layout=(4, 2), figsize=(15, 10), title='DePIN Simulation Results')

    plt.show()