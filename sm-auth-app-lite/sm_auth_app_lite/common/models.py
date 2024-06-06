
#define using pydantic
class MetaEntry:
    def __init__(self,
                 execution_id,
                 start_time,
                 query=None,
                 end_time=None,
                 thread_count=None,
                 email_message_count=None,
                 raw_message_count=None,
                decoded_message_count=None,
                status=None,
                user_id=None
                 ) -> None:
        
        self.execution_id =  execution_id
        self.query = query
        self.start_time =  start_time
        self.end_time =  end_time
        self.thread_count =  thread_count
        self.email_message_count =  email_message_count
        self.raw_message_count =  raw_message_count
        self.decoded_message_count =  decoded_message_count
        self.status =  status
        self.user_id =  user_id
