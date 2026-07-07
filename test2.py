from paddleocr import PaddleOCR
<<<<<<< HEAD

input = "c2990ee0d065aa5b079f5d55641e47ec.jpg"
=======
import glob
>>>>>>> 72871ef02214ed24c0603b3864d56657a6597ad6
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
<<<<<<< HEAD
result = ocr.predict("c2990ee0d065aa5b079f5d55641e47ec.jpg")
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")
=======
way=input()
image_list = glob.glob(rf"{way}/*.png") + glob.glob(rf"{way}/*.jpg")
for img_path in image_list:
    print(f"正在处理: {img_path}")
    result = ocr.predict(img_path)
    for res in result:
        res.print()
        res.save_to_img("output")
        res.save_to_json("output")
>>>>>>> 72871ef02214ed24c0603b3864d56657a6597ad6
