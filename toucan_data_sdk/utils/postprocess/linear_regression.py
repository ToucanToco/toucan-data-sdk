import numpy as np
import pandas as pd


def predict_linear(df, *, variable_column: str, target_column: str, input_format: str = None):
    """
    Compute the linear regression of a target_column from a variable_column
    (dtypes of the columns must be numeric).

    ### Parameters

    *mandatory*
    - `variable_column` (*str*): name of the column containing the variable to train the model on,
     dtype should be datetime
    - `target_column` (*str*): name of the column containing the target to predict
    https://towardsdatascience.com/linear-regression-from-scratch-cd0dee067f72
    *optional :*
    - `input_format` (*str*): format of the input values (by default let the parser detect it)
    # return a dataframe with values (original & predicted), value_is_prediction == True where values
    # were predicted and lower_bound/higher_bound for confidence interval
    """
    # Use only variable_column & target_column
    df = df[[variable_column, target_column]]
    original_variable_column = df[variable_column].tolist()
    # As we'll have dates as X variable we should make them ordinal to capture seasonality
    # For example in a date format with dd-mm-yyyy try to extract dayoftheyear (e.g 11/12/2020 is 346)
    df[variable_column] = df[variable_column].apply(
        lambda x: pd.to_datetime(x, dayfirst=True, format=input_format)
    )
    df[variable_column] = df[variable_column].dt.dayofyear

    # Get variables & targets to train the model
    df_train = df[~df[target_column].isnull()]
    # Get variables where targets need to be predicted
    variables_for_prediction = df[df[target_column].isnull()][variable_column]
    X = df_train[variable_column].values
    Y = df_train[target_column].values
    x_mean = np.mean(X)
    y_mean = np.mean(Y)
    numerator, denominator = 0, 0
    n = len(X)

    for i in range(n):
        numerator += (X[i] - x_mean) * (Y[i] - y_mean)
        denominator += (X[i] - x_mean) ** 2
    # Compute coefficients
    b1 = numerator / denominator
    b0 = y_mean - (b1 * x_mean)

    # Predictions
    X_pred = variables_for_prediction.tolist()
    target_predictions = [b0 + b1 * X_pred[i] for i in range(len(X_pred))]

    # For confidence interval:
    # https://datascience.stackexchange.com/questions/41934/
    # obtaining-a-confidence-interval-for-the-prediction-of-a-linear-regression
    stdev = np.sqrt(sum(([b0 + b1 * X[i] for i in range(n)] - Y) ** 2) / (n - 2))
    lower_bound = [target_predictions[i] - 1.96 * stdev for i in range(len(target_predictions))]
    higher_bound = [target_predictions[i] + 1.96 * stdev for i in range(len(target_predictions))]
    predicted = pd.DataFrame(
        {
            variable_column: variables_for_prediction.values,
            target_column: target_predictions,
            f'{target_column}_is_prediction': True,
            f'{target_column}_lower_bound': lower_bound,
            f'{target_column}_higher_bound': higher_bound,
        }
    )
    final = pd.concat([df_train, predicted], axis=0)
    final[variable_column] = original_variable_column
    final[f'{target_column}_is_prediction'].fillna(False, inplace=True)
    final[f'{target_column}_lower_bound'].fillna(final[target_column], inplace=True)
    final[f'{target_column}_higher_bound'].fillna(final[target_column], inplace=True)

    return final
