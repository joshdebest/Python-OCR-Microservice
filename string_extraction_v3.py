import argparse
import cv2
import pytesseract
from pytesseract import Output
import json
import numpy as np
import os
import re


# converts the img to data
# iterates the dictionary and gets the words above a specific conf level
def get_conf_words(img):
    custom_oem_psm_config = r'--psm 3'
    ocr_data = pytesseract.image_to_data(img, lang='eng', config=custom_oem_psm_config, output_type=Output.DICT)

    conf_words = [i for i, word in enumerate(ocr_data["text"]) if int(ocr_data["conf"][i]) > 60]

    ocr_list = []
    for x in conf_words:
        ocr_list.append(ocr_data["text"][x])

    ocr_list = " ".join(ocr_list)
    return ocr_list


# initial blocking func, not fine tuned
# (5,5) (15,5);  (7,7)(9,1);
def get_coordinates(img, size1, size2):
    #small = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, size1)
    grad = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)

    _, thresh = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_OTSU | cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, size2)
    connected = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    mask = np.zeros(thresh.shape, dtype=np.uint8)

    rect_coordinates = []
    for idx in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[idx])
        mask[y:y+h, x:x+w] = 0
        cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
        r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)
        rect_coordinates.append([x, y, w, h, r])
    return rect_coordinates


# takes in the blocking coordinates and the source image
# returns the ocr list from tesseract
def run_tesseract_state(blocking_coor, img):
    # config --psm 6 "Assume a single uniform block of text"
    configuration = r'--psm 6 tessedit_char_whitelist=0123456789'
    tesseract_list = []
    for x in reversed(range(len(blocking_coor))):
        coord = blocking_coor[x]
        cropped_img = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
        ocr_str = pytesseract.image_to_string(cropped_img, lang='eng', config=configuration).replace('\n', ' ').replace('\x0c', '').strip()
        tesseract_list.append(ocr_str.encode('utf-8'))
    #tesseract_list = list(filter(None, tesseract_list))
    return tesseract_list

def run_tesseract_federal(blocking_coor, img):
    # config --psm 7 "Treat the image as a single line of text"
    configuration = r'--psm 7 tessedit_char_whitelist=0123456789'
    tesseract_list = []
    for x in reversed(range(len(blocking_coor))):
        coord = blocking_coor[x]
        cropped_img = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
        ocr_str = pytesseract.image_to_string(cropped_img, lang='eng', config=configuration).replace('\n', ' ').replace('\x0c', '').strip()
        tesseract_list.append(ocr_str.encode('utf-8'))
    #tesseract_list = list(filter(None, tesseract_list))
    return tesseract_list


# helper function that runs tesseract on a state tax lien
def do_state_extraction_old(file):
    # 1st blocking run
    size1 = (10, 10)
    size2 = (15, 1)
    coor = get_coordinates(file, size1, size2)
    rect_coordinates = []
    for idx in range(len(coor)):
        x = coor[idx][0]
        y = coor[idx][1]
        w = coor[idx][2]
        h = coor[idx][3]
        r = coor[idx][4]
        if r > 0.45 and w > 50:
            cv2.rectangle(file, (x, y), (x+w-1, y+h-1), (0, 255, 255), 2)
            rect_coordinates.append([(x, y), (x+w-1, y+h-1)])
    tesseract_list = run_tesseract_state(rect_coordinates, file)

    # 2nd blocking run
    size3 = (15, 15)
    size4 = (10, 10)
    coor2 = get_coordinates(file, size3, size4)
    rect_coordinates2 = []
    for idx in range(len(coor2)):
        x = coor2[idx][0]
        y = coor2[idx][1]
        w = coor2[idx][2]
        h = coor2[idx][3]
        r = coor2[idx][4]
        if r > 0.45 and w > 50:
            cv2.rectangle(file, (x, y), (x+w-1, y+h-1), (0, 0, 255), 2)
            rect_coordinates2.append([(x, y), (x+w-1, y+h-1)])

    # call helper function that runs tesseract
    tesseract_list2 = run_tesseract_state(rect_coordinates2, file)

    # Combine the 2 lists while removing duplicates
    combined_list = tesseract_list + list(set(tesseract_list2) - set(tesseract_list))
    print("Combined list: ", combined_list)

    cv2.imshow("img", file)
    cv2.waitKey(0)
    return combined_list


# helper function that run tesseract on a federal tax lien
def do_federal_extraction(file):
    size1 = (5, 5)
    size2 = (15, 5)
    coor = get_coordinates(file, size1, size2)
    rect_coordinates = []
    for idx in range(len(coor)):
        x = coor[idx][0]
        y = coor[idx][1]
        w = coor[idx][2]
        h = coor[idx][3]
        r = coor[idx][4]
        # targets the section where total amount appears on the document
        if r > 0.45 and w > 50 and 2300 < y < 2500 and x > 1800:
            cv2.rectangle(file, (x-5, y-5), (x+w+5, y+h+5), (0, 255, 255), 2)
            rect_coordinates.append([(x-5, y-5), (x+w+5, y+h+5)])
    tesseract_list = run_tesseract_federal(rect_coordinates, file)
    print(tesseract_list)
    #cv2.imshow("img", file)
    #cv2.waitKey(0)
    return tesseract_list


# Helper func to extracted the total amount from the tesseract string
def get_total_amount(input_str):
    amount_index = input_str.rfind('$')
    final_str = input_str[amount_index:]
    end_index = final_str.find('.')
    final_str = final_str[1:end_index+3]
    return final_str


# Main function that extracts data from each document depending on what type it is
def run_string_extraction(file, doc_type):
    file = cv2.resize(file, (2400, 3000))

    if doc_type == 'Notice of State Tax Lien':
        extracted_data = get_conf_words(file)
        regex = re.compile('[^0-9$.,]')
        extracted_data = regex.sub("", extracted_data)
        extracted_data = extracted_data.strip()
        
        total = get_total_amount(extracted_data)
        return total

    elif doc_type == 'Notice of Federal Tax Lien':
        extracted_data = do_federal_extraction(file)
        return extracted_data
