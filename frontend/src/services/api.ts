import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = localStorage.getItem('refresh_token')
                if (refreshToken) {
                    const response = await axios.post('/api/auth/refresh/', {
                        refresh: refreshToken,
                    })
                    const { access } = response.data
                    localStorage.setItem('access_token', access)
                    originalRequest.headers.Authorization = `Bearer ${access}`
                    return api(originalRequest)
                } else {
                    // No refresh token, clear access token and let the error propagate
                    localStorage.removeItem('access_token')
                }
            } catch (refreshError) {
                // Refresh failed, clear tokens and let the error propagate
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                // Only redirect to login if we're not already on the login page
                if (window.location.pathname !== '/login') {
                    window.location.href = '/login'
                }
            }
        }

        return Promise.reject(error)
    }
)

// Authentication API
export const authAPI = {
    login: (credentials: { username: string; password: string }) =>
        api.post('/auth/login/', credentials),

    register: (userData: { username: string; email: string; password: string; first_name: string; last_name: string }) =>
        api.post('/users/register/', userData),



    getProfile: () => api.get('/users/profile/'),

    updateProfile: (profileData: any) => api.put('/users/profile/', profileData),
}

// Projects API
export const projectsAPI = {
    list: (params?: any) => api.get('/projects/', { params }),

    create: (projectData: { name: string; description: string; users?: number[] }) =>
        api.post('/projects/create/', projectData),

    get: (slug: string) => api.get(`/projects/detail/${slug}/`),

    update: (slug: string, projectData: any) =>
        api.put(`/projects/update/${slug}/`, projectData),

    delete: (slug: string) => api.delete(`/projects/delete/${slug}/`),

    getStats: (slug: string) => api.get(`/projects/stats/${slug}/`),

    getUserProjects: () => api.get('/projects/user-projects/'),

    addMember: (slug: string, userId: number) =>
        api.post(`/projects/${slug}/members/create/`, { user: userId }),

    removeMember: (slug: string, userId: number) =>
        api.delete(`/projects/${slug}/members/${userId}/delete/`),
}

// Documents API
export const documentsAPI = {
    list: (projectSlug: string, params?: any) =>
        api.get(`/documents/list/${projectSlug}/`, { params }),

    create: (projectSlug: string, documentData: any) => {
        // If documentData is FormData (for file uploads), ensure project is included
        if (documentData instanceof FormData) {
            // Check if project is already in FormData, if not add it
            if (!documentData.has('project')) {
                documentData.append('project', projectSlug)
            }
            return api.post(`/documents/create/`, documentData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            })
        }
        // Otherwise, send as JSON with project slug
        return api.post(`/documents/create/`, { ...documentData, project: projectSlug })
    },

    upload: (projectSlug: string, file: File, metadata: any) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('project', projectSlug)
        Object.keys(metadata).forEach(key => {
            formData.append(key, metadata[key])
        })

        return api.post(`/documents/upload/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },

    get: (projectSlug: string, documentId: number) =>
        api.get(`/documents/detail/${projectSlug}/${documentId}/`),

    update: (projectSlug: string, documentId: number, documentData: any) =>
        api.put(`/documents/update/${projectSlug}/${documentId}/`, documentData),

    delete: (projectSlug: string, documentId: number) =>
        api.delete(`/documents/delete/${projectSlug}/${documentId}/`),

    process: (projectSlug: string, documentId: number, processingData: any) =>
        api.post(`/documents/process/${projectSlug}/${documentId}/`, processingData),

    getStats: (projectSlug: string, documentId: number) =>
        api.get(`/documents/stats/${projectSlug}/${documentId}/`),

    search: (projectSlug: string, query: string) =>
        api.get(`/documents/search/${projectSlug}/`, { params: { search: query } }),
}

// Entities API
export const entitiesAPI = {
    list: (projectSlug: string, documentId: number, params?: any) =>
        api.get(`/entities/list/${projectSlug}/${documentId}/`, { params }),

    create: (projectSlug: string, documentId: number, entityData: any) =>
        api.post(`/entities/create/${projectSlug}/${documentId}/`, entityData),

    get: (projectSlug: string, documentId: number, entityId: number) =>
        api.get(`/entities/detail/${projectSlug}/${documentId}/${entityId}/`),

    update: (projectSlug: string, documentId: number, entityId: number, entityData: any) =>
        api.put(`/entities/update/${projectSlug}/${documentId}/${entityId}/`, entityData),

    delete: (projectSlug: string, documentId: number, entityId: number) =>
        api.delete(`/entities/delete/${projectSlug}/${documentId}/${entityId}/`),

    verify: (projectSlug: string, documentId: number, entityId: number, verified: boolean) =>
        api.post(`/entities/verify/${projectSlug}/${documentId}/${entityId}/`, { verified }),

    bulkUpdate: (projectSlug: string, documentId: number, updates: any[]) =>
        api.post(`/entities/bulk-update/${projectSlug}/${documentId}/`, { updates }),

    bulkVerify: (projectSlug: string, documentId: number, entityIds: number[], verified: boolean) =>
        api.post(`/entities/bulk-verify/${projectSlug}/${documentId}/`, { entity_ids: entityIds, verified }),

    getStats: (projectSlug: string, documentId: number) =>
        api.get(`/entities/stats/${projectSlug}/${documentId}/`),
}

// LLM Integration API
export const llmAPI = {
    getModels: () => api.get('/llm/models/'),

    createModel: (modelData: any) => api.post('/llm/models/', modelData),

    getModel: (modelId: number) => api.get(`/llm/models/${modelId}/`),

    updateModel: (modelId: number, modelData: any) => api.put(`/llm/models/${modelId}/`, modelData),

    deleteModel: (modelId: number) => api.delete(`/llm/models/${modelId}/`),

    testConnection: (modelId: number) => api.post(`/llm/models/${modelId}/test/`),

    getPrompts: () => api.get('/llm/prompts/'),

    createPrompt: (promptData: any) => api.post('/llm/prompts/', promptData),
}

// Processing API
export const processingAPI = {
    getJobs: (params?: any) => api.get('/processing/jobs/', { params }),

    getJob: (jobId: number) => api.get(`/processing/jobs/${jobId}/`),

    getJobStatus: (jobId: number) => api.get(`/processing/jobs/${jobId}/progress/`),

    cancelJob: (jobId: number) => api.delete(`/processing/jobs/${jobId}/`),

    getProcessingStatus: (documentId: number) => api.get(`/processing/jobs/${documentId}/progress/`),

    // Additional endpoints that match the backend
    createJob: (jobData: any) => api.post('/processing/jobs/create/', jobData),

    updateJob: (jobId: number, jobData: any) => api.put(`/processing/jobs/${jobId}/update/`, jobData),

    deleteJob: (jobId: number) => api.delete(`/processing/jobs/${jobId}/delete/`),

    getJobResult: (jobId: number) => api.get(`/processing/jobs/${jobId}/result/`),

    performJobAction: (jobId: number, action: string) => api.post(`/processing/jobs/${jobId}/action/`, { action }),

    getJobStats: () => api.get('/processing/jobs/stats/'),

    getQueueStatus: () => api.get('/processing/jobs/queue-status/'),
}

// Core API
export const coreAPI = {
    getEntityTypes: () => api.get('/core/entity-types/'),

    createEntityType: (entityTypeData: any) => api.post('/core/entity-types/', entityTypeData),

    updateEntityType: (entityTypeId: number, entityTypeData: any) =>
        api.put(`/core/entity-types/${entityTypeId}/`, entityTypeData),

    deleteEntityType: (entityTypeId: number) => api.delete(`/core/entity-types/${entityTypeId}/`),
}

export default api
