# conda activate webservicep2plendingg webservicep2plendingg
# uvicorn main:app --reload

# melakukan import yang dibutuhkan
from typing import Union #Mengimpor modul Union dari pustaka typing
from fastapi import FastAPI,Response,Request,HTTPException #Mengimpor kelas-kelas dan fungsi yang diperlukan dari modul fastapi
from fastapi.middleware.cors import CORSMiddleware #Mengimpor modul CORSMiddleware dari fastapi.middleware.cors
import sqlite3 # Mengimpor modul sqlite3

app = FastAPI()

app.add_middleware(
	CORSMiddleware, #untuk mengontrol permintaan lintas asal (Cross-Origin Request) pada API
	allow_origins=["*"], #mengizinkan akses dari semua sumber daya.
	allow_credentials=True, #Mengizinkan kredensial seperti cookie dan otentikasi HTTP saat melakukan permintaan lintas asal
	allow_methods=["*"], # mengizinkan penggunaan semua metode
	allow_headers=["*"], #mengizinkan penggunaan semua header.
) #Inisialisasi FastAPI dan menambahkan middleware CORS untuk mengizinkan permintaan dari berbagai sumber.


@app.get("/")
def read_root():
    return {"Hello": "World"} # untuk mengembalikan pesan "Hello World" saat mengakses route root ("/")

@app.get("/mahasiswa/{nim}")
def ambil_mhs(nim:str):
    return {"nama": "Budi Martami"} # mengembalikan data mhs berdasarkan NIM/NPM yang diberikan

@app.get("/mahasiswa2/")
def ambil_mhs2(nim:str):
    return {"nama": "Budi Martami 2"} # tambahan untuk mengembalikan data mahasiswa dengan NIM tertentu

@app.get("/daftar_mhs/") # untuk mengembalikan daftar mahasiswa berdasarkan provinsi dan angkatan
def daftar_mhs(id_prov:str,angkatan:str):
    return {"query":" idprov: {}  ; angkatan: {} ".format(id_prov,angkatan),"data":[{"nim":"1234"},{"nim":"1235"}]}

# panggil sekali saja
@app.get("/init/") # Mendeklarasikan route API yang dapat diakses dengan metode GET pada path "/init/"
def init_db(): #Mendefinisikan fungsi init_db() yang akan dieksekusi saat route "/init/" diakses
  try:
    DB_NAME = "upi.db" #nama database
    con = sqlite3.connect(DB_NAME) #connect ke database
    cur = con.cursor() #Membuat objek cursor untuk menjalankan perintah SQL pada database
    create_table = """ CREATE TABLE mahasiswa( 
            ID      	INTEGER PRIMARY KEY 	AUTOINCREMENT,
            nim     	TEXT            	NOT NULL,
            nama    	TEXT            	NOT NULL,
            id_prov 	TEXT            	NOT NULL,
            angkatan	TEXT            	NOT NULL,
            tinggi_badan  INTEGER
        )  
        """
    cur.execute(create_table) # Menjalankan perintah SQL untuk membuat tabel "mahasiswa" dalam database.
    con.commit # Melakukan commit untuk menyimpan perubahan ke database
  except:
           return ({"status":"terjadi error"})  # cek error
  finally:
           con.close() #tutup koneksi database
    
  return ({"status":"ok, db dan tabel berhasil dicreate"}) #inisisalisasi database dengan membuat tabel

from pydantic import BaseModel # Mengimpor kelas BaseModel dari modul pydantic, yang digunakan sebagai dasar untuk mendefinisikan model data.

from typing import Optional # untuk mendefinisikan atribut opsional dalam model data.

class Mhs(BaseModel): #Mhs akan memiliki fitur dan kemampuan yang disediakan oleh BaseModel
   nim: str #Mendeklarasikan atribut nim dengan tipe data string
   nama: str #Mendeklarasikan atribut nama dengan tipe data string
   id_prov: str #Mendeklarasikan atribut id_prov dengan tipe data string.
   angkatan: str #Mendeklarasikan atribut angkatan dengan tipe data string.
   tinggi_badan: Optional[int] | None = None  # yang boleh null hanya ini


#status code 201 standard return creation
#return objek yang baru dicreate (response_model tipenya Mhs)
@app.post("/tambah_mhs/", response_model=Mhs,status_code=201)  #Mendeklarasikan route API dengan metode POST pada path "/tambah_mhs/"
def tambah_mhs(m: Mhs,response: Response, request: Request): #Mendefinisikan yang akan dieksekusi saat route "/tambah_mhs/" diakses dengan metode POST.
   try:
       DB_NAME = "upi.db" #menyimpan nama database
       con = sqlite3.connect(DB_NAME) #connect ke database
       cur = con.cursor() #menjalankan perintah SQL pada database.
       # hanya untuk test, rawal sql injecttion, gunakan spt SQLAlchemy
       cur.execute("""insert into mahasiswa (nim,nama,id_prov,angkatan,tinggi_badan) values ( "{}","{}","{}","{}",{})""".format(m.nim,m.nama,m.id_prov,m.angkatan,m.tinggi_badan)) 
       con.commit()  # menyimpan perubahan ke database setelah data mahasiswa baru dimasukkan
   except:
       print("oioi error") # menampilkan error
       return ({"status":"terjadi error"})   # cek error
   finally:  	 
       con.close() # tutup koneksi ke database
   response.headers["Location"] = "/mahasiswa/{}".format(m.nim) #Mengatur header respons HTTP untuk lokasi baru data mahasiswa yang ditambahkan.
   print(m.nim)
   print(m.nama)
   print(m.angkatan)
  #Mencetak nilai atribut nim, nama, dan angkatan dari objek m ke konsol
   return m #Mengembalikan objek m setelah berhasil menambahkan data mahasiswa baru ke database.



@app.get("/tampilkan_semua_mhs/") #Mendeklarasikan route API dengan metode GET pada path "/tampilkan_semua_mhs/"
def tampil_semua_mhs(): #Mendefinisikan fungsi tampil_semua_mhs yang akan dieksekusi saat route "/tampilkan_semua_mhs/" diakses dengan metode GET
   try:
       DB_NAME = "upi.db" 
       con = sqlite3.connect(DB_NAME) # koneksi ke database
       cur = con.cursor() #menjalankan perintah SQL pada database.
       recs = [] #Membuat list kosong recs untuk menampung data mahasiswa yang diambil dari database.
       for row in cur.execute("select * from mahasiswa"):
           recs.append(row) # ambil data semua mhs dari database
   except:
       return ({"status":"terjadi error"})   # cek error
   finally:  	 
       con.close() # menutup koneksi ke database
   return {"data":recs} # Mengembalikan respons JSON yang berisi data mahasiswa yang berhasil diambil dari database.

from fastapi.encoders import jsonable_encoder #untuk mengkonversi objek Pydantic model ke bentuk JSON yang dapat dienkapsulasi dalam respons HTTP.


@app.put("/update_mhs_put/{nim}",response_model=Mhs) #Mendeklarasikan route API dengan metode PUT
def update_mhs_put(response: Response,nim: str, m: Mhs ): #Mendefinisikan fungsi update_mhs_put yang akan dieksekusi 
    #update keseluruhan
    #karena key, nim tidak diupdape
    try:
       DB_NAME = "upi.db"
       con = sqlite3.connect(DB_NAME) # connect ke database
       cur = con.cursor() #menjalankan perintah SQL pada database
       cur.execute("select * from mahasiswa where nim = ?", (nim,) )  #tambah koma untuk menandakan tupple
       existing_item = cur.fetchone() #Mengambil satu baris data dari hasil eksekusi perintah SQL sebelumnya, yang akan menunjukkan apakah data mahasiswa dengan NIM yang dimaksud ada di database atau tidak.
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # cek error
    
    if existing_item:  #data ada #Memulai mengecek apakah data mahasiswa dengan NIM yang dimaksud ada dalam database.
            print(m.tinggi_badan) #Mencetak nilai atribut tinggi_badan dari objek m
            cur.execute("update mahasiswa set nama = ?, id_prov = ?, angkatan=?, tinggi_badan=? where nim=?", (m.nama,m.id_prov,m.angkatan,m.tinggi_badan,nim)) #menjalankan perintah SQL
            con.commit() # Melakukan commit untuk menyimpan perubahan ke database setelah data mahasiswa diupdate.
            response.headers["location"] = "/mahasiswa/{}".format(m.nim) #Mengatur header respons HTTP untuk lokasi baru data mahasiswa yang diupdate.
    else:  # data tidak ada
            print("item not foud") #menampilkan pesan bahwa item tidak di temukan
            raise HTTPException(status_code=404, detail="Item Not Found")
      
    con.close() #menutuk koneksi ke database

    return m 
#Fungsi untuk memperbarui data mahasiswa berdasarkan NIM menggunakan metode PUT


# khusus untuk patch, jadi boleh tidak ada
# menggunakan "kosong" dan -9999 supaya bisa membedakan apakah tdk diupdate ("kosong") atau mau
# diupdate dengan dengan None atau 0
class MhsPatch(BaseModel): #deklarasi model untuk operasi patch dengan atribut yang bisa dirubah
   nama: str | None = "kosong" #Mendefinisikan atribut nama dengan tipe data string (str) 
   id_prov: str | None = "kosong" #Mendefinisikan atribut id_prov dengan tipe data string (str) 
   angkatan: str | None = "kosong" #Mendefinisikan atribut angkatan dengan tipe data string (str) 
   tinggi_badan: Optional[int] | None = -9999  # yang boleh null hanya ini


@app.patch("/update_mhs_patch/{nim}",response_model = MhsPatch) #Mendefinisikan endpoint HTTP PATCH dengan path /update_mhs_patch/{nim}
def update_mhs_patch(response: Response, nim: str, m: MhsPatch ): #Mendefinisikan fungsi update_mhs_patch yang menerima parameter response bertipe Response, nim bertipe string (str), dan m bertipe MhsPatch.
    try:
      print(str(m)) #debugging
      DB_NAME = "upi.db"
      con = sqlite3.connect(DB_NAME) # connect ke database
      cur = con.cursor() #Membuat objek cursor untuk melakukan operasi database.
      cur.execute("select * from mahasiswa where nim = ?", (nim,) )  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone() #Mengambil satu baris data hasil eksekusi perintah SQL sebelumnya.
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "update mahasiswa set " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.nama!="kosong": #Mulai blok kondisional untuk mengecek apakah atribut nama dari data mahasiswa tidak kosong.
            if m.nama!=None: #Jika tidak kosong, tambahkan perintah UPDATE untuk kolom nama dengan nilai yang diberikan
                sqlstr = sqlstr + " nama = '{}' ,".format(m.nama)
            else:     
                sqlstr = sqlstr + " nama = null ," #Jika nama None, tambahkan perintah UPDATE untuk kolom nama dengan nilai NULL
        
        if m.angkatan!="kosong": #Mulai blok kondisional untuk mengecek apakah atribut angkatan dari data mahasiswa tidak kosong.
            if m.angkatan!=None:
                sqlstr = sqlstr + " angkatan = '{}' ,".format(m.angkatan)
            else:
                sqlstr = sqlstr + " angkatan = null ,"
        
        if m.id_prov!="kosong": #Mulai blok kondisional untuk mengecek apakah atribut id_prov dari data mahasiswa tidak kosong.
            if m.id_prov!=None: #Jika tidak kosong, tambahkan perintah UPDATE untuk kolom nama dengan nilai yang diberikan
                sqlstr = sqlstr + " id_prov = '{}' ,".format(m.id_prov) 
            else:
                sqlstr = sqlstr + " id_prov = null, "     

        if m.tinggi_badan!=-9999:
            if m.tinggi_badan!=None:  #Jika tidak kosong, tambahkan perintah UPDATE untuk kolom nama dengan nilai yang diberikan
                sqlstr = sqlstr + " tinggi_badan = {} ,".format(m.tinggi_badan)
            else:    
                sqlstr = sqlstr + " tinggi_badan = null ,"

        sqlstr = sqlstr[:-1] + " where nim='{}' ".format(nim)  #buang koma yang trakhir  #menambahkan kondisi WHERE berdasarkan NIM
        print(sqlstr)      # cetak string
        try:
            cur.execute(sqlstr) # Eksekusi perintah SQL untuk melakukan update data mahasiswa.
            con.commit()  # commit perubahan database       
            response.headers["location"] = "/mahasixswa/{}".format(nim) # Set header response untuk menunjukkan lokasi data yang diubah.
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   # cek error
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close() #menutupk koneksi ke database
    return m # memperbarui data mhs berdasarkan NIM menggunakan metode PATCH.
  
    
@app.delete("/delete_mhs/{nim}") #Mendefinisikan endpoint HTTP DELETE dengan path /delete_mhs/{nim} 
def delete_mhs(nim: str): #Mendefinisikan fungsi delete_mhs yang menerima parameter nim bertipe string (str), yang merupakan NIM dari mahasiswa yang akan dihapus.
    try:
       DB_NAME = "upi.db"
       con = sqlite3.connect(DB_NAME) # connect ke database
       cur = con.cursor()
       sqlstr = "delete from mahasiswa  where nim='{}'".format(nim)                 
       print(sqlstr) # debug 
       cur.execute(sqlstr)
       con.commit()
    except:
       return ({"status":"terjadi error"})   # cek error
    finally:  	 
       con.close() #tutup koneksi
    
    return {"status":"ok"}

