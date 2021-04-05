# Python-OCR-Microservice

This is a microservice I wrote as part of a larger start-up project. The microservice 
is an OCR (Optical Character Recognition) image processor that extracts and stores data.

## Main Systems and Functionality
The program runs in a docker container and waits for a start command. It then pulls 
images from an S3 bucket and passes them through the string extraction program. Next
the images get cleansed and passed to Tesseract's OCR engine which extracts certain data 
from these images to be stored in MongoDB.

## Technology Stack
- Google's Tesseract OCR Engine
   - Used to extract certain data from images
- OpenCV
   - Used to cleanse the images in order to improve OCR
- Postgres
   - Used to update our document index and track the progress of each image
- MongoDB
   - Used to temporarily store the extracted data for the next microservice 