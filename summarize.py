from transformers import pipeline
print("Importando modelo Pegasus XSum")
print("Esto puede tardar un rato la primera vez en funcion de la conexion")
print("La direccion de descarga es ~/.cache/huggingface/transformers/ en Linux y C://Users//<Usuario>//.cache//huggingface//transformers// en Windows 10")
generator = pipeline("summarization", model="google/pegasus-xsum")
prompt = input("Introduce el texto a resumir: ")
res = generator(prompt, temperature=0.3, truncation=True)
print("Resumen:")
print(res[0]['summary_text'])