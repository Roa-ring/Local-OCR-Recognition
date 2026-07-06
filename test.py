from paddleocr import TextRecognition
model = TextRecognition(model_name="PP-OCRv6_medium_rec")
input = "13d0a418-fe7b-4d9b-873e-f2bbccb2554c.png"
output = model.predict(input=input, batch_size=1)
for res in output:
    res.print()
    res.save_to_json(save_path="./output/res.json")