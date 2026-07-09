from paddleocr import PaddleOCR

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
result = ocr.predict("output.png")
for res in result:
    res.print()
    res.save_to_img("output/test")
    res.save_to_json("output/test")