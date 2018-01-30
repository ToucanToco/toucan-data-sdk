def argmax(df, column):
    df = df[df[column] == df[column].max()]
    return df
