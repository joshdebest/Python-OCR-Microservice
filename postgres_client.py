from postgres_connection import connection_pool
import psycopg2
import psycopg2.extras


class PostgreSQLClient:

    def __init__(self):
        print('Created PostgreSQLClient')

    def query_list_of_document_ids__from_s3_documents_index(self, filing_type_id, action_type):
        try:
            tiff_documents_list = []
            connection = connection_pool.getconn()
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                query = """SELECT document_id FROM liens.s3_documents_index WHERE (document_id) IN (
                                SELECT document_id 
                                    FROM document_sequence.processed_document_tracker_sequence 
                                    WHERE (pdfs_converted_into_tiffs)=True 
                                    AND (extracted_strings_from_images)=False
                                ) AND filing_type_id=(%s) AND action_type=(%s)"""
                cursor.execute(query, [filing_type_id, action_type])

                return_list = cursor.fetchall()
                print(return_list)
                for individual_result in return_list:
                    print("Result:", individual_result["document_id"])
                    clean_result = str(individual_result["document_id"])
                    print("Clean Result:", clean_result)
                    tiff_document_name = "id-" + clean_result + "-pagenum-1.tiff"
                    print("Tiff Document Name:", tiff_document_name)
                    tiff_documents_list.append({"document_id": clean_result, "tiff_document_name": tiff_document_name})

            connection_pool.putconn(connection)
            return tiff_documents_list
        except psycopg2.OperationalError as error:
            print(error)
            print("Failed to insert into update document tracking process for ocr\n")


    def update_mysql_document_tracking(self, document_id):
        try:
            connection = connection_pool.getconn()
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                query = """UPDATE document_sequence.processed_document_tracker_sequence SET extracted_strings_from_images = %s WHERE document_id = %s """
                cursor.execute(query, [True, document_id])
            connection.commit()
            connection_pool.putconn(connection)
        except psycopg2.OperationalError as error:
            print(error)
            print("Failed to insert into update document tracking process for ocr\n")
