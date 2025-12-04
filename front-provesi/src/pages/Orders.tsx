import React, { useEffect, useState } from 'react';
import { getPedidos, createPedido, cambiarEstadoPedido } from '../services/orderService';
import { getProductos, getBodegas } from '../services/inventoryService';
import type { Pedido, Producto, Bodega } from '../types';

const Orders: React.FC = () => {
    const [pedidos, setPedidos] = useState<Pedido[]>([]);
    const [productos, setProductos] = useState<Producto[]>([]);
    const [bodegas, setBodegas] = useState<Bodega[]>([]);
    const [loading, setLoading] = useState(true);
    
    // Form State for Creating Order
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newPedido, setNewPedido] = useState({
        bodega_seleccionada: '',
        cliente: 0,
        operario: '',
        items: [] as string[],
        productos_solicitados: [] as Array<{ producto: string; cantidad: number }>
    });

    // Form State for Changing Status
    const [showStatusForm, setShowStatusForm] = useState(false);
    const [selectedPedidoId, setSelectedPedidoId] = useState<number | null>(null);
    const [statusChange, setStatusChange] = useState({
        nuevo_estado: '',
        metodo_pago: '',
        num_cuenta: '',
        comprobante: ''
    });

    // Product selection state
    const [selectedProductos, setSelectedProductos] = useState<Array<{ producto: string; cantidad: number }>>([]);
    const [currentProducto, setCurrentProducto] = useState('');
    const [currentCantidad, setCurrentCantidad] = useState(1);

    // Filter State
    const [filterEstado, setFilterEstado] = useState('');
    const [filterOperario, setFilterOperario] = useState('');

    const estadosPedido = [
        'Transito', 'Alistamiento', 'Por verificar', 'Rechazado x verificar',
        'Verificado', 'Empacado x despachar', 'Despachado', 'Despachado x facturar',
        'Entregado', 'Devuelto', 'Produccion', 'Bordado', 'Dropshipping', 'Compra', 'Anulado'
    ];

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [pedidosData, productosData, bodegasData] = await Promise.all([
                getPedidos(),
                getProductos(),
                getBodegas()
            ]);
            setPedidos(pedidosData);
            setProductos(productosData);
            setBodegas(bodegasData);
        } catch (error) {
            console.error("Error loading data", error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (estado: string) => {
        const colors: Record<string, string> = {
            'Transito': 'bg-blue-100 text-blue-800',
            'Alistamiento': 'bg-yellow-100 text-yellow-800',
            'Por verificar': 'bg-orange-100 text-orange-800',
            'Rechazado x verificar': 'bg-red-100 text-red-800',
            'Verificado': 'bg-green-100 text-green-800',
            'Empacado x despachar': 'bg-purple-100 text-purple-800',
            'Despachado': 'bg-indigo-100 text-indigo-800',
            'Despachado x facturar': 'bg-pink-100 text-pink-800',
            'Entregado': 'bg-teal-100 text-teal-800',
            'Devuelto': 'bg-gray-100 text-gray-800',
            'Produccion': 'bg-cyan-100 text-cyan-800',
            'Bordado': 'bg-lime-100 text-lime-800',
            'Dropshipping': 'bg-amber-100 text-amber-800',
            'Compra': 'bg-emerald-100 text-emerald-800',
            'Anulado': 'bg-slate-100 text-slate-800'
        };
        return colors[estado] || 'bg-gray-100 text-gray-800';
    };

    const addProductoToSelection = () => {
        if (currentProducto && currentCantidad > 0) {
            setSelectedProductos([...selectedProductos, {
                producto: currentProducto,
                cantidad: currentCantidad
            }]);
            setCurrentProducto('');
            setCurrentCantidad(1);
        }
    };

    const removeProductoFromSelection = (index: number) => {
        setSelectedProductos(selectedProductos.filter((_, i) => i !== index));
    };

    const handleCreatePedido = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createPedido({
                ...newPedido,
                productos_solicitados: selectedProductos
            });
            
            // Reset form
            setNewPedido({
                bodega_seleccionada: '',
                cliente: 0,
                operario: '',
                items: [],
                productos_solicitados: []
            });
            setSelectedProductos([]);
            setShowCreateForm(false);
            loadData();
            alert("Pedido creado exitosamente");
        } catch (error) {
            console.error("Error creating order", error);
            alert("Error al crear pedido. Verifique los datos y credenciales.");
        }
    };

    const handleStatusChange = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedPedidoId) return;

        try {
            const datos_factura = statusChange.nuevo_estado === 'Empacado x despachar' ? {
                metodo_pago: statusChange.metodo_pago,
                num_cuenta: statusChange.num_cuenta,
                comprobante: statusChange.comprobante
            } : undefined;

            await cambiarEstadoPedido(selectedPedidoId, {
                nuevo_estado: statusChange.nuevo_estado,
                pedido_id: selectedPedidoId,
                datos_factura
            });

            // Reset form
            setStatusChange({
                nuevo_estado: '',
                metodo_pago: '',
                num_cuenta: '',
                comprobante: ''
            });
            setSelectedPedidoId(null);
            setShowStatusForm(false);
            loadData();
            alert("Estado del pedido actualizado exitosamente");
        } catch (error) {
            console.error("Error updating order status", error);
            alert("Error al cambiar estado del pedido. Verifique los datos y credenciales.");
        }
    };

    const openStatusChangeForm = (pedidoId: number) => {
        setSelectedPedidoId(pedidoId);
        setShowStatusForm(true);
    };

    const filteredPedidos = pedidos.filter(pedido => {
        let match = true;
        if (filterEstado && pedido.estado !== filterEstado) match = false;
        if (filterOperario && !pedido.operario.toLowerCase().includes(filterOperario.toLowerCase())) match = false;
        return match;
    });

    if (loading) {
        return <div className="flex justify-center items-center h-64">Cargando...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="sm:flex sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Pedidos</h1>
                    <p className="mt-2 text-sm text-gray-700">
                        Gestiona todos los pedidos del sistema
                    </p>
                </div>
                <div className="mt-4 sm:mt-0">
                    <button
                        onClick={() => setShowCreateForm(!showCreateForm)}
                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                        {showCreateForm ? 'Cancelar' : 'Crear Pedido'}
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white shadow rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Filtros</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Estado</label>
                        <select
                            value={filterEstado}
                            onChange={(e) => setFilterEstado(e.target.value)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                        >
                            <option value="">Todos los estados</option>
                            {estadosPedido.map(estado => (
                                <option key={estado} value={estado}>{estado}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Operario</label>
                        <input
                            type="text"
                            value={filterOperario}
                            onChange={(e) => setFilterOperario(e.target.value)}
                            placeholder="Buscar por operario..."
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                        />
                    </div>
                    <div className="flex items-end">
                        <button
                            onClick={() => {
                                setFilterEstado('');
                                setFilterOperario('');
                            }}
                            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                        >
                            Limpiar Filtros
                        </button>
                    </div>
                </div>
            </div>

            {/* Create Form */}
            {showCreateForm && (
                <div className="bg-white shadow rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Crear Nuevo Pedido</h2>
                    <form onSubmit={handleCreatePedido} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Bodega *</label>
                                <select
                                    required
                                    value={newPedido.bodega_seleccionada}
                                    onChange={(e) => setNewPedido({...newPedido, bodega_seleccionada: e.target.value})}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                >
                                    <option value="">Seleccione una bodega</option>
                                    {bodegas.map(bodega => (
                                        <option key={bodega._id} value={bodega._id}>
                                            {bodega.ciudad} - {bodega.direccion}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Cliente ID *</label>
                                <input
                                    type="number"
                                    required
                                    value={newPedido.cliente || ''}
                                    onChange={(e) => setNewPedido({...newPedido, cliente: parseInt(e.target.value)})}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Operario *</label>
                                <input
                                    type="text"
                                    required
                                    value={newPedido.operario}
                                    onChange={(e) => setNewPedido({...newPedido, operario: e.target.value})}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Items (SKUs) - separados por coma *</label>
                                <input
                                    type="text"
                                    required
                                    placeholder="SKU1, SKU2, SKU3"
                                    value={newPedido.items.join(', ')}
                                    onChange={(e) => setNewPedido({...newPedido, items: e.target.value.split(',').map(s => s.trim())})}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                />
                            </div>
                        </div>

                        <div className="border-t pt-4">
                            <h3 className="text-lg font-medium mb-3">Productos Solicitados</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                                <div className="md:col-span-1">
                                    <label className="block text-sm font-medium text-gray-700">Producto</label>
                                    <select
                                        value={currentProducto}
                                        onChange={(e) => setCurrentProducto(e.target.value)}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                    >
                                        <option value="">Seleccione producto</option>
                                        {productos.map(producto => (
                                            <option key={producto._id} value={producto._id}>
                                                {producto.nombre} ({producto._id})
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Cantidad</label>
                                    <input
                                        type="number"
                                        min="1"
                                        value={currentCantidad}
                                        onChange={(e) => setCurrentCantidad(parseInt(e.target.value))}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                    />
                                </div>
                                <div className="flex items-end">
                                    <button
                                        type="button"
                                        onClick={addProductoToSelection}
                                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                                    >
                                        Agregar Producto
                                    </button>
                                </div>
                            </div>

                            {selectedProductos.length > 0 && (
                                <div className="mt-4">
                                    <h4 className="text-sm font-medium text-gray-700 mb-2">Productos Agregados:</h4>
                                    <ul className="space-y-2">
                                        {selectedProductos.map((item, index) => {
                                            const producto = productos.find(p => p._id === item.producto);
                                            return (
                                                <li key={index} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                                                    <span>
                                                        {producto?.nombre || item.producto} - Cantidad: {item.cantidad}
                                                    </span>
                                                    <button
                                                        type="button"
                                                        onClick={() => removeProductoFromSelection(index)}
                                                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                                                    >
                                                        Eliminar
                                                    </button>
                                                </li>
                                            );
                                        })}
                                    </ul>
                                </div>
                            )}
                        </div>

                        <div className="flex justify-end space-x-3 pt-4 border-t">
                            <button
                                type="button"
                                onClick={() => {
                                    setShowCreateForm(false);
                                    setSelectedProductos([]);
                                }}
                                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                            >
                                Crear Pedido
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Status Change Form */}
            {showStatusForm && (
                <div className="bg-white shadow rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Cambiar Estado del Pedido #{selectedPedidoId}</h2>
                    <form onSubmit={handleStatusChange} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700">Nuevo Estado *</label>
                                <select
                                    required
                                    value={statusChange.nuevo_estado}
                                    onChange={(e) => setStatusChange({...statusChange, nuevo_estado: e.target.value})}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                >
                                    <option value="">Seleccione un estado</option>
                                    {estadosPedido.map(estado => (
                                        <option key={estado} value={estado}>{estado}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {statusChange.nuevo_estado === 'Empacado x despachar' && (
                            <div className="border-t pt-4">
                                <h3 className="text-lg font-medium mb-3">Datos de Factura</h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Método de Pago *</label>
                                        <input
                                            type="text"
                                            required
                                            value={statusChange.metodo_pago}
                                            onChange={(e) => setStatusChange({...statusChange, metodo_pago: e.target.value})}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Número de Cuenta *</label>
                                        <input
                                            type="text"
                                            required
                                            value={statusChange.num_cuenta}
                                            onChange={(e) => setStatusChange({...statusChange, num_cuenta: e.target.value})}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Comprobante *</label>
                                        <input
                                            type="text"
                                            required
                                            value={statusChange.comprobante}
                                            onChange={(e) => setStatusChange({...statusChange, comprobante: e.target.value})}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                                        />
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="flex justify-end space-x-3 pt-4 border-t">
                            <button
                                type="button"
                                onClick={() => {
                                    setShowStatusForm(false);
                                    setSelectedPedidoId(null);
                                }}
                                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                            >
                                Cambiar Estado
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Orders Table */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                        Lista de Pedidos ({filteredPedidos.length})
                    </h3>
                </div>
                <div className="border-t border-gray-200">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Operario</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Items</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {filteredPedidos.map((pedido) => (
                                    <tr key={pedido.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            #{pedido.id}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(pedido.estado)}`}>
                                                {pedido.estado}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {pedido.operario || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            Cliente #{pedido.cliente || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {pedido.items?.length || 0} items
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <button
                                                onClick={() => pedido.id && openStatusChangeForm(pedido.id)}
                                                className="text-primary-600 hover:text-primary-900 mr-4"
                                            >
                                                Cambiar Estado
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {filteredPedidos.length === 0 && (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500">
                                            No hay pedidos disponibles
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Orders;
