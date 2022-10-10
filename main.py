from pyexpat.errors import messages
from urllib import response
import boto3
import json
import gzip
from flatten_json import flatten
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP
import ast
import psycopg2
from psycopg2 import Error
import time
import string


AWS_REGION = "awslocal"

sqs_client = boto3.client("sqs", region_name=AWS_REGION)
aws_access_key_id = 'fetchtest' 
aws_secret_access_key = 'fetchtest1'

# defining method that interacts with local sqs queue to extract data
def receive_message():
    sqs_client = boto3.client("sqs", endpoint_url="http://localhost:4566/000000000000/login-queue", region_name=AWS_REGION, aws_access_key_id='fetchtest', aws_secret_access_key='fetchtest1')
    response = sqs_client.receive_message(
        QueueUrl = "http://localhost:4566/000000000000/login-queue",
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    ) 
     
    return response


def main():
    #  set up hybrid encryption method (public/private key with encrpyted AES session key for arbitrary amount of data)
    key = RSA.generate(2048)
    # print(key)
    private_key = key.export_key()
    # print(private_key)
    file_out = open("private.pem", "wb")
    file_out.write(private_key)
    file_out.close()

    public_key = key.publickey().export_key()
    # print(public_key)
    file_out = open("receiver.pem", "wb")
    file_out.write(public_key)
    file_out.close()

    recipient_key = RSA.import_key(open("receiver.pem").read())
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Try/Except/Finally block with a for loop to establish some control flow as I am iterating through each unique record for insertion
    try:
        connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="localhost",
                                  port="54321",
                                  database="postgres")
        cursor = connection.cursor()
    
        num = 101
        for _ in range(num):
            # indexing into my receive_message output and also replacing null with an empty string for future record insertion
            msg = receive_message()
            flat_json2 = flatten(msg)
            print(flat_json2)
            stringdict2 = msg["Messages"][0]["Body"]
            new_string = stringdict2.replace("null", "''")
            newdictionary = ast.literal_eval(new_string)
            # first PII variable defined
            data = newdictionary["ip"].encode("utf-8")
            file_out = open("encrypted_data.bin", "wb")
            # Encrypt the data with the AES session key for 1st PII variable
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(data)
            [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
            file_out.close()
            # second PII variable defined
            data2 = newdictionary["device_id"].encode("utf-8")
            file_out = open("encrypted_data.bin", "wb")
            # Encrypt the data with the AES session key for 2nd PII variable
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            ciphertext2, tag = cipher_aes.encrypt_and_digest(data2)
            [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext2) ]
            file_out.close()
            # code block with SQL integration to insert records of the 7 fields to postgres DB
            postgres_insert_query = """ INSERT INTO user_logins (USER_ID, DEVICE_TYPE, MASKED_IP, MASKED_DEVICE_ID, LOCALE, APP_VERSION, CREATE_DATE) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            record_to_insert = (newdictionary["user_id"], newdictionary["device_type"], ciphertext, ciphertext2, newdictionary["locale"], newdictionary["app_version"], time.strftime("%Y-%m-%d"))
            print("Record successfully inserted")
            cursor.execute(postgres_insert_query, record_to_insert)
        
    

        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into user_logins table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into user_logins table", error)

    finally:
    # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    
if __name__=="__main__":
    main()
