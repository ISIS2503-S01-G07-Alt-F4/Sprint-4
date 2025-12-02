import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import ProvesiLogo from '../assets/ProvesiLogo.png';

const Navbar: React.FC = () => {
    const location = useLocation();

    const isActive = (path: string) => {
        return location.pathname === path ? 'text-primary-600 border-b-2 border-primary-600' : 'text-gray-600 hover:text-primary-600';
    };

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center">
                            <img src={ProvesiLogo} alt="Provesi Logo" className="h-25 w-auto mr-2" />
                            <Link to="/" className="text-xl font-bold text-gray-900">WMS</Link>
                        </div>
                        <div className="hidden sm:ml-10 sm:flex sm:space-x-8">
                            <Link to="/" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/')}`}>
                                Dashboard
                            </Link>
                            <Link to="/productos" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/productos')}`}>
                                Productos
                            </Link>
                            <Link to="/bodegas" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/bodegas')}`}>
                                Bodegas
                            </Link>
                            <Link to="/items" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/items')}`}>
                                Items
                            </Link>
                            <Link to="/auditoria" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/auditoria')}`}>
                                Auditoría
                            </Link>
                        </div>
                    </div>
                    <div className="flex items-center">
                        <div className="flex-shrink-0">
                            <button className="relative inline-flex items-center gap-x-1.5 rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600">
                                Iniciar Sesión
                            </button>
                        </div>
                        <div className="hidden md:ml-4 md:flex md:flex-shrink-0 md:items-center">
                            <span className="text-sm text-gray-500">user@provesi.com</span>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
