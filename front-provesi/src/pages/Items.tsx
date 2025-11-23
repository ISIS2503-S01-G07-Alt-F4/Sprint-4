import React, { useEffect, useState } from 'react';
import { 
    getItems, createItem, deleteItem, getProductos, getBodegas, 
    getEstanteriasByBodega, getItemsByProductoAndBodega, getItemsByEstanteria 
} from '../services/inventoryService';
import type { Item, Producto, Bodega, Estanteria } from '../types';

const Items: React.FC = () => {
    const [items, setItems] = useState<Item[]>([]);
    const [productos, setProductos] = useState<Producto[]>([]);
    const [bodegas, setBodegas] = useState<Bodega[]>([]);
    const [loading, setLoading] = useState(true);
    
    // Form State
    const [newItem, setNewItem] = useState<Partial<Item>>({
        _id: '',
        estado: 'disponible',
        producto_id: '',
        bodega_id: '',
        estanteria_id: ''
    });
    const [formShelves, setFormShelves] = useState<Estanteria[]>([]);

    // Filter State
    const [filterBodega, setFilterBodega] = useState('');
    const [filterProducto, setFilterProducto] = useState('');
    const [filterEstanteria, setFilterEstanteria] = useState('');
    const [filterShelves, setFilterShelves] = useState<Estanteria[]>([]);

    // Modal State
    const [selectedItemDetails, setSelectedItemDetails] = useState<{item: Item, producto: Producto} | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    // Load shelves for filter when filterBodega changes
    useEffect(() => {
        if (filterBodega) {
            getEstanteriasByBodega(filterBodega).then(setFilterShelves).catch(console.error);
        } else {
            setFilterShelves([]);
            setFilterEstanteria('');
        }
    }, [filterBodega]);

    const loadData = async () => {
        try {
            const [itemsData, productsData, bodegasData] = await Promise.all([
                getItems(),
                getProductos(),
                getBodegas()
            ]);
            setItems(itemsData);
            setProductos(productsData);
            setBodegas(bodegasData);
        } catch (error) {
            console.error("Error loading data", error);
        } finally {
            setLoading(false);
        }
    };

    const handleFilter = async () => {
        setLoading(true);
        try {
            let data: Item[] = [];
            if (filterBodega && filterProducto) {
                data = await getItemsByProductoAndBodega(filterProducto, filterBodega);
            } else if (filterBodega && filterEstanteria) {
                data = await getItemsByEstanteria(filterBodega, filterEstanteria);
            } else {
                // Fallback to client-side filtering if API doesn't support partial combos or just reload all
                const allItems = await getItems();
                data = allItems.filter(item => {
                    let match = true;
                    if (filterBodega && item.bodega_id !== filterBodega) match = false;
                    if (filterProducto && item.producto_id !== filterProducto) match = false;
                    if (filterEstanteria && item.estanteria_id !== filterEstanteria) match = false;
                    return match;
                });
            }
            setItems(data);
        } catch (error) {
            console.error("Error filtering items", error);
        } finally {
            setLoading(false);
        }
    };

    const clearFilters = () => {
        setFilterBodega('');
        setFilterProducto('');
        setFilterEstanteria('');
        loadData();
    };

    const handleBodegaChange = async (bodegaId: string) => {
        setNewItem({...newItem, bodega_id: bodegaId, estanteria_id: ''});
        if (bodegaId) {
            try {
                const shelves = await getEstanteriasByBodega(bodegaId);
                setFormShelves(shelves);
            } catch (error) {
                console.error("Error loading shelves", error);
                setFormShelves([]);
            }
        } else {
            setFormShelves([]);
        }
    };

    const getStatusColor = (estado: string) => {
        switch (estado) {
            case 'disponible': return 'bg-green-100 text-green-800';
            case 'vendido': return 'bg-blue-100 text-blue-800';
            case 'dañado': return 'bg-red-100 text-red-800';
            case 'devuelto': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createItem(newItem as Item);
            setNewItem({ _id: '', estado: 'disponible', producto_id: '', bodega_id: '', estanteria_id: '' });
            setFormShelves([]);
            loadData(); 
            alert("Item creado exitosamente");
        } catch (error) {
            console.error("Error creating item", error);
            alert("Error al crear item. Verifique los datos.");
        }
    };

    const handleDelete = async (id: string) => {
        if (globalThis.confirm("¿Estás seguro de eliminar este item?")) {
            try {
                await deleteItem(id);
                loadData();
            } catch (error) {
                console.error("Error deleting item", error);
            }
        }
    };

    const openDetails = (item: Item) => {
        const prod = productos.find(p => p._id === item.producto_id);
        if (prod) {
            setSelectedItemDetails({ item, producto: prod });
        }
    };

    return (
        <div>
            <div className="md:flex md:items-center md:justify-between mb-8">
                <div className="min-w-0 flex-1">
                    <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                        Items (Inventario Físico)
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">Gestión individual de items en inventario.</p>
                </div>
            </div>
            
            {/* Create Item Form */}
            <div className="bg-white rounded-lg shadow-card border border-gray-200 mb-8 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Registrar Nuevo Item</h3>
                </div>
                <div className="p-6">
                    <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="col-span-1">
                            <label htmlFor="item-sku" className="block text-sm font-medium text-gray-700 mb-1">SKU / ID</label>
                            <input 
                                id="item-sku"
                                type="text" 
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newItem._id}
                                onChange={e => setNewItem({...newItem, _id: e.target.value})}
                                required
                                placeholder="Identificador único"
                            />
                        </div>
                        
                        <div className="col-span-1">
                            <label htmlFor="item-producto" className="block text-sm font-medium text-gray-700 mb-1">Producto</label>
                            <select 
                                id="item-producto"
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newItem.producto_id}
                                onChange={e => setNewItem({...newItem, producto_id: e.target.value})}
                                required
                            >
                                <option value="">Seleccionar Producto</option>
                                {productos.map(p => (
                                    <option key={p._id} value={p._id}>{p.nombre} ({p._id})</option>
                                ))}
                            </select>
                        </div>

                        <div className="col-span-1">
                            <label htmlFor="item-bodega" className="block text-sm font-medium text-gray-700 mb-1">Bodega</label>
                            <select 
                                id="item-bodega"
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newItem.bodega_id}
                                onChange={e => handleBodegaChange(e.target.value)}
                                required
                            >
                                <option value="">Seleccionar Bodega</option>
                                {bodegas.map(b => (
                                    <option key={b._id} value={b._id}>{b.ciudad} - {b.direccion}</option>
                                ))}
                            </select>
                        </div>

                        <div className="col-span-1">
                            <label htmlFor="item-estanteria" className="block text-sm font-medium text-gray-700 mb-1">Estantería</label>
                            <select 
                                id="item-estanteria"
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newItem.estanteria_id}
                                onChange={e => setNewItem({...newItem, estanteria_id: e.target.value})}
                                required
                                disabled={!newItem.bodega_id}
                            >
                                <option value="">Seleccionar Estantería</option>
                                {formShelves.map(est => (
                                    <option key={est._id} value={est._id}>
                                        {est.area_bodega} (Cap: {est.capacidad_utilizada}/{est.capacidad_total})
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="col-span-1">
                            <label htmlFor="item-estado" className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                            <select 
                                id="item-estado"
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newItem.estado}
                                onChange={e => setNewItem({...newItem, estado: e.target.value as any})}
                                required
                            >
                                <option value="disponible">Disponible</option>
                                <option value="vendido">Vendido</option>
                                <option value="dañado">Dañado</option>
                                <option value="devuelto">Devuelto</option>
                            </select>
                        </div>

                        <div className="col-span-1 md:col-span-2 flex justify-end">
                            <button type="submit" className="inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors">
                                Registrar Item
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Filtrar Items</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <div>
                        <label htmlFor="filter-bodega" className="block text-xs font-medium text-gray-500 mb-1">Bodega</label>
                        <select 
                            id="filter-bodega"
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                            value={filterBodega}
                            onChange={e => setFilterBodega(e.target.value)}
                        >
                            <option value="">Todas</option>
                            {bodegas.map(b => (
                                <option key={b._id} value={b._id}>{b.ciudad}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label htmlFor="filter-estanteria" className="block text-xs font-medium text-gray-500 mb-1">Estantería</label>
                        <select 
                            id="filter-estanteria"
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                            value={filterEstanteria}
                            onChange={e => setFilterEstanteria(e.target.value)}
                            disabled={!filterBodega}
                        >
                            <option value="">Todas</option>
                            {filterShelves.map(est => (
                                <option key={est._id} value={est._id}>{est.area_bodega} ({est._id})</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label htmlFor="filter-producto" className="block text-xs font-medium text-gray-500 mb-1">Producto</label>
                        <select 
                            id="filter-producto"
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                            value={filterProducto}
                            onChange={e => setFilterProducto(e.target.value)}
                        >
                            <option value="">Todos</option>
                            {productos.map(p => (
                                <option key={p._id} value={p._id}>{p.nombre}</option>
                            ))}
                        </select>
                    </div>
                    <div className="flex gap-2">
                        <button 
                            onClick={handleFilter}
                            className="flex-1 inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none"
                        >
                            Filtrar
                        </button>
                        <button 
                            onClick={clearFilters}
                            className="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none"
                        >
                            Limpiar
                        </button>
                    </div>
                </div>
            </div>

            {loading ? <div className="text-center py-10 text-gray-500">Cargando items...</div> : (
                <div className="bg-white shadow-card rounded-lg border border-gray-200 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ubicación</th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {items.map(item => {
                                    const prod = productos.find(p => p._id === item.producto_id);
                                    const bod = bodegas.find(b => b._id === item.bodega_id);
                                    return (
                                        <tr key={item._id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item._id}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                <div className="flex items-center">
                                                    <span>{prod?.nombre || item.producto_id}</span>
                                                    <button 
                                                        onClick={() => openDetails(item)}
                                                        className="ml-2 text-primary-600 hover:text-primary-800 text-xs underline"
                                                    >
                                                        Ver Detalles
                                                    </button>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                                                getStatusColor(item.estado)
                                            }`}>
                                                    {item.estado}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {bod?.ciudad} <span className="text-gray-400">/</span> {item.estanteria_id}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button 
                                                    onClick={() => handleDelete(item._id)}
                                                    className="text-red-600 hover:text-red-900"
                                                >
                                                    Eliminar
                                                </button>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Details Modal */}
            {selectedItemDetails && (
                <div className="fixed inset-0 z-10 overflow-y-auto" aria-labelledby="modal-title">
                    <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={() => setSelectedItemDetails(null)}></div>
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                <div className="sm:flex sm:items-start">
                                    <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                                        <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                            Detalles del Producto
                                        </h3>
                                        <div className="mt-2">
                                            <p className="text-sm text-gray-500 mb-4">
                                                Información del producto asociado al Item <strong>{selectedItemDetails.item._id}</strong>
                                            </p>
                                            <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
                                                <p className="text-sm font-semibold text-gray-900">{selectedItemDetails.producto.nombre}</p>
                                                <p className="text-xs text-gray-500 mb-2">{selectedItemDetails.producto.tipo}</p>
                                                <p className="text-sm text-gray-700 mb-3">{selectedItemDetails.producto.descripcion}</p>
                                                
                                                {selectedItemDetails.producto.atributos && Object.keys(selectedItemDetails.producto.atributos).length > 0 && (
                                                    <div className="border-t border-gray-200 pt-2 mt-2">
                                                        <p className="text-xs font-bold text-gray-500 uppercase mb-2">Atributos</p>
                                                        <div className="grid grid-cols-2 gap-2">
                                                            {Object.entries(selectedItemDetails.producto.atributos).map(([key, value]) => (
                                                                <div key={key} className="text-xs">
                                                                    <span className="font-medium text-gray-600">{key}:</span> {value as string}
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                                <button 
                                    type="button" 
                                    className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                                    onClick={() => setSelectedItemDetails(null)}
                                >
                                    Cerrar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Items;
