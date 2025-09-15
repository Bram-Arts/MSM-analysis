from scipy import stats
import pandas as pd
import slicer

def confidence_interval(df: pd.DataFrame, success: str | list, confidence: float = 0.95) -> None:
    """
    Determine the chance of success of a certain breeding result, including confidence intervals.

    Parameters
    ----------
    df: pd.DataFrame
        Dataset with which to determine success.
    
    success: str | list
        List of monsters that are considered to be a successful result.
        If string, interpreted as a monster group alias.

    confidence: float, default 0.95
        confidence% interval to give.
    """
    if type(success) is str:
        success = slicer.alias_parser(success)
    k = 0
    # Count number of successes
    for _, row in df.iterrows():
        if row["Result Monster"] in success:
            k+=1
    n = df.shape[0] # number of measurements
    print("{} datapoints have {} successes in total".format(n, k))
    interval = stats.beta.interval(confidence, k+1, n-k+1)
    print("That's a {}% confidence interval of between {:.4f} and {:.4f}".format(int(confidence*100), interval[0], interval[1]))
    return interval