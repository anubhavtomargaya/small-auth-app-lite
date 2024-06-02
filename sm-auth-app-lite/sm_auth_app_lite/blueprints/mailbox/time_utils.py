from datetime import datetime, timedelta
def get_timerange(start:datetime=datetime.utcnow(),
                  n=1):
    """ get before and after values (date strings) for the gmail search query
    returns: before, after for the specified date diff -> n"""
  
    today = datetime.date() + timedelta(days=1,hours=5,minutes=30)
    print(today)

    return today.__str__(), (today - timedelta(days=n)).__str__()


if __name__ =='__main__':
    print(get_timerange())