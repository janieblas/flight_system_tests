import pytest
import logging
from src.EMS import EngineMonitoringSystem


class TestRequerimientosfuncionales:

    @pytest.fixture(autouse=True)
    def setup_logging(self):
        """Configurar logging antes de cada test"""
        # Limpiar handlers existentes
        logging.root.handlers = []
        
        # Configurar logging para tests
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/test_engine.log',
            filemode='w'
        )
        yield
        # Cleanup después del test
        logging.shutdown()

    def test_TC001_Verificar_Inicialización_del_Sistema(self):
        """TC-001: Verificar Inicialización del Sistema con manejo de errores"""
        try:
            # ARRANGE & ACT
            motor = EngineMonitoringSystem()
            logging.shutdown()
            
            # ASSERT - Leer logs
            try:
                with open('logs/test_engine.log', 'r') as f:
                    log_content = f.read()
            except FileNotFoundError:
                pytest.fail("El archivo de log no fue creado")
            except PermissionError:
                pytest.fail("No hay permisos para leer el archivo de log")
            
            # Verificaciones
            assert "Sistema inicializado" in log_content
            assert "Temp=27°C" in log_content
            assert "Presión=0 PSI" in log_content
            assert "RPM=0" in log_content
            assert "Combustible=100%" in log_content
            assert "Estado=APAGADO" in log_content
            
            assert "ERROR" not in log_content
            assert "CRITICAL" not in log_content
            
        except Exception as e:
            pytest.fail(f"Error inesperado durante la inicialización: {str(e)}")

    def test_TC002_verificar_encendido_motor(self):
        """TC-002 (RF-002): Verificar Encendido del Motor"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        
        # ACT
        motor.motor_on()
        
        logging.shutdown()
        
        # ASSERT
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        assert "Motor encendido correctamente" in log_content
        assert "Estado actual - ENCENDIDO" in log_content
        assert "Temp=85°C" in log_content
        assert "Presión=45 PSI" in log_content
        assert "RPM=1000" in log_content
        
        assert "INFO" in log_content
        assert "ERROR" not in log_content

    def test_TC003_verificar_fallo_encendido_sin_combustible(self):
        """TC-003 (RF-003): Verificar Fallo de Encendido sin Combustible"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        motor.gas_level = 0  # Establecer combustible en 0
        
        # ACT
        motor.motor_on()
        
        logging.shutdown()
        
        # ASSERT
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        # Verificar mensaje de error
        assert "ERROR" in log_content
        assert "Fallo crítico: Intento de encender sin combustible" in log_content
        
        # Verificar que el motor permanece APAGADO
        assert "Estado actual - APAGADO" in log_content
        assert "Temp=27°C" in log_content
        assert "Presión=0 PSI" in log_content
        assert "RPM=0" in log_content
        
        # NO debe aparecer mensaje de encendido exitoso
        assert "Motor encendido correctamente" not in log_content

    def test_TC004_verificar_apagado_motor(self):
        """TC-004 (RF-004): Verificar Apagado del Motor"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        motor.motor_on()  # Primero encender
        
        # Guardar nivel de combustible actual
        gas_inicial = motor.gas_level
        
        # ACT
        motor.motor_off()
        
        logging.shutdown()
        
        # ASSERT
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        # Verificar mensajes de apagado
        assert "Motor apagado correctamente" in log_content
        assert "Estado actual - APAGADO" in log_content
        assert "Temp=27°C" in log_content
        assert "Presión=0 PSI" in log_content
        assert "RPM=0" in log_content
        
        # Verificar que combustible no cambió
        assert motor.gas_level == gas_inicial
        assert f"Combustible={gas_inicial}%" in log_content
        
        # Verificar secuencia: primero encendido, luego apagado
        assert log_content.index("Motor encendido") < log_content.index("Motor apagado")

    def test_TC005_verificar_actualizacion_parametros_motor_encendido(self):
        """TC-005 (RF-005): Verificar Actualización de Parámetros con Motor Encendido"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        motor.motor_on()
        
        # ACT
        motor.update_parameters(100, 50, 2500, 80)
        
        logging.shutdown()
        
        # ASSERT
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        # Verificar logs de actualización
        assert "DEBUG" in log_content
        assert "Actualizando parámetros: Temp=100, Presión=50, RPM=2500, Gas=80" in log_content
        assert "Parámetros actualizados correctamente" in log_content
        
        # Verificar valores actualizados en log
        assert "Estado actual - ENCENDIDO" in log_content
        assert "Temp=100°C" in log_content
        assert "Presión=50 PSI" in log_content
        assert "RPM=2500" in log_content
        assert "Combustible=80%" in log_content
        
        # Verificar valores en el objeto
        assert motor.temperature == 100
        assert motor.pressure == 50
        assert motor.RPM == 2500
        assert motor.gas_level == 80

    def test_TC006_verificar_rechazo_actualizacion_motor_apagado(self):
        """TC-006 (RF-005): Verificar Rechazo de Actualización con Motor Apagado"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()  # Motor apagado por defecto
        
        # ACT
        motor.update_parameters(100, 50, 2500, 80)
        
        logging.shutdown()
        
        # ASSERT
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        # Verificar mensaje de advertencia
        assert "WARNING" in log_content
        assert "Intento de actualizar parámetros con motor apagado" in log_content
        
        # Verificar que los parámetros NO cambiaron
        assert "Estado actual - APAGADO" in log_content
        assert "Temp=27°C" in log_content
        assert "Presión=0 PSI" in log_content
        assert "RPM=0" in log_content
        assert "Combustible=100%" in log_content
        
        # NO debe aparecer mensaje de actualización exitosa
        assert "Parámetros actualizados correctamente" not in log_content
        
        # Verificar valores en el objeto (sin cambios)
        assert motor.temperature == 27
        assert motor.pressure == 0
        assert motor.RPM == 0
        assert motor.gas_level == 100

    def test_TC007_verificar_is_running_motor_encendido(self):
        """TC-007 (RF-006): Verificar is_running() con Motor Encendido"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        
        # ACT
        motor.motor_on()
        resultado = motor.is_running()
        
        logging.shutdown()
        
        # ASSERT
        assert resultado == True
        
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        # Verificar que el encendido fue exitoso
        assert "Motor encendido correctamente" in log_content
        assert "ERROR" not in log_content

    def test_TC008_verificar_is_running_motor_apagado(self):
        """TC-008 (RF-006): Verificar is_running() con Motor Apagado"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        
        # ACT
        resultado = motor.is_running()
        
        logging.shutdown()
        
        # ASSERT
        assert resultado == False
        
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        # No debe haber errores
        assert "ERROR" not in log_content
        assert "CRITICAL" not in log_content

    def test_TC009_verificar_reporte_estado_completo(self):
        """TC-009 (RF-007): Verificar Reporte de Estado Completo"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        motor.motor_on()
        motor.update_parameters(95, 60, 3000, 75)
        
        # ACT
        reporte = motor.get_status()
        
        logging.shutdown()
        
        # ASSERT - Verificar contenido del reporte
        assert "Estado: ENCENDIDO" in reporte
        assert "Temperatura: 95°C" in reporte
        assert "Presión: 60 PSI" in reporte
        assert "RPM: 3000" in reporte
        assert "Combustible: 75%" in reporte
        
        # Verificar logs de operaciones previas
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        assert "Motor encendido correctamente" in log_content
        assert "Parámetros actualizados correctamente" in log_content

    def test_TC010_verificar_multiples_ciclos_encendido_apagado(self):
        """TC-010 (RF-002, RF-004): Verificar Múltiples Ciclos de Encendido/Apagado"""
        
        # ARRANGE
        motor = EngineMonitoringSystem()
        
        # ACT - 3 ciclos de encendido/apagado
        for i in range(3):
            motor.motor_on()
            assert motor.is_running() == True, f"Ciclo {i+1}: Motor no encendió"
            
            motor.motor_off()
            assert motor.is_running() == False, f"Ciclo {i+1}: Motor no apagó"
        
        logging.shutdown()
        
        # ASSERT
        with open('logs/test_engine.log', 'r') as f:
            log_content = f.read()
        
        # Contar ocurrencias de mensajes clave
        encendidos = log_content.count("Motor encendido correctamente")
        apagados = log_content.count("Motor apagado correctamente")
        
        assert encendidos == 3, f"Esperaba 3 encendidos, encontré {encendidos}"
        assert apagados == 3, f"Esperaba 3 apagados, encontré {apagados}"
        
        # Verificar estado final
        assert motor.is_running() == False
        assert "Estado actual - APAGADO" in log_content

    def test_TC010_verificar_multiples_ciclos_encendido_apagado(self):
        """TC-010: Verificar Múltiples Ciclos con manejo robusto de errores"""
        
        try:
            # ARRANGE
            motor = EngineMonitoringSystem()
            
            # ACT - 3 ciclos de encendido/apagado
            for i in range(3):
                try:
                    # Encender
                    motor.motor_on()
                    if not motor.is_running():
                        raise AssertionError(f"Ciclo {i+1}: Motor no encendió correctamente")
                    
                    # Apagar
                    motor.motor_off()
                    if motor.is_running():
                        raise AssertionError(f"Ciclo {i+1}: Motor no apagó correctamente")
                        
                except AssertionError as e:
                    pytest.fail(f"Fallo en ciclo {i+1}: {str(e)}")
                except Exception as e:
                    pytest.fail(f"Error inesperado en ciclo {i+1}: {str(e)}")
            
            logging.shutdown()
            
            # ASSERT - Verificar logs
            try:
                with open('logs/test_engine.log', 'r') as f:
                    log_content = f.read()
            except FileNotFoundError:
                pytest.fail("El archivo de log no existe después de los ciclos")
            
            # Contar ocurrencias
            encendidos = log_content.count("Motor encendido correctamente")
            apagados = log_content.count("Motor apagado correctamente")
            
            if encendidos != 3:
                pytest.fail(f"Esperaba 3 encendidos, encontré {encendidos}")
            if apagados != 3:
                pytest.fail(f"Esperaba 3 apagados, encontré {apagados}")
            
            # Verificar estado final
            assert motor.is_running() == False, "El motor debería estar apagado al final"
            assert "Estado actual - APAGADO" in log_content
            
        except Exception as e:
            pytest.fail(f"Error crítico durante ciclos múltiples: {str(e)}")