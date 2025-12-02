import axios from 'axios';
import type { AuditedService, PaginatedAuditLogs } from '../types';

const auditApi = axios.create({
    baseURL: '/audit-api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getAuditLogs = async (page: number = 1, limit: number = 10, serviceId?: string): Promise<PaginatedAuditLogs> => {
    let url = `/audit-logs/?page=${page}&limit=${limit}`;
    if (serviceId) {
        url += `&service_id=${serviceId}`;
    }
    const response = await auditApi.get(url);
    return response.data;
};

export const getAuditedServices = async (): Promise<AuditedService[]> => {
    const response = await auditApi.get('/audited-services/');
    return response.data;
};
