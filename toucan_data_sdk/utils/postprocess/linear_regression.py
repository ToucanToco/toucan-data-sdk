import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_linear(df, *, variable_column: str, target_column: str):
    """
    Compute the linear regression of a target_column from a variable_column
    (dtypes of the columns must be numeric).

    ### Parameters

    *mandatory*
    - `variable_column` (*str*): name of the column containing the variable to train the model on
    - `target_column` (*str*): name of the column containing the target to predict
    - `periods_to_predict` (*int*): number of periods to predict
    https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
    """
    # Use only variable_column & target_column
    df = df[[variable_column, target_column]]
    # As we'll mostly use dates as X variable we should make them numeric for the prediction
    original_variable_column = df[variable_column].tolist()
    df[variable_column] = range(len(df[variable_column]))
    # Get variables & targets to train the model
    df_train = df[~df[target_column].isnull()]
    # Get variables where targets need to be predicted
    variables_for_prediction = df[df[target_column].isnull()][variable_column]
    regr = LinearRegression()
    regr.fit(
        df_train[variable_column].values.reshape(-1, 1),
        df_train[target_column].values.reshape(-1, 1),
    )
    # For confidence interval:
    # https://datascience.stackexchange.com/questions/41934/
    # obtaining-a-confidence-interval-for-the-prediction-of-a-linear-regression
    stdev = np.sqrt(
        sum(
            (
                df_train[variable_column].values.reshape(-1, 1)
                - df_train[target_column].values.reshape(-1, 1)
            )
            ** 2
        )
        / (len(df_train[target_column].values.reshape(-1, 1)) - 2)
    )
    target_predictions = regr.predict(variables_for_prediction.values.reshape(-1, 1))
    lower_bound = target_predictions - 1.96 * stdev
    higher_bound = target_predictions + 1.96 * stdev
    # return a dataframe with values (original & predicted), value_is_prediction where values
    # were predicted and lower_bound/higher_bound for confidence interval
    predicted = pd.DataFrame(
        {
            variable_column: variables_for_prediction.values,
            target_column: target_predictions.flatten(),
            f'{target_column}_is_prediction': True,
            f'{target_column}_lower_bound': lower_bound.flatten(),
            f'{target_column}_higher_bound': higher_bound.flatten(),
        }
    )
    final = pd.concat([df_train, predicted], axis=0)
    final[variable_column] = original_variable_column
    return final
