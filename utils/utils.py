from datetime import datetime

class Utilities:
    @staticmethod
    def convertDateTimeToStr(obj):
        """
        Convierte objetos datetime a cadenas (formato YYYY-MM-DD HH:MM:SS) en un diccionario o lista.
        """
        if isinstance(obj, dict):
            return {k: Utilities.convertDateTimeToStr(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Utilities.convertDateTimeToStr(v) for v in obj]
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')  # Formato deseado
        else:
            return obj
