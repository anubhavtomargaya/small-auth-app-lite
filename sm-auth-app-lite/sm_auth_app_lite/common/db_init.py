from playhouse.shortcuts import model_to_dict
from peewee import *
# from db_config import username,password,dbname,endpoint

# db = PostgresqlDatabase(dbname,host= endpoint, 
                            # user=username,password = password,port=5432)

# db= MySQLDatabase(database_name,username ,password,endpoint)

db = SqliteDatabase('pockets.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0})

class BaseModel(Model):
    class Meta:
        database = db

from peewee import *
from playhouse.shortcuts import model_to_dict  


class PipelineExecutionMeta(BaseModel):
    execution_id = CharField(primary_key=True)
    gmail_query = CharField(null=True)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    thread_count = IntegerField(default=0,null=True)
    email_message_count = IntegerField(default=0,null=True)
    raw_message_count = IntegerField(default=0,null=True)
    existing_raw_message_count = IntegerField(default=0,null=True)
    decoded_message_count = IntegerField(default=0,null=True)
    status = CharField(default=None)
    user_id = CharField(null=True)  # Added for foreign key relationship
    class Meta:
        table_name = 'execution_metadata'

class RawTransactions(BaseModel):
    txn_id = AutoField() #change to the upstream txn primary key 
    execution_id = CharField(null=True)
    msgId=TextField(unique=True)
    threadId=TextField()
    snippet=TextField(null=True)
    msgEpochTime = BigIntegerField()
    msgEncodedData = TextField()
    msghistoryId=IntegerField(null=True)
    
    class Meta:
        table_name = 'raw_transactions'

class RawTransactionsV1(BaseModel):
    msgId=TextField(unique=True)
    threadId=TextField()
    snippet=TextField(null=True)
    msgEpochTime = BigIntegerField()
    msgEncodedData = TextField()
    msghistoryId=IntegerField(null=True)
    
    class Meta:
        table_name = 'raw_transactionsv1'

##being used as a reporting layer of the transaction but the non null fields are problematic 
##so the data would not be processed on the server. Errors are destined for this endeavour.
        
# class Transactions(BaseModel):
#     txn_id = AutoField() #change to the upstream txn primary key 
#     msgId=TextField(unique=True)
#     msgEpochTime = BigIntegerField()
#     date = DateField(formats=['%d-%m-%Y','%Y-%m-%d']) #give format according to upstream
#     to_vpa = TextField(225)
#     amount_debited = DecimalField()
#     additional_category_1 = TextField(null=True, default=None)
#     additional_category_2 = TextField(null=True,default=None)

#     class Meta:
#         table_name = 'transactions_02'


class Transactions(BaseModel):
    txn_id = AutoField() #change to the upstream txn primary key 
    execution_id = CharField(null=True)
    msgId=CharField(unique=True)
    msgEpochTime = BigIntegerField(null=True)
    date = DateField(null=True,formats=['%d-%m-%Y','%Y-%m-%d']) #give format according to upstream
    to_vpa = CharField(null=True)
    amount_debited = DecimalField(null=True)
    label = TextField(null=True,default=None)
    config_label = CharField(null=True,default=None)
    record_created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        table_name = 'upi_transactions'


class VPA(BaseModel):
    id = AutoField() #change to the upstream txn primary key 
    vpa_user=TextField(unique=True)
    vpa_provider = TextField(null=True)
    category =  TextField(null=True)
    additional_category_1 = TextField(null=True, default=None)
    additional_category_2 = TextField(null=True,default=None)

    class Meta:
        table_name = 'vpa'

##not working, materialise the table or find other way to map view output to class.
class TransactionsView(BaseModel):
    msgId = TextField(unique=True)
    date = DateField(formats=['%d-%m-%Y','%Y-%m-%d']) #give format according to upstream
    vpa_user = TextField(225)
    category =  TextField(null=True)
    amount_debited = DecimalField()
    

    class Meta:
        table_name = 'transactions_vw'

class InsertResponse():
    
    def __init__(self) -> None:
        self.success_inserts = []
        self.failed_insert = []
        
# db.create_tables([Transactions,VPA,RawTransactions])
db.create_tables([PipelineExecutionMeta,RawTransactions,Transactions])
