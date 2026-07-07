from paddleocr import PaddleOCR
import glob
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
way=input()
image_list = glob.glob(rf"{way}/*.png") + glob.glob(rf"{way}/*.jpg")
for img_path in image_list:
    print(f"正在处理: {img_path}")
    result = ocr.predict(img_path)
    for res in result:
        res.print()
        res.save_to_img("output")
        res.save_to_json("output")
