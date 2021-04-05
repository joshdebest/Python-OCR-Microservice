import time
from wsgiref import simple_server
import falcon
import msgpack
import ocr_image_processor_handler
from aws_s3_sdk_controller import AwsS3SdkController

class CommunicationToBulkDataCollectorMicroservice:

    print("---------- OCR IMAGE PROCESSOR HAS SUCCESSFULLY STARTED ----------")

    def on_get(self, req, resp):
        """Handles GET requests"""
        outgoing_message = {'msg': 'A Successful Connection made to ocr-image-processor API Server'}
        # TODO Eventually make outgoing message encoded

        aws_sdk_controller = AwsS3SdkController()
        aws_sdk_controller.list_all_s3_buckets()

        resp.data = msgpack.packb(outgoing_message)
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        print(resp)

    def on_post(self, req, resp):
        raw_incoming_message_command = req.media.get('command')
        incoming_filing_type = req.media.get('filing_type')
        print(raw_incoming_message_command)

        if raw_incoming_message_command == "StartOCRImageProcessorMicroService":

            outgoing_message = {'msg': 'Starting OCR Image Processing Microservice'}
            # TODO Eventually make outgoing message encoded
            resp.data = msgpack.packb(outgoing_message)
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            print(resp)

            start_time = time.time()
            ocr_image_processor_handler.start_image_processing_text_extraction("ca-lien-tiffs", incoming_filing_type)
            print("\n*---- Processing all tiff files took", time.time() - start_time, "seconds to run ----*")
        else:
            outgoing_message = {'msg': 'Error in the command sent'}
            resp.data = msgpack.packb(outgoing_message)
            resp.status = falcon.HTTP_406
            resp.content_type = falcon.MEDIA_JSON
            print(resp)


api = falcon.API()
api.add_route('/', CommunicationToBulkDataCollectorMicroservice())

if __name__ == '__main__':
    httpd = simple_server.make_server('', 8090, api)
    httpd.serve_forever()
