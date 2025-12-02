import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
    return (
        <div>
            <div className="text-center py-12 px-4 sm:px-6 lg:px-8">
                <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-4">
                    Sistema de Inventario <span className="text-primary-600">Provesi</span>
                </h1>
                <p className="mt-4 max-w-2xl text-xl text-gray-500 mx-auto">
                    Gestiona tus productos, bodegas e items de manera eficiente y centralizada.
                </p>
            </div>

            <div className="mt-8 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
                <Link to="/products" className="group relative bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg shadow-card hover:shadow-card-hover transition-all duration-200 border border-gray-200">
                    <div>
                        <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                            </svg>
                        </span>
                    </div>
                    <div className="mt-8">
                        <h3 className="text-lg font-medium">
                            <span className="absolute inset-0" aria-hidden="true"></span>
                            {' '}Productos
                        </h3>
                        <p className="mt-2 text-sm text-gray-500">
                            Administra el catálogo completo de productos, precios y descripciones.
                        </p>
                    </div>
                    <span className="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400" aria-hidden="true">
                        <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0 1 1 0 00-2 0zm-7-8a1 1 0 00-1 1v1zm-1 12a1 1 0 102 0 1 1 0 00-2 0zm-7-8a1 1 0 00-1 1v1zm-1 12a1 1 0 102 0 1 1 0 00-2 0zM4 4h16v2H4V4zm16 12V4h2v12h-2zm-8-8v8h2V8h-2zm-8 8V8h2v8H4z" />
                        </svg>
                    </span>
                </Link>

                <Link to="/bodegas" className="group relative bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg shadow-card hover:shadow-card-hover transition-all duration-200 border border-gray-200">
                    <div>
                        <span className="rounded-lg inline-flex p-3 bg-purple-50 text-purple-700 ring-4 ring-white">
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                        </span>
                    </div>
                    <div className="mt-8">
                        <h3 className="text-lg font-medium">
                            <span className="absolute inset-0" aria-hidden="true"></span>
                            {' '}Bodegas
                        </h3>
                        <p className="mt-2 text-sm text-gray-500">
                            Gestiona las ubicaciones físicas, estanterías y capacidad de almacenamiento.
                        </p>
                    </div>
                </Link>

                <Link to="/items" className="group relative bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg shadow-card hover:shadow-card-hover transition-all duration-200 border border-gray-200">
                    <div>
                        <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                            </svg>
                        </span>
                    </div>
                    <div className="mt-8">
                        <h3 className="text-lg font-medium">
                            <span className="absolute inset-0" aria-hidden="true"></span>
                            {' '}Items
                        </h3>
                        <p className="mt-2 text-sm text-gray-500">
                            Controla el inventario físico individual, estados y movimientos.
                        </p>
                    </div>
                </Link>
            </div>
        </div>
    );
};

export default Dashboard;
