import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_linear(df, *, variable_column: str, target_column: str):
    """
    Compute the linear regression of a target_column from a variable_column
    (dtypes of the columns must be numeric).

    ### Parameters

    *mandatory*
    - `variable_column` (*str*): name of the column containing the variable to train the model on,
     dtype should be datetime
    - `target_column` (*str*): name of the column containing the target to predict
    https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
    """
    # Use only variable_column & target_column
    df = df[[variable_column, target_column]]
    original_variable_column = df[variable_column].tolist()
    # As we'll mostly use dates as X variable we should make them numeric for the prediction
    # we'll try to extract the day and if not possible, the month
    if len(df[variable_column].iloc[0]) >= 10:
        df[variable_column] = df[variable_column].apply(lambda x: pd.to_datetime(x, dayfirst=True))
        df[variable_column] = df[variable_column].dt.dayofyear
    else:
        df[variable_column] = df[variable_column].apply(lambda x: pd.to_datetime(x))
        df[variable_column] = df[variable_column].dt.month

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
    target_predictions = regr.predict(variables_for_prediction.values.reshape(-1, 1))
    stdev = np.sqrt(
        sum(
            (
                regr.predict(df_train[variable_column].values.reshape(-1, 1))
                - df_train[target_column].values.reshape(-1, 1)
            )
            ** 2
        )
        / (len(df_train[target_column]) - 2)
    )
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
    final[f'{target_column}_is_prediction'].fillna(False, inplace=True)
    final[f'{target_column}_lower_bound'].fillna(final[target_column], inplace=True)
    final[f'{target_column}_higher_bound'].fillna(final[target_column], inplace=True)

    return final
