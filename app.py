#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, uuid
from datetime import datetime
from typing import Dict, Any, Optional
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

HOST = os.getenv("KEYDB_HOST", "localhost")
PORT = int(os.getenv("KEYDB_PORT", "6379"))
PASSWORD = os.getenv("KEYDB_PASSWORD") or None
DB = int(os.getenv("KEYDB_DB", "0"))
KEY_PREFIX = os.getenv("KEY_PREFIX", "libro")
ESTADOS_VALIDOS = {"pendiente","leyendo","terminado"}

def conectar()->Redis:
    try:
        r = Redis(host=HOST, port=PORT, password=PASSWORD, db=DB, socket_timeout=4)
        if not r.ping(): raise ConnectionError("Ping falló")
        return r
    except (ConnectionError, TimeoutError) as e:
        print(f"❌ Error de conexión a KeyDB/Redis: {e}"); sys.exit(1)

def validar_libro(d:Dict[str,Any], parcial:bool=False)->Optional[str]:
    campos=["titulo","autor","genero","estado"]
    if not parcial:
        falta=[c for c in campos if c not in d]
        if falta: return "Faltan campos obligatorios: " + ", ".join(falta)
    if "titulo" in d and (not isinstance(d["titulo"],str) or not d["titulo"].strip()): return "El campo 'titulo' debe ser un string no vacío."
    if "autor" in d and (not isinstance(d["autor"],str) or not d["autor"].strip()): return "El campo 'autor' debe ser un string no vacío."
    if "genero" in d and (not isinstance(d["genero"],str) or not d["genero"].strip()): return "El campo 'genero' debe ser un string no vacío."
    if "estado" in d:
        if not isinstance(d["estado"],str): return "El campo 'estado' debe ser un string."
        if d["estado"].strip().lower() not in ESTADOS_VALIDOS: return "Estado inválido. Valores permitidos: pendiente, leyendo, terminado"
    return None

def now_iso(): return datetime.utcnow().isoformat()
def key_for(book_id:str)->str: return f"{KEY_PREFIX}:{book_id}"

def pedir_input(msg:str, requerido:bool=True, por_defecto:Optional[str]=None)->str:
    while True:
        val = input(f"{msg}{' ['+por_defecto+']' if por_defecto else ''}: ").strip()
        if val: return val
        if not requerido: return por_defecto or ""
        print("⚠️ Este campo es obligatorio.")

def imprimir_libro(doc:Dict[str,Any]):
    print("-"*60)
    print(f"ID:       {doc.get('id','—')}")
    print(f"Título:   {doc.get('titulo','—')}")
    print(f"Autor:    {doc.get('autor','—')}")
    print(f"Género:   {doc.get('genero','—')}")
    print(f"Estado:   {doc.get('estado','—')}")
    if doc.get("creado_en"): print(f"Creado:   {doc['creado_en']}")
    if doc.get("actualizado_en"): print(f"Actual.:  {doc['actualizado_en']}")

def agregar_libro(r:Redis):
    print("\n➕ Agregar nuevo libro")
    titulo = pedir_input("Título"); autor = pedir_input("Autor"); genero = pedir_input("Género")
    estado = pedir_input("Estado (pendiente/leyendo/terminado)", por_defecto="pendiente").strip().lower()
    data={"id":str(uuid.uuid4()),"titulo":titulo,"autor":autor,"genero":genero,"estado":estado,"creado_en":now_iso(),"actualizado_en":now_iso()}
    err=validar_libro(data); 
    if err: print("❌",err); return
    r.set(key_for(data["id"]), json.dumps(data)); print("✅ Libro agregado con id:", data["id"])

def obtener_libro(r:Redis, book_id:str):
    raw=r.get(key_for(book_id)); return json.loads(raw) if raw else None

def actualizar_libro(r:Redis):
    print("\n✏️  Actualizar libro")
    book_id = pedir_input("Ingrese el id del libro a actualizar")
    doc = obtener_libro(r, book_id)
    if not doc: print("❌ No se encontró un libro con ese id."); return
    print("Deje en blanco para mantener el valor actual.")
    nuevo_titulo = pedir_input("Nuevo título", requerido=False, por_defecto=doc.get("titulo",""))
    nuevo_autor = pedir_input("Nuevo autor", requerido=False, por_defecto=doc.get("autor",""))
    nuevo_genero = pedir_input("Nuevo género", requerido=False, por_defecto=doc.get("genero",""))
    nuevo_estado = pedir_input("Nuevo estado (pendiente/leyendo/terminado)", requerido=False, por_defecto=doc.get("estado","pendiente"))
    update={}
    if nuevo_titulo != doc.get("titulo"): update["titulo"]=nuevo_titulo
    if nuevo_autor != doc.get("autor"): update["autor"]=nuevo_autor
    if nuevo_genero != doc.get("genero"): update["genero"]=nuevo_genero
    if nuevo_estado != doc.get("estado"): update["estado"]=nuevo_estado.strip().lower()
    if not update: print("ℹ️  No hay cambios para aplicar."); return
    err=validar_libro(update, parcial=True)
    if err: print("❌",err); return
    doc.update(update); doc["actualizado_en"]=now_iso()
    r.set(key_for(book_id), json.dumps(doc)); print("✅ Libro actualizado correctamente.")

def eliminar_libro(r:Redis):
    print("\n🗑️  Eliminar libro")
    book_id = pedir_input("Ingrese el id del libro a eliminar")
    res = r.delete(key_for(book_id))
    print("✅ Libro eliminado." if res else "❌ No se encontró un libro con ese id.")

def iterar_libros(r:Redis):
    cursor=0; pattern=key_for("*")
    while True:
        cursor, keys = r.scan(cursor=cursor, match=pattern, count=250)
        for k in keys:
            raw=r.get(k)
            if raw: yield json.loads(raw)
        if cursor==0: break

def ver_listado(r:Redis):
    print("\n📋 Listado de libros")
    hay=False
    for d in iterar_libros(r): hay=True; imprimir_libro(d)
    if not hay: print("(Sin registros)")

def buscar_libros(r:Redis):
    print("\n🔎 Buscar libros (deje vacío para omitir)")
    f_titulo = pedir_input("Título contiene", requerido=False).lower()
    f_autor = pedir_input("Autor contiene", requerido=False).lower()
    f_genero = pedir_input("Género contiene", requerido=False).lower()
    def matches(d):
        def cont(val, sub): return (sub in val.lower()) if sub else True
        return cont(d.get("titulo",""), f_titulo) and cont(d.get("autor",""), f_autor) and cont(d.get("genero",""), f_genero)
    res=[d for d in iterar_libros(r) if matches(d)]
    if not res: print("🙈 No se encontraron resultados."); return
    print(f"Se encontraron {len(res)} resultado(s):")
    for d in res: imprimir_libro(d)

def mostrar_menu():
    print("\n=== Biblioteca (KeyDB/Redis) ===")
    print("1) Agregar nuevo libro")
    print("2) Actualizar información de un libro")
    print("3) Eliminar libro existente")
    print("4) Ver listado de libros")
    print("5) Buscar libros")
    print("6) Salir")

def main():
    try: r=conectar()
    except SystemExit: return
    while True:
        mostrar_menu()
        op=input("Seleccione una opción (1-6): ").strip()
        if op=='1': agregar_libro(r)
        elif op=='2': actualizar_libro(r)
        elif op=='3': eliminar_libro(r)
        elif op=='4': ver_listado(r)
        elif op=='5': buscar_libros(r)
        elif op=='6': print("👋 ¡Hasta pronto!"); break
        else: print("❌ Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nInterrumpido por el usuario. Cerrando…"); sys.exit(0)
