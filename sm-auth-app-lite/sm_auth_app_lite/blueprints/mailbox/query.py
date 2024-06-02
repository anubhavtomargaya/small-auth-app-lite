
from .time_utils import get_timerange

def get_query_for_email(email='alerts@hdfcbank.net',
                        start=None,
                        end=None):
        if start and end:
            return  f"from:{email} after:{start} before:{end}"
        
        before,after = get_timerange()
        x = f"from:{email} after:{after} before:{before}"
        print(x,"qrt")
        return x

    