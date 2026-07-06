from paddleocr import TextRecognition
model = TextRecognition(model_name="PP-OCRv6_medium_rec")
input = "bdc0fe63-cf15-440f-be9c-07b04a5e63d0.png"
output = model.predict(input=input, batch_size=1)
for res in output:
    res.print()
    res.save_to_json(save_path="./output/res.json")