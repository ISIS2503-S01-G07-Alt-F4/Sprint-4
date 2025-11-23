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
