#Engine Monitoring System
import logging

class EngineMonitoringSystem:
     
    _ON = 1
    _OFF = 0

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.temperature = 27 
        self.pressure = 0
        self.RPM = 0
        self.gas_level = 100
        self.status = self._OFF
        
        # LOG: Reportar inicialización
        self.logger.info(f"Sistema inicializado - Temp={self.temperature}°C, Presión={self.pressure} PSI, RPM={self.RPM}, Combustible={self.gas_level}%, Estado=APAGADO")

    def motor_on(self):
        self.logger.debug(f"Estado actual antes de encender: Gas={self.gas_level}%, Status={self.status}")
        
        if self.gas_level > 0:
            self.status = self._ON
            self.RPM = 1000
            self.pressure = 45
            self.temperature = 85
            
            self.logger.info("Motor encendido correctamente")
            self.logger.debug(f"Parámetros iniciales: RPM={self.RPM}, Temp={self.temperature}°C, Presión={self.pressure} PSI")
            
            # LOG: Reportar estado completo después de encender
            self.logger.info(f"Estado actual - ENCENDIDO: Temp={self.temperature}°C, Presión={self.pressure} PSI, RPM={self.RPM}, Combustible={self.gas_level}%")
        else:
            self.logger.error("Fallo crítico: Intento de encender sin combustible")
            # LOG: Reportar que el motor sigue apagado
            self.logger.info(f"Estado actual - APAGADO: Temp={self.temperature}°C, Presión={self.pressure} PSI, RPM={self.RPM}, Combustible={self.gas_level}%")

    def motor_off(self):
        self.status = self._OFF
        self.RPM = 0
        self.pressure = 0
        self.temperature = 27
        
        # LOG: Reportar apagado
        self.logger.info("Motor apagado correctamente")
        self.logger.info(f"Estado actual - APAGADO: Temp={self.temperature}°C, Presión={self.pressure} PSI, RPM={self.RPM}, Combustible={self.gas_level}%")

    def update_parameters(self, temperature, pressure, RPM, gas_level):
        self.logger.debug(f"Actualizando parámetros: Temp={temperature}, Presión={pressure}, RPM={RPM}, Gas={gas_level}")

        if self.status == self._ON:
            self.temperature = temperature
            self.pressure = pressure
            self.RPM = RPM
            self.gas_level = gas_level
            
            self.logger.info("Parámetros actualizados correctamente")
            # LOG: Reportar nuevos valores
            self.logger.info(f"Estado actual - ENCENDIDO: Temp={self.temperature}°C, Presión={self.pressure} PSI, RPM={self.RPM}, Combustible={self.gas_level}%")
        else:
            self.logger.warning("Intento de actualizar parámetros con motor apagado")
            # LOG: Reportar que no hubo cambios
            self.logger.info(f"Estado actual - APAGADO: Temp={self.temperature}°C, Presión={self.pressure} PSI, RPM={self.RPM}, Combustible={self.gas_level}%")

    def motor_status(self):
        results = {}
        
        # Verificar temperatura (80-120°C)
        if 80 <= self.temperature <= 120:
            results['temperature'] = 'OK'
        elif 70 <= self.temperature < 80 or 120 < self.temperature <= 130:
            results['temperature'] = 'WARNING'
        else:
            results['temperature'] = 'CRITICAL'
        
        # Verificar presión (40-80 PSI)
        if 40 <= self.pressure <= 80:
            results['pressure'] = 'OK'
        elif 30 <= self.pressure < 40 or 80 < self.pressure <= 90:
            results['pressure'] = 'WARNING'
        else:
            results['pressure'] = 'CRITICAL'
        
        # Verificar RPM (1000-5000)
        if 1000 <= self.RPM <= 5000:
            results['RPM'] = 'OK'
        elif 800 <= self.RPM < 1000 or 5000 < self.RPM <= 5500:
            results['RPM'] = 'WARNING'
        else:
            results['RPM'] = 'CRITICAL'
        
        # Verificar combustible (0-100%)
        if self.gas_level > 20:
            results['gas_level'] = 'OK'
        elif 10 <= self.gas_level <= 20:
            results['gas_level'] = 'WARNING'
        else:
            results['gas_level'] = 'CRITICAL'

        for param, status in results.items():
            if status == 'WARNING':
                self.logger.warning(f"{param} fuera de rango óptimo: {getattr(self, param)}")
            elif status == 'CRITICAL':
                self.logger.critical(f"{param} en nivel CRÍTICO: {getattr(self, param)}")
            else:
                self.logger.debug(f"{param} en rango normal: {getattr(self, param)}")
        
        # LOG: Reportar resumen de verificación
        self.logger.info(f"Verificación de estado completada - Temp:{results['temperature']}, Presión:{results['pressure']}, RPM:{results['RPM']}, Combustible:{results['gas_level']}")
        
        return results
    
    def get_status(self):
        status_str = "ENCENDIDO" if self.status == self._ON else "APAGADO"
        return f"""
        === Estado del Motor ===
        Estado: {status_str}
        Temperatura: {self.temperature}°C
        Presión: {self.pressure} PSI
        RPM: {self.RPM}
        Combustible: {self.gas_level}%
        """

    def __str__(self):
        return self.get_status()
    
    def is_running(self):
        return self.status == self._ON