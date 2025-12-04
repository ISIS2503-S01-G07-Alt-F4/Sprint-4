import api from './api';
import type { Pedido } from '../types';

// Obtener todos los pedidos
export const getPedidos = async () => {
  const response = await api.get<Pedido[]>('/pedidos/');
  return response.data;
};

// Obtener un pedido específico
export const getPedido = async (id: number) => {
  const response = await api.get<Pedido>(`/pedidos/${id}`);
  return response.data;
};

// Crear un nuevo pedido
export const createPedido = async (pedidoData: {
  username: string;
  password: string;
  bodega_seleccionada: string;
  cliente: number;
  operario: string;
  items: string[];
  productos_solicitados: Array<{ producto: string; cantidad: number }>;
}) => {
  const response = await api.post('/pedidos/', pedidoData);
  return response.data;
};

// Cambiar el estado de un pedido
export const cambiarEstadoPedido = async (
  id: number,
  estadoData: {
    username: string;
    password: string;
    nuevo_estado: string;
    pedido_id: number;
    datos_factura?: {
      metodo_pago: string;
      num_cuenta: string;
      comprobante: string;
    };
  }
) => {
  const response = await api.put(`/pedidos/${id}`, estadoData);
  return response.data;
};

// Verificar integridad de un pedido
export const verificarIntegridad = async (pedidoId: number) => {
  const response = await api.get(`/pedidos/${pedidoId}/verificar-integridad`);
  return response.data;
};
