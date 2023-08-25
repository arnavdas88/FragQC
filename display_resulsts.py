import pandas as pd

result_df = pd.read_json("results.json")

result_df['fidelity_jump'] = result_df['fragqc_fidelity'] - result_df['noisy_fidelity']
fidelity_avg = (result_df['fragqc_fidelity'] + result_df['noisy_fidelity']) / 2

result_df['fidelity_jump'] /= fidelity_avg

print(result_df)