export interface Producto {
    _id: string; // codigo_barras
    tipo: string;
    nombre: string;
    descripcion: string;
    precio: number;
    cantidad_items_disponibles: number;
    atributos?: Record<string, any>;
}

export interface Item {
    _id: string; // sku
    ingreso_fecha: string;
    salida_fecha?: string;
    estado: 'disponible' | 'vendido' | 'devuelto' | 'dañado';
    producto_id: string;
    estanteria_id: string;
    bodega_id: string;
    movimientos_recientes?: any[];
}

export interface Estanteria {
    _id: string; // numero_estanteria
    area_bodega: string;
    capacidad_total: number;
    capacidad_utilizada: number;
}

export interface Bodega {
    _id?: string;
    ciudad: string;
    direccion: string;
    estanterias: Estanteria[];
}

export interface Cliente {
    id: number;
    nombre: string;
    numero_telefono: string;
}

export interface Factura {
    id?: number;
    costo_total: number;
    metodo_pago: string;
    num_cuenta: string;
    comprobante: string;
    cliente?: number;
}

export interface ProductoSolicitado {
    producto: string; // ID del producto
    cantidad: number;
}

export interface Pedido {
    id?: number;
    estado: string;
    items?: string[]; // SKUs de items
    factura?: Factura;
    cliente?: number;
    operario: string;
    hash_de_integridad?: string;
    productos_solicitados?: ProductoSolicitado[];
}
