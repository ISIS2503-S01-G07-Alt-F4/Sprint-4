import React, { useEffect, useState } from 'react';
import type { AuditLog, AuditedService } from '../types';
import { getAuditLogs, getAuditedServices } from '../services/auditService';

const AuditLogs: React.FC = () => {
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [services, setServices] = useState<AuditedService[]>([]);
    const [selectedService, setSelectedService] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(true);
    const [page, setPage] = useState<number>(1);
    const [limit, setLimit] = useState<number>(10);
    const [total, setTotal] = useState<number>(0);
    const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

    useEffect(() => {
        const fetchServices = async () => {
            try {
                const servicesData = await getAuditedServices();
                setServices(servicesData);
            } catch (error) {
                console.error('Error fetching services:', error);
            }
        };
        fetchServices();
    }, []);

    useEffect(() => {
        const fetchLogs = async () => {
            setLoading(true);
            try {
                const logsData = await getAuditLogs(page, limit, selectedService);
                setLogs(logsData.data);
                setTotal(logsData.total);
            } catch (error) {
                console.error('Error fetching audit logs:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchLogs();
    }, [page, limit, selectedService]);

    const totalPages = Math.ceil(total / limit);

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setPage(newPage);
        }
    };

    const handleServiceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedService(e.target.value);
        setPage(1); // Reset to first page when filter changes
    };

    const toggleExpand = (id: string) => {
        setExpandedLogId(expandedLogId === id ? null : id);
    };

    if (loading && logs.length === 0) {
        return <div className="p-4">Loading...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Audit Logs</h1>

            <div className="mb-4 flex justify-between items-center">
                <div>
                    <label htmlFor="service-filter" className="block text-sm font-medium text-gray-700">
                        Filter by Service
                    </label>
                    <select
                        id="service-filter"
                        value={selectedService}
                        onChange={handleServiceChange}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    >
                        <option value="">All Services</option>
                        {services.map((service) => (
                            <option key={service.id} value={service.id}>
                                {service.name}
                            </option>
                        ))}
                    </select>
                </div>
                <div>
                    <label htmlFor="limit-select" className="block text-sm font-medium text-gray-700">
                        Items per page
                    </label>
                    <select
                        id="limit-select"
                        value={limit}
                        onChange={(e) => {
                            setLimit(Number(e.target.value));
                            setPage(1);
                        }}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    >
                        <option value={5}>5</option>
                        <option value={10}>10</option>
                        <option value={20}>20</option>
                        <option value={50}>50</option>
                    </select>
                </div>
            </div>

            <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Timestamp</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Service</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Action</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">User</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Description</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Entity</th>
                            <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                                <span className="sr-only">Details</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                        {logs.map((log) => (
                            <React.Fragment key={log.id}>
                                <tr className={expandedLogId === log.id ? 'bg-gray-50' : ''}>
                                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-500 sm:pl-6">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </td>
                                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{log.audited_service_id}</td>
                                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                        <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${log.action === 'DELETE' ? 'bg-red-100 text-red-800' :
                                                log.action === 'CREATE' ? 'bg-green-100 text-green-800' :
                                                    log.action === 'UPDATE' ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-blue-100 text-blue-800'
                                            }`}>
                                            {log.action}
                                        </span>
                                    </td>
                                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{log.user_id}</td>
                                    <td className="px-3 py-4 text-sm text-gray-500">{log.description}</td>
                                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{log.entity} ({log.entity_id})</td>
                                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                                        <button
                                            onClick={() => toggleExpand(log.id)}
                                            className="text-indigo-600 hover:text-indigo-900"
                                        >
                                            {expandedLogId === log.id ? 'Hide Details' : 'View Details'}
                                        </button>
                                    </td>
                                </tr>
                                {expandedLogId === log.id && (
                                    <tr>
                                        <td colSpan={7} className="px-4 py-4 bg-gray-50">
                                            <div className="text-sm text-gray-700">
                                                <h4 className="font-bold mb-2">Metadata:</h4>
                                                <pre className="bg-gray-100 p-2 rounded overflow-x-auto">
                                                    {JSON.stringify(log.metadata, null, 2)}
                                                </pre>
                                                <div className="mt-2">
                                                    <span className="font-bold">IP:</span> {log.ip || 'N/A'}
                                                </div>
                                                <div className="mt-1">
                                                    <span className="font-bold">Registered At:</span> {new Date(log.registered_at).toLocaleString()}
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                        <p className="text-sm text-gray-700">
                            Showing <span className="font-medium">{(page - 1) * limit + 1}</span> to <span className="font-medium">{Math.min(page * limit, total)}</span> of <span className="font-medium">{total}</span> results
                        </p>
                    </div>
                    <div>
                        <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                            <button
                                onClick={() => handlePageChange(page - 1)}
                                disabled={page === 1}
                                className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                            >
                                <span className="sr-only">Previous</span>
                                Previous
                            </button>
                            {/* Simple pagination: just show current page */}
                            <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                                Page {page} of {totalPages}
                            </span>
                            <button
                                onClick={() => handlePageChange(page + 1)}
                                disabled={page === totalPages}
                                className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                            >
                                <span className="sr-only">Next</span>
                                Next
                            </button>
                        </nav>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuditLogs;
