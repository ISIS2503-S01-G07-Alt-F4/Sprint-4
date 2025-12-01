import React, { useEffect, useState } from 'react';
import { getProductos, createProducto, deleteProducto } from '../services/inventoryService';
import type { Producto } from '../types';

const Products: React.FC = () => {
    const [productos, setProductos] = useState<Producto[]>([]);
    const [loading, setLoading] = useState(true);
    const [newProducto, setNewProducto] = useState<Partial<Producto>>({
        _id: '',
        nombre: '',
        tipo: '',
        descripcion: '',
        precio: 0,
        cantidad_items_disponibles: 0,
        atributos: {}
    });

    // State for managing dynamic attributes
    const [attributeKey, setAttributeKey] = useState('');
    const [attributeValue, setAttributeValue] = useState('');

    useEffect(() => {
        loadProductos();
    }, []);

    const loadProductos = async () => {
        try {
            const data = await getProductos();
            if (Array.isArray(data)) {
                setProductos(data);
            } else {
                console.error("Data received is not an array:", data);
                setProductos([]);
            }
        } catch (error) {
            console.error("Error loading products", error);
            setProductos([]);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createProducto(newProducto as Producto);
            setNewProducto({ _id: '', nombre: '', tipo: '', descripcion: '', precio: 0, cantidad_items_disponibles: 0, atributos: {} });
            setAttributeKey('');
            setAttributeValue('');
            loadProductos();
        } catch (error) {
            console.error("Error creating product", error);
            alert("Error al crear producto. Verifique que el código de barras no exista.");
        }
    };

    const handleDelete = async (id: string) => {
        if (globalThis.confirm("¿Estás seguro de eliminar este producto?")) {
            try {
                await deleteProducto(id);
                loadProductos();
            } catch (error) {
                console.error("Error deleting product", error);
            }
        }
    };

    const addAttribute = () => {
        if (attributeKey && attributeValue) {
            setNewProducto({
                ...newProducto,
                atributos: {
                    ...newProducto.atributos,
                    [attributeKey]: attributeValue
                }
            });
            setAttributeKey('');
            setAttributeValue('');
        }
    };

    const removeAttribute = (key: string) => {
        const newAtributos = { ...newProducto.atributos };
        delete newAtributos[key];
        setNewProducto({ ...newProducto, atributos: newAtributos });
    };

    return (
        <div>
            <div className="md:flex md:items-center md:justify-between mb-8">
                <div className="min-w-0 flex-1">
                    <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                        Productos
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">Gestiona el catálogo de productos disponibles.</p>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-card border border-gray-200 mb-8 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Registrar Nuevo Producto</h3>
                </div>
                <div className="p-6">
                    <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="col-span-1">
                            <label htmlFor="prod-id" className="block text-sm font-medium text-gray-700 mb-1">Código de Barras</label>
                            <input 
                                id="prod-id"
                                type="text" 
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newProducto._id}
                                onChange={e => setNewProducto({...newProducto, _id: e.target.value})}
                                required
                                placeholder="E.g. 123456789"
                            />
                        </div>
                        <div className="col-span-1">
                            <label htmlFor="prod-nombre" className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                            <input 
                                id="prod-nombre"
                                type="text" 
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newProducto.nombre}
                                onChange={e => setNewProducto({...newProducto, nombre: e.target.value})}
                                required
                                placeholder="Nombre del producto"
                            />
                        </div>
                        <div className="col-span-1">
                            <label htmlFor="prod-tipo" className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                            <input 
                                id="prod-tipo"
                                type="text" 
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newProducto.tipo}
                                onChange={e => setNewProducto({...newProducto, tipo: e.target.value})}
                                required
                                placeholder="Categoría"
                            />
                        </div>
                        <div className="col-span-1">
                            <label htmlFor="prod-precio" className="block text-sm font-medium text-gray-700 mb-1">Precio</label>
                            <div className="relative mt-1 rounded-md shadow-sm">
                                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                    <span className="text-gray-500 sm:text-sm">$</span>
                                </div>
                                <input 
                                    id="prod-precio"
                                    type="number" 
                                    className="block w-full rounded-md border-gray-300 pl-7 focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                    value={newProducto.precio}
                                    onChange={e => setNewProducto({...newProducto, precio: Number.parseFloat(e.target.value)})}
                                    required
                                    placeholder="0.00"
                                />
                            </div>
                        </div>
                        <div className="col-span-1 md:col-span-2">
                            <label htmlFor="prod-desc" className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                            <textarea 
                                id="prod-desc"
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                rows={3}
                                value={newProducto.descripcion}
                                onChange={e => setNewProducto({...newProducto, descripcion: e.target.value})}
                                required
                                placeholder="Detalles del producto..."
                            />
                        </div>

                        {/* Attributes Section */}
                        <div className="col-span-1 md:col-span-2 border-t border-gray-200 pt-4 mt-2">
                            <span className="block text-sm font-medium text-gray-700 mb-2">Atributos Adicionales</span>
                            <div className="flex gap-2 mb-3">
                                <input 
                                    type="text" 
                                    placeholder="Clave (ej. Color)" 
                                    className="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                    value={attributeKey}
                                    onChange={e => setAttributeKey(e.target.value)}
                                />
                                <input 
                                    type="text" 
                                    placeholder="Valor (ej. Rojo)" 
                                    className="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                    value={attributeValue}
                                    onChange={e => setAttributeValue(e.target.value)}
                                />
                                <button 
                                    type="button"
                                    onClick={addAttribute}
                                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none"
                                >
                                    Agregar
                                </button>
                            </div>
                            
                            {/* List of added attributes */}
                            {newProducto.atributos && Object.keys(newProducto.atributos).length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                    {Object.entries(newProducto.atributos).map(([key, value]) => (
                                        <span key={key} className="inline-flex items-center rounded-full bg-gray-100 px-3 py-0.5 text-sm font-medium text-gray-800">
                                            {key}: {value as string}
                                            <button 
                                                type="button" 
                                                onClick={() => removeAttribute(key)}
                                                className="ml-1.5 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-gray-400 hover:bg-gray-200 hover:text-gray-500 focus:bg-gray-500 focus:text-white focus:outline-none"
                                            >
                                                <span className="sr-only">Remove attribute {key}</span>
                                                <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                                                    <path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" />
                                                </svg>
                                            </button>
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="col-span-1 md:col-span-2 flex justify-end">
                            <button type="submit" className="inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                                Crear Producto
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div className="mb-6">
                <div className="relative mt-1 rounded-md shadow-sm">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        name="search"
                        id="search"
                        className="block w-full rounded-md border-gray-300 pl-10 focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-3 border"
                        placeholder="Buscar productos..."
                    />
                </div>
            </div>

            {loading ? <div className="text-center py-10 text-gray-500">Cargando productos...</div> : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {productos.map(producto => (
                        <div key={producto._id} className="bg-white rounded-lg shadow-card hover:shadow-card-hover transition-shadow duration-200 border border-gray-200 overflow-hidden flex flex-col">
                            <div className="p-5 flex-grow">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900">{producto.nombre}</h3>
                                        <p className="text-xs text-gray-500 uppercase tracking-wide mt-1">{producto.tipo}</p>
                                    </div>
                                    <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                                        {producto.cantidad_items_disponibles} Stock
                                    </span>
                                </div>
                                <p className="mt-3 text-sm text-gray-600 line-clamp-2">{producto.descripcion}</p>
                                
                                {/* Display Attributes */}
                                {producto.atributos && Object.keys(producto.atributos).length > 0 && (
                                    <div className="mt-3 flex flex-wrap gap-1">
                                        {Object.entries(producto.atributos).slice(0, 3).map(([key, value]) => (
                                            <span key={key} className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                                                {key}: {value as string}
                                            </span>
                                        ))}
                                        {Object.keys(producto.atributos).length > 3 && (
                                            <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600">
                                                +{Object.keys(producto.atributos).length - 3}
                                            </span>
                                        )}
                                    </div>
                                )}

                                <div className="mt-4 flex items-baseline">
                                    <span className="text-2xl font-bold tracking-tight text-gray-900">${producto.precio}</span>
                                </div>
                                <div className="mt-2 text-xs text-gray-400">SKU: {producto._id}</div>
                            </div>
                            <div className="bg-gray-50 px-5 py-3 border-t border-gray-200 flex justify-end">
                                <button 
                                    onClick={() => handleDelete(producto._id)}
                                    className="text-sm font-medium text-red-600 hover:text-red-500"
                                >
                                    Eliminar
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Products;
