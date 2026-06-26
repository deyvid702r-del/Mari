import os
import urllib.request
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

clave_secreta = os.environ.get("GEMINI_API_KEY")
cliente = genai.Client(api_key=clave_secreta)

# Pega aquí tu URL de Google Sheets (La misma del ESP32)
URL_SHEETS = "https://docs.google.com/spreadsheets/d/153SyU2r20WgFcZQq0Me-ZiLQVTkcw4iwhczdmH75VlY/edit?gid=0#gid=0"

instrucciones = (
    "Tu nombre es Mari. Eres una Inteligencia Artificial dedicada a la auditoría de seguridad de una flota de transporte. "
    "Cuando el administrador te haga una consulta, el sistema te adjuntará la BASE DE DATOS ACTUAL extraída directamente de los sensores. "
    "TUS REGLAS:\n"
    "1. Basa tus respuestas ÚNICAMENTE en la base de datos que se te adjunta.\n"
    "2. Si te piden un reporte de bloqueados, busca en los datos las filas con estado 'Bloqueado' y menciona la fecha, hora y el nivel de alcohol (g/L).\n"
    "3. Si no hay bloqueados en los datos, dilo claramente.\n"
    "4. Responde de forma concisa, ejecutiva y con voz femenina."
    "5. Si puedes generar reportes si te lo piden"
)

class Mensaje(BaseModel):
    texto: str

class DatosAlcoholimetro(BaseModel):
    dispositivo: str
    nivel: float
    estado: str

def obtener_respuesta_mari(mensaje_usuario):
    try:
        response = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=mensaje_usuario,
            config=types.GenerateContentConfig(
                system_instruction=instrucciones,
            )
        )
        return response.text
    except Exception as e:
        return f"Error con la API: {str(e)}"

# --- RUTA PARA EL CHAT WEB ---
@app.post("/preguntar")
async def chat(mensaje: Mensaje):
    # 1. Mari descarga la base de datos en tiempo real
    datos_historial = ""
    try:
        req = urllib.request.urlopen(URL_SHEETS)
        datos_bd = req.read().decode('utf-8')
        datos_historial = f"\n\n--- BASE DE DATOS ACTUAL (Google Sheets) ---\n{datos_bd}\n-----------------------------------\n"
    except Exception as e:
        datos_historial = "\n[Alerta del sistema: No se pudo conectar a Google Sheets para verificar los registros actuales.]"

    # 2. Le enviamos tu pregunta JUNTO con todo el Excel para que lo analice
    prompt_completo = f"Pregunta del administrador: {mensaje.texto} {datos_historial}"
    
    respuesta_ia = obtener_respuesta_mari(prompt_completo)
    return {"respuesta": respuesta_ia}

# --- RUTA PARA EL ESP32 ---
@app.post("/registro_alcoholimetro")
async def recibir_datos_esp32(datos: DatosAlcoholimetro):
    mensaje_auditoria = f"El hardware acaba de registrar una lectura. Dispositivo: {datos.dispositivo}. Nivel: {datos.nivel} g/L. Estado: {datos.estado}. Genera una alerta ejecutiva de máximo dos oraciones."
    analisis_mari = obtener_respuesta_mari(mensaje_auditoria)
    return {"status": "recibido", "analisis": analisis_mari}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
