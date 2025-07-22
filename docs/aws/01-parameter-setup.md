# Guía de Configuración de Parámetros en AWS

Esta guía describe cómo configurar los parámetros necesarios en **AWS Systems Manager (SSM) Parameter Store** y **AWS Secrets Manager** para que la aplicación funcione correctamente en un entorno de producción.

## 📋 Resumen de Parámetros

La aplicación requiere los siguientes parámetros, que deben ser creados para cada entorno (ej. `development`, `production`):

| Parámetro Lógico      | Servicio de AWS     | Nombre en AWS                                          | Descripción                                  |
| --------------------- | ------------------- | ------------------------------------------------------ | -------------------------------------------- |
| `DatabaseHost`        | SSM Parameter Store | `/accounting-app/[entorno]/database/host`              | La URL o IP del host de la base de datos RDS. |
| `DatabasePassword`    | Secrets Manager     | `accounting-app/[entorno]/database/password`           | La contraseña para la base de datos.          |

Donde `[entorno]` debe ser reemplazado por `development` o `production`.

---

## 🔐 Paso 1: Configurar la Contraseña en AWS Secrets Manager

La contraseña de la base de datos es un secreto sensible y debe almacenarse de forma segura.

1.  **Navega a AWS Secrets Manager** en la consola de AWS.
2.  Haz clic en **"Store a new secret"** (Almacenar un nuevo secreto).
3.  Selecciona **"Other type of secret"** (Otro tipo de secreto).
4.  En la sección **"Secret key/value"**, crea una clave llamada `password` y en el campo de valor, introduce la contraseña de tu base de datos RDS.
    ```json
    {
      "password": "TU_CONTRASENA_SUPER_SECRETA"
    }
    ```
5.  Haz clic en **"Next"**.
6.  **Dale un nombre al secreto**. Usa la siguiente convención para mantener la consistencia:
    -   Para producción: `accounting-app/production/database/password`
    -   Para desarrollo: `accounting-app/development/database/password`
7.  Añade una descripción si lo deseas (ej. "Contraseña de la base de datos para el entorno de producción").
8.  Deja las demás opciones por defecto (rotación, etc.) y finaliza la creación del secreto.

---

## ⚙️ Paso 2: Configurar el Host en AWS SSM Parameter Store

El host de la base de datos es una configuración menos sensible y puede almacenarse en Parameter Store.

1.  **Navega a AWS Systems Manager** en la consola de AWS.
2.  En el panel de la izquierda, selecciona **"Parameter Store"** bajo "Application Management".
3.  Haz clic en **"Create parameter"** (Crear parámetro).
4.  **Dale un nombre al parámetro**. Usa la siguiente convención:
    -   Para producción: `/accounting-app/production/database/host`
    -   Para desarrollo: `/accounting-app/development/database/host`
    *Nota: El `/` inicial es importante para la organización jerárquica.*
5.  En **"Tier"**, deja la opción `Standard`.
6.  En **"Type"**, selecciona `String`.
7.  En **"Data type"**, deja la opción `text`.
8.  En el campo **"Value"**, introduce el endpoint de tu instancia de base de datos RDS. Por ejemplo: `mydb-instance.random-chars.us-east-1.rds.amazonaws.com`.
9.  Haz clic en **"Create parameter"**.

---

## ✅ Verificación

Una vez que hayas creado ambos recursos (el secreto y el parámetro), el `template.yaml` de AWS SAM podrá resolver estos valores automáticamente durante el despliegue, inyectándolos de forma segura como variables de entorno en la función Lambda. No necesitas hacer nada más en el código.

Asegúrate de que el rol IAM que `sam deploy` utiliza tenga los permisos necesarios para leer desde Secrets Manager y SSM Parameter Store. La política `AWSLambdaBasicExecutionRole` junto con permisos para `ssm:GetParameter` y `secretsmanager:GetSecretValue` es generalmente suficiente. 