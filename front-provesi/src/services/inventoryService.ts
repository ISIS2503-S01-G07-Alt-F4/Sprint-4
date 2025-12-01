import api from './api';
import type { Producto, Item, Bodega, Estanteria } from '../types';

// Productos
export const getProductos = async () => {
  const response = await api.get<Producto[]>('/productos/');
  return response.data;
};

export const createProducto = async (producto: Producto) => {
  const response = await api.post('/productos/', producto);
  return response.data;
};

export const updateProducto = async (id: string, producto: Producto) => {
    const response = await api.put(`/productos/${id}`, producto);
    return response.data;
};

export const deleteProducto = async (id: string) => {
    const response = await api.delete(`/productos/${id}`);
    return response.data;
};

// Bodegas
export const getBodegas = async () => {
  const response = await api.get<Bodega[]>('/bodegas/');
  return response.data;
};

export const createBodega = async (bodega: Bodega) => {
  const response = await api.post('/bodegas/', bodega);
  return response.data;
};

export const deleteBodega = async (id: string) => {
    const response = await api.delete(`/bodegas/${id}`);
    return response.data;
};

// Items
export const getItems = async () => {
    const response = await api.get<Item[]>('/items/');
    return response.data;
};

export const createItem = async (item: Item) => {
    const response = await api.post('/items/', item);
    return response.data;
};

export const deleteItem = async (id: string) => {
    const response = await api.delete(`/items/${id}`);
    return response.data;
};

export const getItemsByProductoAndBodega = async (productoId: string, bodegaId: string) => {
    const response = await api.get<{items: Item[]}>(`/items/productoBodega`, {
        params: { codigo_barras: productoId, bodega_id: bodegaId }
    });
    return response.data.items;
};

export const getItemsByEstanteria = async (bodegaId: string, estanteriaId: string) => {
    const response = await api.get<{items: Item[]}>(`/items/estanteria/todos`, {
        params: { bodega_id: bodegaId, numero_estanteria: estanteriaId }
    });
    return response.data.items;
};

// Estanterias
export const getEstanterias = async () => {
    const response = await api.get<Estanteria[]>('/estanterias/');
    return response.data;
};

export const getEstanteriasByBodega = async (bodegaId: string) => {
    const response = await api.get<Estanteria[]>(`/estanterias/${bodegaId}`);
    return response.data;
};

export const createEstanteria = async (bodegaId: string, estanteria: Estanteria) => {
    const response = await api.post(`/estanterias/${bodegaId}`, estanteria);
    return response.data;
};

export const deleteEstanteria = async (bodegaId: string, estanteriaId: string) => {
    const response = await api.delete(`/estanterias/${bodegaId}/${estanteriaId}`);
    return response.data;
};
