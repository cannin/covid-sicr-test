from datetime import datetime
import numpy as np
from numpy.random import gamma, exponential, lognormal
import pandas as pd
from pathlib import Path

import niddk_covid_sicr as ncs


def get_stan_data(full_data_path, args):
    df = pd.read_csv(full_data_path)
    if args.last_date:
        try:
            datetime.strptime(args.last_date, '%m/%d/%y')
        except ValueError:
            msg = "Incorrect --last-date format, should be MM/DD/YY"
            raise ValueError(msg)
        else:
            df = df[df['dates2'] <= args.last_date]

    # t0 := where to start time series, index space
    try:
        t0 = np.where(df["new_cases"].values >= 1)[0][0]
    except IndexError:
        return [None, None]
    # tm := start of mitigation, index space

    try:
        dfm = pd.read_csv(args.data_path / 'mitigationprior.csv')
        tmdate = dfm.loc[dfm.region == args.roi, 'date'].values[0]
        tm = np.where(df["dates2"] == tmdate)[0][0]
    except Exception:
        tm = t0 + 10

    stan_data = {}
    # stan_data['n_scale'] = 1000  # use this instead of population
    # stan_data['n_theta'] = 8
    # stan_data['n_difeq'] = 5
    stan_data['n_ostates'] = 3
    # stan_data['t0'] = t0-1  # to for ODE is day one,
    #                         # index before start of series
    stan_data['tm'] = tm
    stan_data['ts'] = np.arange(t0, len(df['dates2']))
    stan_data['y'] = df[['new_cases', 'new_recover', 'new_deaths']].to_numpy()\
        .astype(int)[t0:, :]
    stan_data['n_obs'] = len(df['dates2']) - t0
    return stan_data, df['dates2'][t0]


def get_n_data(stan_data):
    if stan_data:
        return (stan_data['y'] > 0).ravel().sum()
    else:
        return 0
    

# functions used to initialize parameters
def get_init_fun(args, stan_data, force_fresh=False):
    if args.init and not force_fresh:
        try:
            init_path = Path(args.fits_path) / args.init
            model_path = Path(args.models_path) / args.model_name
            result = ncs.last_sample_as_dict(init_path, model_path)
        except Exception:
            print("Couldn't use last sample from previous fit to initialize")
            return init_fun(force_fresh=True)
        else:
            print("Using last sample from previous fit to initialize")
    else:
        print("Using default values to initialize fit")
        result = {'f1': gamma(1.5, 2.),
                  'f2': gamma(1.5, 1.5),
                  'sigmar': gamma(2., .1/2.),
                  'sigmad': gamma(2., .1/2.),
                  'sigmau': gamma(2., .1/2.),
                  'q': exponential(.1),
                  'mbase': gamma(2., .1/2.),
                  'mlocation': lognormal(np.log(stan_data['tm']), 1.),
                  'extra_std': exponential(1.),
                  'cbase': gamma(2., 2.),
                  'clocation': lognormal(np.log(20.), 1.),
                  'n_pop': lognormal(np.log(1e5), 1.),
                  'sigmar1': gamma(2., .1/2.)
                  }
    
    def init_fun():
        return result
    return init_fun
