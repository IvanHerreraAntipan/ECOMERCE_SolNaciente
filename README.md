# Plataforma de Comercio Electrónico — SolNaciente

## 1. Información del Equipo, PO/SM y Responsabilidades
* **Asignatura:** Desarrollo de Aplicaciones Web (Solemne 02)
* **Sección:** [Número de sección]
* **Equipo:** SolNaciente
* **Scrum Master (SM):** Iván Herrera — Facilitación de ceremonias ágiles, remoción de bloqueos y control de flujo en Git.
* **Equipo de Desarrollo (Developers):**
  * Benjamín Lagos — Backend y persistencia relacional en PostgreSQL (Gestión y Comercio).
  * Benjamín Diaz — Backend NoSQL en MongoDB, transacciones atómicas y pasarela de pago.
  * Nikolas Adasme — Frontend React + Vite, temas visuales y diseño responsivo.
  * Benjamín Astorga — Control de calidad, diseño de pruebas de integración y contratos OpenAPI.
  * Thomas Cornejo — Infraestructura cloud, despliegue distribuido, logs y documentación técnica.

---

## 2. Contexto, Alcance y Mejoras Opcionales
### 2.1 Contexto
Plataforma de comercio electrónico con arquitectura orientada a microservicios para el rubro de **Tenis de Mesa (SolNaciente)**. La solución integra catálogo técnico (maderos, gomas, pelotas, zapatillas y mesas), carrito de compras persistente, autenticación basada en roles, reservas atómicas con control estricto de concurrencia e integración con pasarela de pago en ambiente sandbox (sin cobros reales).

### 2.2 Alcance Obligatorio
* **Páginas públicas:** Inicio, Catálogo, Detalle de producto con galería (4 a 6 imágenes), Carrito, Autenticación, Registro, Checkout/Pago, Resumen/Confirmación de compra, Contacto y Quiénes somos.
* **Panel de administración:** Gestión de usuarios (bloqueo/activación con protección del último admin), creación y edición de productos, ajuste de existencias físicas respetando reservas, administración de contenidos CMS (textos, banners, enlaces) y selección de 4 temas visuales sin modificar código ni redesplegar.
* **Moneda:** Pesos chilenos (CLP).

### 2.3 Exclusiones del Alcance
Conforme al enunciado, la solución no exige despacho físico, facturación electrónica tributaria, cupones de descuento, valoraciones/reseñas de usuarios ni soporte multimoneda.

---

## 3. Arquitectura, Diagramas, Servicios y Datos
La solución se compone de 3 microservicios backend independientes y desacoplados junto a una aplicación cliente en React:

```text
                               +-----------------------------+
                               |     Frontend (React + Vite)  |
                               |    http://localhost:5173    |
                               +--------------+--------------+
                                              |
                   +--------------------------+--------------------------+
                   | (REST / OpenAPI)         | (REST / OpenAPI)         | (REST / OpenAPI)
                   v                          v                          v
       +-----------------------+  +-----------------------+  +-----------------------+
       |  Servicio de Gestión  |  |  Catálogo e Inventario|  |  Servicio de Comercio |
       | http://localhost:8001 |  | http://localhost:8002 |  | http://localhost:8003 |
       +-----------+-----------+  +-----------+-----------+  +-----------+-----------+
                   |                          |                          |
                   v                          v                          v
       +-----------------------+  +-----------------------+  +-----------------------+
       | PostgreSQL (Port 5433)|  |  MongoDB (Port 27017) |  | PostgreSQL (Port 5433)|
       |   ecommerce_gestion   |  |   ecommerce_catalogo  |  |   ecommerce_comercio  |
       |  (Usuarios/Roles/CMS) |  | (Productos/Inventario)|  | (Órdenes/Pagos/Carros)|
       +-----------------------+  +-----------------------+  +-----------------------+
```

### 3.1 Propiedad de Datos por Servicio (CC-05)
* **Servicio de Gestión:** Almacena usuarios, credenciales hasheadas, roles (Cliente/Admin), estados de cuenta, contenidos dinámicos del CMS y mensajes de contacto en **PostgreSQL** (`ecommerce_gestion`).
* **Servicio de Catálogo e Inventario:** Almacena productos, descripciones, galería de 4 a 6 imágenes, stock físico, stock reservado y registro histórico de movimientos en **MongoDB** (`ecommerce_catalogo`). Utiliza transacciones multidocumento sobre un *Replica Set*.
* **Servicio de Comercio:** Almacena carritos autenticados, snapshots históricos de órdenes, estados de pago y registros de notificación en **PostgreSQL** (`ecommerce_comercio`).

---

## 4. Versiones Fijadas y Compatibilidad Oficial (SCRUM-8 / Hito 1)

En cumplimiento de la sección 5 del enunciado (*«La versión concreta de Django y una versión compatible de DRF deben verificarse en fuentes oficiales y quedar aprobadas en H1, junto con Python, drivers y motores»*), se verificaron las propuestas frente a los repositorios oficiales de **PyPI**, **Django Project** y **Django REST Framework**:

### 4.1 Matriz de Versiones y Justificación Técnica

| Componente | Versión Sugerida en Enunciado | Versión Oficial Fijada | Estado y Justificación Técnica |
| :--- | :--- | :--- | :--- |
| **Lenguaje Backend** | *No especificada* | **Python 3.11.9** | Versión LTS oficial con máximo soporte y compatibilidad para Django 5.1 y drivers nativos de C/C++. |
| **Framework Web** | `Django 6.1.1` | **Django 5.1.15** | **Verificación oficial:** Django 6.x no existe en los registros oficiales de lanzamiento de la Django Software Foundation. La versión mayor estable vigente es Django 5.1. |
| **API REST Toolkit** | `DRF 3.18.1` | **DRF 3.15.2** | **Verificación oficial:** DRF 3.18 no ha sido publicada. La versión oficial compatible y testeada para Django 5.1 es DRF 3.15.2. |
| **Driver PostgreSQL** | *No especificada* | **psycopg 3.2.x (`psycopg[binary]`)** | Conector moderno recomendado por Django 5. Reemplaza a psycopg2 para resolver de raíz problemas de codificación de caracteres en Windows (CP1252/UTF-8). |
| **Motor Relacional** | *No especificada* | **PostgreSQL 16 Alpine** | Motor relacional robusto para gestión de identidad y transacciones de órdenes (puerto 5433 en host). |
| **Driver NoSQL** | *No especificada* | **pymongo 4.19.x** | Driver oficial de MongoDB en Python. Permite ejecutar transacciones multidocumento y operaciones atómicas condicionales (`$inc`, `$gte`). |
| **Motor NoSQL** | *No especificada* | **MongoDB 7.0 (Replica Set `rs0`)** | Configurado en modo réplica para soportar sesiones de transacciones ACID multidocumento requeridas en RF-29. |
| **Especificación API** | *No especificada* | **drf-spectacular 0.30.0** | Generador de esquemas OpenAPI 3.0 interactivo con Swagger UI y Redoc (RNF-05). |
| **Frontend Runtime** | *No especificada* | **Node.js v24.x / npm v11.x** | Entorno de ejecución JavaScript moderno. |
| **Frontend Framework** | React | **React 19 + Vite 8.3** | Compilador ultra-rápido con Hot Module Replacement (HMR) y soporte de variables CSS reactivas para los 4 temas. |

### 4.2 Cuentas y Pasarela Sandbox Aprobada
* **Pasarela de pago:** **Transbank Webpay Plus (Integración)**, operando en moneda nacional (CLP) con código de comercio público `597055555532` y tarjetas de prueba oficiales (ver informe técnico adjunto).

---

## 5. Guía de Instalación y Arranque Limpio (RNF-16)

### Paso 1: Clonar el proyecto
```bash
git clone [https://github.com/IvanHerreraAntipan/ECOMERCE_SolNaciente.git](https://github.com/IvanHerreraAntipan/ECOMERCE_SolNaciente.git)
cd ECOMERCE_SolNaciente
```

### Paso 2: Iniciar bases de datos con Docker
```bash
docker compose up -d
```
Verificar que ambos contenedores (`ecommerce_postgres` y `ecommerce_mongodb`) estén en estado *Running*.  
*(Si es primera vez que se ejecuta, crear la base de datos de comercio en PostgreSQL):*
```bash
docker exec -i ecommerce_postgres psql -U ecommerce_user -d postgres -c "CREATE DATABASE ecommerce_comercio;"
```

### Paso 3: Desplegar Servicio de Gestión (Terminal 1 - Puerto 8001)
```bash
cd services/gestion
python -m venv venv
# Activar entorno virtual:
# En Windows: venv\Scripts\activate | En Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8001
```

### Paso 4: Desplegar Servicio de Catálogo e Inventario (Terminal 2 - Puerto 8002)
```bash
cd services/catalogo-inventario
python -m venv venv
# Activar entorno virtual
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8002
```

### Paso 5: Desplegar Servicio de Comercio (Terminal 3 - Puerto 8003)
```bash
cd services/comercio
python -m venv venv
# Activar entorno virtual
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8003
```

### Paso 6: Desplegar Frontend React (Terminal 4 - Puerto 5173)
```bash
cd frontend
npm install
npm run dev
```

---

## 6. Variables de Entorno (Sin Valores Secretos)
Cada servicio incluye un archivo `.env.example` libre de credenciales sensibles (RNF-12):

* **`services/gestion/.env.example`:**
  ```env
  DEBUG=True
  SECRET_KEY=clave-ejemplo-gestion
  ALLOWED_HOSTS=localhost,127.0.0.1
  DB_NAME=ecommerce_gestion
  DB_USER=ecommerce_user
  DB_PASSWORD=ecommerce_password
  DB_HOST=127.0.0.1
  DB_PORT=5433
  CORS_ALLOWED_ORIGINS=http://localhost:5173,[http://127.0.0.1:5173](http://127.0.0.1:5173)
  ```
* **`services/catalogo-inventario/.env.example`:**
  ```env
  DEBUG=True
  SECRET_KEY=clave-ejemplo-catalogo
  ALLOWED_HOSTS=localhost,127.0.0.1
  MONGO_URI=mongodb://127.0.0.1:27017/?replicaSet=rs0
  MONGO_DB_NAME=ecommerce_catalogo
  CORS_ALLOWED_ORIGINS=http://localhost:5173,[http://127.0.0.1:5173](http://127.0.0.1:5173)
  ```
* **`services/comercio/.env.example`:**
  ```env
  DEBUG=True
  SECRET_KEY=clave-ejemplo-comercio
  ALLOWED_HOSTS=localhost,127.0.0.1
  DB_NAME=ecommerce_comercio
  DB_USER=ecommerce_user
  DB_PASSWORD=ecommerce_password
  DB_HOST=127.0.0.1
  DB_PORT=5433
  CORS_ALLOWED_ORIGINS=http://localhost:5173,[http://127.0.0.1:5173](http://127.0.0.1:5173)
  ```

---

## 7. Datos Iniciales y Primer Administrador Seguro
Para cumplir con RB-06, RB-07 y el requisito de seguridad que prohíbe exponer contraseñas en scripts públicos:

1. Ejecutar el comando seguro de creación de superusuario en el servicio de gestión:
   ```bash
   cd services/gestion
   python manage.py createsuperuser --username admin --email admin@tienda.cl
   ```
2. La contraseña debe ingresarse de forma interactiva en la terminal sin quedar registrada en el historial de Git.
3. El primer administrador se inicializa con estado `ACTIVO` y rol `ADMINISTRADOR`.

---

## 8. Pruebas, Estados, Reservas e Idempotencia
### 8.1 Máquina de Estados de la Orden (Sección 5)
La orden de compra transita estrictamente por los siguientes estados:
1. `PENDIENTE_PAGO`: Carrito validado, orden creada con snapshot histórico y reserva indivisible de stock asignada en MongoDB.
2. `CONFIRMACION_PENDIENTE`: Pago aprobado por la pasarela, pendiente de confirmación de consolidación de inventario.
3. `CONFIRMADA`: Pago verificado + stock consolidado con éxito (`stock_fisico -= n`, `stock_reservado -= n`).
4. `RECHAZADA`: Transacción declinada por la pasarela de pago; se liberan las unidades reservadas (`stock_reservado -= n`).
5. `CANCELADA`: El cliente interrumpe el flujo; reserva liberada inmediatamente.
6. `VENCIDA`: Expiración de la reserva de 15 minutos sin confirmación de pago; el stock reservado se libera tras conciliación.
7. `REVISION_REQUERIDA`: Inconsistencia detectada (ej. pago aprobado tardíamente sobre stock agotado); requiere compensación o revisión administrativa sin forzar inventario negativo.

### 8.2 Modelo de Inventario Atómico y Concurrencia
* **Invariante:** `stock_disponible = stock_fisico - stock_reservado`.
* La reserva del carrito es indivisible: si falla una sola línea, ninguna queda reservada.
* **Control de concurrencia (RNF-08):** Operación atómica condicional sobre MongoDB:
  ```javascript
  db.productos.updateOne(
    { _id: id_producto, stock_fisico: { $gte: stock_reservado + cantidad } },
    { $inc: { stock_reservado: cantidad } }
  )
  ```
* **Idempotencia de pagos (RB-09 / RNF-09):** Procesamiento de webhooks con verificación de token y registro de eventos para ignorar notificaciones duplicadas sin duplicar compras ni descuentos de existencias.

---

## 9. URLs, Plataformas, Cuotas y Persistencia
### 9.1 Entorno Local
* **Frontend:** `http://localhost:5173/`
* **API Gestión y Swagger:** `http://localhost:8001/api/docs/`
* **API Catálogo y Swagger:** `http://localhost:8002/api/docs/`
* **API Comercio y Swagger:** `http://localhost:8003/api/docs/`

### 9.2 Entorno Remoto (Despliegue Hito 1 / SCRUM-14)
* **Frontend en Producción:** Desplegado con HTTPS en Vercel.
* **Backends y Bases Remotas (H4):** Render / Neon / MongoDB Atlas (M0 Replica Set).

---

## 10. Logs, Reintentos, Respaldos y Recuperación (RNF-18 / RF-38)
* **Sanitización de logs:** Registro de eventos críticos (intentos de login, bloqueos, reservas y conciliaciones) sanitizando contraseñas, tokens y datos bancarios.
* **Notificaciones por correo (RF-36 y RF-37):** Registro independiente de envíos de correo por orden con control de estado (`ENVIADO`, `FALLIDO`, `PENDIENTE`). Un fallo de correo no revierte la compra y admite reintento manual desde el panel de administración.
* **Conciliación (RF-38):** Endpoint y tarea administrativa para detectar órdenes en estado `CONFIRMACION_PENDIENTE` o interrupciones de red, consultando la pasarela y forzando liberación o confirmación idempotente.

---

## 11. Trazabilidad, Flujo Git y Limitaciones Conocidas
* **Estrategia de ramas:**
  * `main`: Rama de producción estable.
  * `develop`: Integración de sprints e hitos.
  * `feature/<nombre-tarea>`: Ramas de trabajo individuales con Pull Requests vinculados a historias de usuario (RNF-15).
* **Mínimo de contribuciones:** Cada integrante mantiene un registro auditable de al menos 7 contribuciones significativas en el historial de Git.
* **Limitaciones conocidas:** En ambiente local de Windows, PostgreSQL se mapea al puerto `5433` para evitar conflictos con instancias nativas previas del sistema operativo.

---

## 12. Procedencia y Licencias de Recursos
* **Iconografía:** Lucide React / Heroicons (Licencia MIT).
* **Imágenes de catálogo:** Recursos libres de derechos obtenidos de Unsplash / Pexels.
* **Tipografías:** Google Fonts (Inter / Roboto, Licencia Open Font License).
* **Frameworks y librerías:** Django (BSD-3), React (MIT), Vite (MIT), DRF (BSD-3), MongoDB PyMongo (Apache 2.0).