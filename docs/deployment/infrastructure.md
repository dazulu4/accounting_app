# Infraestructura de Despliegue

Este documento describe la infraestructura de nube utilizada para desplegar la aplicación en el entorno de Producción. Utilizamos **AWS (Amazon Web Services)** y el modelo de **Infraestructura como Código (IaC)** a través de **AWS SAM (Serverless Application Model)**.

---

## Componentes Principales de la Infraestructura

La arquitectura de despliegue se basa en un enfoque *serverless* para minimizar la gestión de servidores y maximizar la escalabilidad.

### 1. AWS Lambda

-   **Propósito**: El núcleo de nuestra infraestructura. La aplicación Flask no se ejecuta en un servidor tradicional, sino que está empaquetada como una **función AWS Lambda**.
-   **Funcionamiento**: Cada petición HTTP que llega a la API activa una instancia de la función Lambda, que procesa la petición y devuelve una respuesta.
-   **Ventajas**:
    -   **Escalabilidad Automática**: AWS se encarga de escalar el número de instancias de la función según la demanda.
    -   **Pago por Uso**: Solo pagamos por el tiempo de computación que utilizamos.

### 2. Amazon API Gateway

-   **Propósito**: Actúa como la "puerta de entrada" para todas las peticiones a nuestra aplicación. Es un servicio completamente gestionado que expone la función Lambda como una **API RESTful** segura y escalable.
-   **Responsabilidades**:
    -   Enrutamiento de peticiones a la función Lambda.
    -   Gestión de CORS (Cross-Origin Resource Sharing).
    -   Autorización y control de acceso (aunque no se detalla en este documento).
    -   Limitación de peticiones (throttling) para proteger el backend.

### 3. AWS Systems Manager (SSM) Parameter Store

-   **Propósito**: Se utiliza para almacenar de forma segura parámetros de configuración que no son secretos, como el host y el puerto de la base de datos.
-   **Seguridad**: Nos permite separar la configuración de la aplicación del código fuente. Los valores se inyectan en la función Lambda en tiempo de despliegue.

### 4. AWS Secrets Manager

-   **Propósito**: Se utiliza para gestionar los secretos de la aplicación, como la contraseña de la base de datos.
-   **Seguridad**: Secrets Manager ofrece una gestión de secretos más robusta, incluyendo la rotación automática de credenciales. Al igual que con SSM, el secreto se inyecta de forma segura en la función Lambda en tiempo de desplieg-e.

---

## Infraestructura como Código (IaC) con AWS SAM

Toda esta infraestructura se define y gestiona como código utilizando **AWS SAM**.

-   **`template.yaml`**: Este es el archivo de plantilla de SAM que define todos los recursos de AWS que necesitamos (la función Lambda, la API Gateway, etc.) y cómo se conectan entre sí.
-   **`samconfig.toml`**: Archivo de configuración para los comandos de SAM, que permite definir parámetros específicos para cada entorno (e.g., development vs. producción).

El uso de IaC nos proporciona:
-   **Consistencia**: Garantiza que los entornos de desarrollo y Producción sean lo más parecidos posible.
-   **Automatización**: Permite que el proceso de creación y actualización de la infraestructura sea completamente automático.
-   **Control de Versiones**: La definición de la infraestructura se versiona en Git junto con el código de la aplicación. 