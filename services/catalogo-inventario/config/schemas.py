from datetime import datetime

def validar_producto(data):
    """Valida los campos obligatorios según la sección 5 del enunciado."""
    errores = {}
    
    # Nombre y descripción
    if not data.get('nombre') or not str(data.get('nombre')).strip():
        errores['nombre'] = 'El nombre no puede estar vacío.'
    if not data.get('descripcion') or not str(data.get('descripcion')).strip():
        errores['descripcion'] = 'La descripción no puede estar vacía.'
        
    # Precio positivo en CLP
    try:
        precio = int(data.get('precio', 0))
        if precio <= 0:
            errores['precio'] = 'El precio debe ser un número entero positivo en CLP.'
    except (ValueError, TypeError):
        errores['precio'] = 'El precio debe ser un número válido.'

    # Stock físico >= 0
    try:
        stock_fisico = int(data.get('stock_fisico', 0))
        if stock_fisico < 0:
            errores['stock_fisico'] = 'El stock físico debe ser mayor o igual a 0.'
    except (ValueError, TypeError):
        errores['stock_fisico'] = 'Stock físico inválido.'

    # RB-05: Entre 4 y 6 imágenes obligatorias
    imagenes = data.get('imagenes', [])
    if not isinstance(imagenes, list) or len(imagenes) < 4 or len(imagenes) > 6:
        errores['imagenes'] = f'El producto debe incluir entre 4 y 6 imágenes obligatorias (recibidas: {len(imagenes) if isinstance(imagenes, list) else 0}).'

    return len(errores) == 0, errores

def construir_producto_dict(data):
    """Construye el documento BSON para insertar en MongoDB."""
    return {
        'nombre': data['nombre'].strip(),
        'descripcion': data['descripcion'].strip(),
        'categoria': data.get('categoria', 'maderos'),
        'precio': int(data['precio']),
        'moneda': 'CLP',
        'stock_fisico': int(data['stock_fisico']),
        'stock_reservado': 0,
        'imagenes': data['imagenes'],
        'atributos': data.get('atributos', {}),
        'activo': True,
        'version': 1,
        'creado_en': datetime.utcnow(),
        'actualizado_en': datetime.utcnow()
    }