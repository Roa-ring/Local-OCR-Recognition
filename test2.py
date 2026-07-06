from paddleocr import PaddleOCR
input = "./13d0a418-fe7b-4d9b-873e-f2bbccb2554c.png"
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
result = ocr.predict(input)
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")