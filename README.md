# Plataforma de Comercio Electrónico — Solemne 02

## 1. Información del Equipo, PO/SM y Responsabilidades
* **Asignatura:** Desarrollo de Aplicaciones Web
* **Sección:** [Número de sección]
* **Equipo:** [SolNaciente]
* **Scrum Master (SM):** [Iván Herrera] — Facilitación de ceremonias ágiles, remoción de bloqueos y control de flujo en Git.
* **Equipo de Desarrollo (Developers):**
  * [Benjamín Lagos] — Backend y persistencia relacional en PostgreSQL (Gestión y Comercio).
  * [Benjamín Diaz] — Backend NoSQL en MongoDB, transacciones atómicas y pasarela de pago.
  * [Nikolas Adasme] — Frontend React + Vite, temas visuales y diseño responsivo.
  * [Benjamín Astorga] — ().
  * [Thomas Cornejo] — ().

---

## 2. Contexto, Alcance y Mejoras Opcionales
### 2.1 Contexto
Plataforma de comercio electrónico con arquitectura orientada a microservicios para un rubro comercial definido por el equipo. La solución integra un catálogo dinámico, carrito de compras persistente, autenticación basada en roles, reservas atómicas con control estricto de concurrencia e integración con pasarela de pago en ambiente sandbox (sin cobros reales).

### 2.2 Alcance Obligatorio
* **Páginas públicas:** Inicio, Catálogo, Detalle de producto con galería (4 a 6 imágenes), Carrito, Autenticación, Registro, Checkout/Pago, Resumen/Confirmación de compra, Contacto y Quiénes somos.
* **Panel de administración:** Gestión de usuarios (bloqueo/activación), creación y edición de productos, ajuste de existencias físicas, administración de contenidos CMS (textos, banners, enlaces) y selección de 4 temas visuales sin modificar código ni redesplegar.
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

## 4. Versiones, Compatibilidad, Prerrequisitos y Cuentas
### 4.1 Entorno de Ejecución
* **Python:** 3.11.x (verificado y compatible con Django 5.1).
* **Node.js:** v20.x o superior (verificado con Node v24.x y npm v11.x).
* **Docker Desktop:** Versión 4.x o superior con soporte para Docker Compose v2.

### 4.2 Motores y Drivers
* **PostgreSQL:** 16-alpine (puerto externo `5433`, interno `5432`). Driver Python: `psycopg` (v3 binario).
* **MongoDB:** 7.0 (puerto `27017`) con replica set `rs0` inicializado. Driver Python: `pymongo` 4.x.
* **Django:** 5.1.x y **Django REST Framework:** 3.15.x.
* **Documentación OpenAPI:** `drf-spectacular` 0.30.x.

### 4.3 Cuentas y Pasarela Sandbox
* **Pasarela de pago:** Cuenta activa en entorno de pruebas (Sandbox de Webpay Plus / Transbank o Mercado Pago en modo test).

---

## 5. Guía de Instalación y Arranque Limpio (RNF-16)

### Paso 1: Clonar el proyecto
```bash
git clone <URL_DEL_REPOSITORIO>
cd ECOMERCE
```

### Paso 2: Iniciar bases de datos con Docker
```bash
docker compose up -d
```
*(Si es primera vez que se ejecuta, crear la base de datos de comercio):*
```bash
docker exec -i ecommerce_postgres psql -U ecommerce_user -d postgres -c "CREATE DATABASE ecommerce_comercio;"
```

### Paso 3: Desplegar Servicio de Gestión (Terminal 1)
```bash
cd services/gestion
python -m venv venv
# Activar entorno virtual:
# En Windows: venv\Scripts\activate
# En Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8001
```

### Paso 4: Desplegar Servicio de Catálogo e Inventario (Terminal 2)
```bash
cd services/catalogo-inventario
python -m venv venv
# Activar entorno virtual
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8002
```

### Paso 5: Desplegar Servicio de Comercio (Terminal 3)
```bash
cd services/comercio
python -m venv venv
# Activar entorno virtual
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8003
```

### Paso 6: Desplegar Frontend React (Terminal 4)
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
  CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
  ```
* **`services/catalogo-inventario/.env.example`:**
  ```env
  DEBUG=True
  SECRET_KEY=clave-ejemplo-catalogo
  ALLOWED_HOSTS=localhost,127.0.0.1
  MONGO_URI=mongodb://127.0.0.1:27017/?replicaSet=rs0
  MONGO_DB_NAME=ecommerce_catalogo
  CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
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
  CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
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

### 9.2 Entorno Remoto (Despliegue Hito 4)
* **Frontend:** Desplegado en Vercel / Netlify.
* **Backends:** Desplegados en Render / Railway con contenedores independientes.
* **Persistencia remota:** PostgreSQL en Neon/Supabase y MongoDB en MongoDB Atlas (M0 Free Tier con Replica Set habilitado).

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