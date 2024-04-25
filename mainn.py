from typing import Union # Mengimpor modul Union dari pustaka typing. 
#Union digunakan untuk mendeklarasikan tipe data yang dapat memiliki lebih dari satu tipe.
from fastapi import FastAPI #ntuk membuat aplikasi web dengan kerangka kerja FastAPI.
app = FastAPI() #Membuat instance aplikasi FastAPI yang disimpan dalam variabel app
@app.get("/") #Mendekorasi fungsi read_root sebagai endpoint HTTP GET dengan path /
def read_root(): #mengembalikan pesan "Hello World" dalam format JSON saat endpoint diakses.
  return {"Hello": "World"} #Mengembalikan objek JSON dengan key "Hello" dan value "World" sebagai respons dari endpoint /
