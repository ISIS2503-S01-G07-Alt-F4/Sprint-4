import React, { useEffect, useState } from 'react';
import { getBodegas, createBodega, deleteBodega, createEstanteria, deleteEstanteria } from '../services/inventoryService';
import type { Bodega, Estanteria } from '../types';

const Warehouses: React.FC = () => {
    const [bodegas, setBodegas] = useState<Bodega[]>([]);
    const [loading, setLoading] = useState(true);
    const [newBodega, setNewBodega] = useState<Partial<Bodega>>({
        ciudad: '',
        direccion: ''
    });
    
    // State for managing shelves
    const [selectedBodegaId, setSelectedBodegaId] = useState<string | null>(null);
    const [newEstanteria, setNewEstanteria] = useState<Partial<Estanteria>>({
        _id: '',
        area_bodega: '',
        capacidad_total: 0,
        capacidad_utilizada: 0
    });

    useEffect(() => {
        loadBodegas();
    }, []);

    const loadBodegas = async () => {
        try {
            const data = await getBodegas();
            setBodegas(data);
        } catch (error) {
            console.error("Error loading bodegas", error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createBodega(newBodega as Bodega);
            setNewBodega({ ciudad: '', direccion: '' });
            loadBodegas();
        } catch (error) {
            console.error("Error creating bodega", error);
        }
    };

    const handleDelete = async (id: string) => {
        if (globalThis.confirm("¿Estás seguro de eliminar esta bodega?")) {
            try {
                await deleteBodega(id);
                loadBodegas();
            } catch (error) {
                console.error("Error deleting bodega", error);
            }
        }
    };

    const handleCreateEstanteria = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedBodegaId) return;

        try {
            await createEstanteria(selectedBodegaId, newEstanteria as Estanteria);
            setNewEstanteria({ _id: '', area_bodega: '', capacidad_total: 0, capacidad_utilizada: 0 });
            loadBodegas(); // Reload to see new shelf
            alert("Estantería agregada correctamente");
        } catch (error) {
            console.error("Error creating estanteria", error);
            alert("Error al crear estantería");
        }
    };

    const handleDeleteEstanteria = async (bodegaId: string, estanteriaId: string) => {
        if (globalThis.confirm("¿Eliminar esta estantería?")) {
            try {
                await deleteEstanteria(bodegaId, estanteriaId);
                loadBodegas();
            } catch (error) {
                console.error("Error deleting estanteria", error);
            }
        }
    };

    return (
        <div>
            <div className="md:flex md:items-center md:justify-between mb-8">
                <div className="min-w-0 flex-1">
                    <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                        Bodegas
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">Administración de ubicaciones físicas y estanterías.</p>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-card border border-gray-200 mb-8 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Agregar Nueva Bodega</h3>
                </div>
                <div className="p-6">
                    <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="col-span-1">
                            <label htmlFor="bodega-ciudad" className="block text-sm font-medium text-gray-700 mb-1">Ciudad</label>
                            <input 
                                id="bodega-ciudad"
                                type="text" 
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newBodega.ciudad}
                                onChange={e => setNewBodega({...newBodega, ciudad: e.target.value})}
                                required
                                placeholder="Ej. Bogotá"
                            />
                        </div>
                        <div className="col-span-1">
                            <label htmlFor="bodega-direccion" className="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
                            <input 
                                id="bodega-direccion"
                                type="text" 
                                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                                value={newBodega.direccion}
                                onChange={e => setNewBodega({...newBodega, direccion: e.target.value})}
                                required
                                placeholder="Ej. Calle 123 # 45-67"
                            />
                        </div>
                        <div className="col-span-1 md:col-span-2 flex justify-end">
                            <button type="submit" className="inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                                Crear Bodega
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {loading ? <div className="text-center py-10 text-gray-500">Cargando bodegas...</div> : (
                <div className="grid grid-cols-1 gap-6">
                    {bodegas.map(bodega => (
                        <div key={bodega._id} className="bg-white rounded-lg shadow-card border border-gray-200 overflow-hidden">
                            <div className="p-5 border-b border-gray-100">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center">
                                        <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 mr-4">
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3.75h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Z" />
                                            </svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">{bodega.ciudad}</h3>
                                            <p className="text-sm text-gray-500">{bodega.direccion}</p>
                                        </div>
                                    </div>
                                    <div className="flex space-x-2">
                                        <button 
                                            onClick={() => setSelectedBodegaId(selectedBodegaId === bodega._id ? null : bodega._id!)}
                                            className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
                                        >
                                            {selectedBodegaId === bodega._id ? 'Ocultar Estanterías' : 'Ver Estanterías'}
                                        </button>
                                        <button 
                                            onClick={() => handleDelete(bodega._id!)}
                                            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none"
                                        >
                                            Eliminar
                                        </button>
                                    </div>
                                </div>
                            </div>
                            
                            {/* Shelves Section */}
                            {selectedBodegaId === bodega._id && (
                                <div className="bg-gray-50 p-5 border-t border-gray-200">
                                    <h4 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-4">Estanterías en {bodega.ciudad}</h4>
                                    
                                    {/* List of Shelves */}
                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                                        {bodega.estanterias && bodega.estanterias.length > 0 ? (
                                            bodega.estanterias.map(est => (
                                                <div key={est._id} className="bg-white p-4 rounded shadow-sm border border-gray-200 relative group">
                                                    <div className="flex justify-between items-start">
                                                        <div>
                                                            <span className="text-xs font-semibold text-gray-500 uppercase">ID: {est._id}</span>
                                                            <p className="font-medium text-gray-900">{est.area_bodega}</p>
                                                        </div>
                                                        <button 
                                                            onClick={() => handleDeleteEstanteria(bodega._id!, est._id)}
                                                            className="text-gray-400 hover:text-red-500 transition-colors"
                                                            title="Eliminar estantería"
                                                        >
                                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                                                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                            </svg>
                                                        </button>
                                                    </div>
                                                    <div className="mt-2">
                                                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                                                            <span>Capacidad</span>
                                                            <span>{est.capacidad_utilizada} / {est.capacidad_total}</span>
                                                        </div>
                                                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                                                            <div 
                                                                className={`h-1.5 rounded-full ${est.capacidad_utilizada >= est.capacidad_total ? 'bg-red-500' : 'bg-green-500'}`} 
                                                                style={{ width: `${Math.min((est.capacidad_utilizada / est.capacidad_total) * 100, 100)}%` }}
                                                            ></div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="col-span-full text-center py-4 text-sm text-gray-500 italic">
                                                No hay estanterías registradas.
                                            </div>
                                        )}
                                    </div>

                                    {/* Add Shelf Form */}
                                    <div className="bg-white p-4 rounded border border-gray-200">
                                        <h5 className="text-xs font-bold text-gray-700 mb-3">Agregar Nueva Estantería</h5>
                                        <form onSubmit={handleCreateEstanteria} className="flex flex-wrap gap-3 items-end">
                                            <div className="flex-1 min-w-[120px]">
                                                <label htmlFor="est-id" className="block text-xs font-medium text-gray-500 mb-1">ID / Número</label>
                                                <input 
                                                    id="est-id"
                                                    type="text" 
                                                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-xs p-2 border"
                                                    placeholder="E.g. A-01"
                                                    value={newEstanteria._id}
                                                    onChange={e => setNewEstanteria({...newEstanteria, _id: e.target.value})}
                                                    required
                                                />
                                            </div>
                                            <div className="flex-1 min-w-[120px]">
                                                <label htmlFor="est-area" className="block text-xs font-medium text-gray-500 mb-1">Área</label>
                                                <input 
                                                    id="est-area"
                                                    type="text" 
                                                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-xs p-2 border"
                                                    placeholder="E.g. Zona Norte"
                                                    value={newEstanteria.area_bodega}
                                                    onChange={e => setNewEstanteria({...newEstanteria, area_bodega: e.target.value})}
                                                    required
                                                />
                                            </div>
                                            <div className="w-24">
                                                <label htmlFor="est-cap" className="block text-xs font-medium text-gray-500 mb-1">Capacidad</label>
                                                <input 
                                                    id="est-cap"
                                                    type="number" 
                                                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-xs p-2 border"
                                                    placeholder="100"
                                                    value={newEstanteria.capacidad_total || ''}
                                                    onChange={e => setNewEstanteria({...newEstanteria, capacidad_total: Number(e.target.value)})}
                                                    required
                                                />
                                            </div>
                                            <button 
                                                type="submit" 
                                                className="inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-xs font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none"
                                            >
                                                Agregar
                                            </button>
                                        </form>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Warehouses;
