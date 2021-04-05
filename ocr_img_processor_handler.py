import concurrent.futures
from postgresql_client import PostgreSQLClient
from aws_s3_sdk_controller import AwsS3SdkController
#import string_extracton_v2
import string_extracton_v3
from mongodb import MongoDB
import multiprocessing
import numpy as np

#TODO fix http POST request to extracted data

number_of_cpu_processors = (multiprocessing.cpu_count() - 2)
postgresql_client = PostgreSQLClient()

def break_up_list_into_equal_sizes(full_list_of_lien_tiffs, n):
    return np.array_split(full_list_of_lien_tiffs, n)


def start_image_processing_text_extraction(bucket_name, filing_type):
    tiff_documents_list = postgresql_client.query_list_of_document_ids__from_s3_documents_index(filing_type, "Lien Financing Stmt")
    print("Number of CPU Processors:", number_of_cpu_processors)
    try:

        broken_up_tiff_documents_list = break_up_list_into_equal_sizes(tiff_documents_list, number_of_cpu_processors)
        print("Full Array Size:", len(tiff_documents_list))
        print("Mini Array Size:", len(broken_up_tiff_documents_list))

        with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_cpu_processors) as executor:
            data_extraction_results = [executor.submit(extract_and_upload_text_from_images,
                                                       bucket_name,
                                                       mini_array,
                                                       filing_type)
                                       for mini_array in broken_up_tiff_documents_list]

            for f in concurrent.futures.as_completed(data_extraction_results):
                print(f.result())

        # extracted_string_processor_messenger_client.get_request_from_extracted_string_processor()
        # extracted_string_processor_messenger_client.post_request_from_extracted_string_processor()

    except Exception as error:
        print("[ERROR]  start_image_processing_text_extraction:", error)


def extract_and_upload_text_from_images(bucket_name, tiff_documents_list, filing_type):

    print("Length of mini_tiff_documents_list:", len(tiff_documents_list))

    aws_s3_sdk_controller = AwsS3SdkController()
    mini_thread_postgresql_client = PostgreSQLClient()
    mongodb_client = MongoDB()

    for json_object in tiff_documents_list:
        try:
            document_id = json_object.get("document_id")

            # print(json_object.get("tiff_document_name"))
            # print("Document ID:", document_id)

            tiff_document = aws_s3_sdk_controller.download_specific_s3_file(bucket_name,
                                                                            json_object.get("tiff_document_name"))
            extracted_string = string_extracton_v3.run_string_extraction(tiff_document, filing_type)

            mongodb_client.insert_document_into_database(document_id, extracted_string)

            mini_thread_postgresql_client.update_mysql_document_tracking(document_id)

        except Exception as error:
            print("[ERROR]  Tiff File Name:", json_object.get("tiff_document_name"))
            print("[ERROR]  Document ID:", document_id)
            print("[ERROR]  extract_and_upload_text_from_images", error)

    # client.post_request_from_extracted_string_processor()
