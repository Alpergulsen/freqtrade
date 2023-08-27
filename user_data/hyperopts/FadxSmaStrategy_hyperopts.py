from freqtrade.optimize import CategoricalParameter, create_param_space, IntParameter
from freqtrade.optimize.hyperopt import Hyperopt

# Define parameter spaces for optimization
param_space = {
    "adx_period": IntParameter(4, 24),
    "sma_short_period": IntParameter(4, 24),
    "sma_long_period": IntParameter(12, 175),
}

# Create the Hyperopt object
hyperopt = Hyperopt(strategy=FAdxSmaStrategy, parameter_space=create_param_space(param_space))

# Run optimization
best_params, _ = hyperopt.run()
