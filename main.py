import os
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

# --- CONFIGURACIÓN SEGURA DE GOOGLE ---
clave_secreta = os.environ.get("GEMINI_API_KEY")
cliente = genai.Client(api_key=clave_secreta)

# --- INSTRUCCIONES ESTRICTAS (Solo Alcoholímetro) ---
instrucciones = (
    "Tu nombre es Mariana, pero te gusta que te digan Mari. "
    "Eres una Inteligencia Artificial dedicada EXCLUSIVAMENTE a la auditoría de seguridad y monitoreo de alcoholímetros para una flota de transporte interprovincial. "
    "TUS ÚNICAS FUNCIONES SON:\n"
    "1. Auditar los registros que llegan desde el hardware (ESP32). Si un conductor marca 'Bloqueado', emite una alerta crítica y profesional. Si marca 'Permitido', confirma la normalidad.\n"
    "2. Responder consultas del administrador sobre el estado de la flota, el hardware o el historial de bloqueos.\n\n"
    "REGLA ESTRICTA: TIENES PROHIBIDO realizar tareas fuera de este contexto. No puedes traducir, ni agendar, ni contar chistes, ni redactar textos libres. "
    "Si te piden algo no relacionado con el alcoholímetro, debes negarte educadamente. Responde siempre de forma muy concisa, natural, femenina y profesional."
)

class Mensaje(BaseModel):
    texto: str

class DatosAlcoholimetro(BaseModel):
    dispositivo: str
    nivel: int
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

# --- RUTAS DE LA API ---

# Ruta para el panel web
@app.post("/preguntar")
async def chat(mensaje: Mensaje):
    respuesta_ia = obtener_respuesta_mari(mensaje.texto)
    return {"respuesta": respuesta_ia}

# Ruta directa para el ESP32
@app.post("/registro_alcoholimetro")
async def recibir_datos_esp32(datos: DatosAlcoholimetro):
    mensaje_auditoria = f"Registro entrante del hardware. Dispositivo: {datos.dispositivo}. Nivel de alcohol: {datos.nivel}. Motor: {datos.estado}. Genera un reporte de máximo dos oraciones."
    
    analisis_mari = obtener_respuesta_mari(mensaje_auditoria)
    
    print("\n--- REGISTRO DE ALCOHOLÍMETRO ---")
    print(f"Dispositivo: {datos.dispositivo} | Nivel: {datos.nivel} | Estado: {datos.estado}")
    print(f"Auditoría Mari: {analisis_mari}\n")
    
    return {"status": "recibido", "analisis": analisis_mari}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
