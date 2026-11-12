"""Cliente de Gemini simulado: no hace llamadas de red ni consume cuota."""

from google.genai import types


def respuesta_llamada(nombre: str, argumentos: dict | None = None) -> types.GenerateContentResponse:
    llamada = types.FunctionCall(name=nombre, args=argumentos or {})
    contenido = types.Content(role="model", parts=[types.Part(function_call=llamada)])
    return types.GenerateContentResponse(candidates=[types.Candidate(content=contenido)])


def respuesta_texto(texto: str) -> types.GenerateContentResponse:
    contenido = types.Content(role="model", parts=[types.Part(text=texto)])
    return types.GenerateContentResponse(candidates=[types.Candidate(content=contenido)])


def respuesta_vacia() -> types.GenerateContentResponse:
    return types.GenerateContentResponse(candidates=[])


class _Modelos:
    def __init__(self, secuencia):
        self._secuencia = list(secuencia)
        self.llamadas: list[dict] = []

    def generate_content(self, model, contents, config):
        self.llamadas.append({"model": model, "contents": list(contents), "config": config})
        if not self._secuencia:
            raise AssertionError("El agente hizo más llamadas de las previstas")
        siguiente = self._secuencia.pop(0)
        if isinstance(siguiente, Exception):
            raise siguiente
        return siguiente


class ClienteFalso:
    def __init__(self, *secuencia):
        self.models = _Modelos(secuencia)

    @property
    def llamadas(self):
        return self.models.llamadas


def resultados_enviados(cliente: ClienteFalso) -> list[dict]:
    """Respuestas de herramienta que el agente envió de vuelta al modelo."""
    salida = []
    for llamada in cliente.llamadas:
        for contenido in llamada["contents"]:
            for parte in contenido.parts or []:
                if parte.function_response is not None:
                    salida.append(parte.function_response.response)
    return salida
