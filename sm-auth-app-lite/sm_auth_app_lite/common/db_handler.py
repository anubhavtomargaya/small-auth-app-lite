from datetime import datetime
from decimal import Decimal
from sm_auth_app_lite.common.db_init import PipelineExecutionMeta, RawTransactions,db,Transactions
from sm_auth_app_lite.common.models import MetaEntry
from dateutil.parser import parse
from peewee import IntegrityError

def query_raw_messages(ids:list,column:str='snippet'):
    query = RawTransactions.select().where(RawTransactions.msgId << ids)
    for transaction in query:
        if column=='snippet':
            yield transaction.snippet
        else:
            yield transaction

    
class FetchRawMessageResponse:
    def __init__(self,
                 execution_id,
                 inserted_msgs,
                 existing_msgs
                 ) -> None:
        self.execution_id = execution_id
        self.inserted_msgs = inserted_msgs
        self.existing_msgs = existing_msgs

def insert_raw_transactions(execution_id,
                            data_list)-> FetchRawMessageResponse:
    """Inserts multiple raw transactions into the database.

    Args:
        data_list (list): List of dictionaries containing raw transaction data.

    Returns:
        list: List of created RawTransactions objects.
    """
    # print("data list",data_list)
    # created_objects = []
    inserted_objects = []
    existing_ids = []
    for row_data in data_list:
        try:
                #TODO: Insert executionid in txn table as wellx
            with db.atomic():
                    # Attempt insert using insert_many with ignore conflicts
                    # inserted_objects.extend(RawTransactions.insert_many(row_data).execute())
                    row_data['execution_id'] = execution_id
                    inserted_object = RawTransactions.insert_many(row_data).execute()
                    inserted_objects.append(row_data['msgId'])
            # created_objects.append(insert_raw_transaction(row_data))
        except IntegrityError as e:
            # Extract existing message IDs from the error message
            if 'UNIQUE constraint failed: raw_transactions.msgId' in str(e):
                existing_ids.append(row_data['msgId'])  # Assuming 'msgId' is the unique field
            else:
                raise e  # Re-raise other exceptions

    return FetchRawMessageResponse(execution_id=execution_id,
                                   inserted_msgs=inserted_objects,
                                   existing_msgs=existing_ids)


# def insert_raw_transaction(data):
#     """Inserts a single raw transaction into the database.

#     Args:
#         data (dict): Dictionary containing raw transaction data.

#     Returns:
#         RawTransactions: The created RawTransactions object.
#     """
#     try:
#         return RawTransactions.create(**data)
#     except Exception as e:
#         raise Exception('Error inserting RawTransaction: %s', e)
# def insert_many_raw_transactions(data_list):
#     """Inserts multiple raw transactions into the database efficiently.

#     Args:
#         data_list (list): List of dictionaries containing raw transaction data.

#     Returns:
#         int: The number of rows inserted.
#     """
#     try:
#         # Perform bulk insert using insert_many
#         with db.atomic():  # Ensure transaction safety
#             inserted_count = RawTransactions.insert_many(data_list).execute()
#         return inserted_count
#     except Exception as e:
#         raise Exception('Error inserting RawTransactions: %s', e)
   

def insert_final_transactions(execution_id, data_generator):
    """Inserts transactions from the generator into the 'upi_transactions' table.

    Args:
        data_generator: A generator yielding dictionaries representing transaction data.
    Returns:
        list: A list of message IDs that were skipped due to duplicate entries.
    """

    skipped_ids = []
    inserted_ids = []
    with db.atomic():  # Ensure all insertions happen atomically
        for record in data_generator:
            try:
                # Create Transactions object with data
                transaction = Transactions(
                    msgId=record['msgId'],
                    execution_id=execution_id,
                    msgEpochTime=record['msgEpochTime']/1000,
                    date= parse(record['date']).date() ,  # Parse date according to format
                    to_vpa=record['to_vpa'],
                    amount_debited=Decimal(record['amount_debited']),
                )
                # Attempt insertion, ignoring conflicts
                transaction.save()
                inserted_ids.append(record['msgId'])
            except IntegrityError as e:
                # Check for unique constraint violation
                if 'UNIQUE constraint failed: upi_transactions.msgId' in str(e):
                    skipped_ids.append(record['msgId'])
                else:
                    raise e  # Re-raise other exceptions
    processed_emails_response =  {"skipped":skipped_ids,
                                "inserted":inserted_ids}
    return processed_emails_response

def insert_execution_metadata(meta:MetaEntry):
    try:
        
        PipelineExecutionMeta.create(
            execution_id=meta.execution_id,
            gmail_query=meta.query,
            start_time=meta.start_time,
            end_time=meta.end_time,
            thread_count=meta.thread_count,
            email_message_count=meta.email_message_count,
            raw_message_count=meta.raw_message_count,
            decoded_message_count=meta.decoded_message_count,
            status=meta.status,
            user_id = 'me'
        )
        print("inserted metadata entry: ", meta.execution_id)
    except Exception as e:
        raise Exception(f"Unable to insert entry: {e}")


def update_stage_data(execution_id, stage_name, **kwargs):
    """Creates a new PipelineStage entry for the given execution and stage."""

    # Extract additional data from kwargs (if relevant)
    thread_count = kwargs.get("thread_count", 0)
    email_message_count = kwargs.get("email_message_count", 0)
    raw_message_count = kwargs.get("raw_message_count", 0)
    decoded_message_count = kwargs.get("decoded_message_count", 0)

    # Create a new stage entry
    PipelineExecutionMeta.create(
        execution_meta_id=execution_id,
        stage_name=stage_name,
        thread_count=thread_count,
        email_message_count=email_message_count,
        raw_message_count=raw_message_count,
        decoded_message_count=decoded_message_count,
    )
