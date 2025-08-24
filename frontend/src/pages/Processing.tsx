import { useState, useEffect } from 'react'
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Cpu,
  Settings,
  Eye,
  Loader2
} from 'lucide-react'
import { motion } from 'framer-motion'
import { formatDate } from '@/lib/utils'
import { processingAPI } from '@/services/api'
import toast from 'react-hot-toast'
import { useAuth } from '@/contexts/AuthContext'

interface ProcessingJob {
  id: number
  job_id: string
  name: string
  description: string
  job_type: string
  status: 'pending' | 'queued' | 'running' | 'completed' | 'failed' | 'cancelled' | 'retrying'
  progress: number
  total_steps: number
  current_step: string
  started_at: string | null
  completed_at: string | null
  estimated_completion: string | null
  error_message: string
  priority: number
  retry_count: number
  max_retries: number
  created_at: string
  updated_at: string
  document?: number
  project?: number
}

const statusConfig = {
  pending: { label: 'Pending', icon: Clock, color: 'text-gray-600', bg: 'bg-gray-100' },
  queued: { label: 'Queued', icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  running: { label: 'Running', icon: RefreshCw, color: 'text-blue-600', bg: 'bg-blue-100' },
  completed: { label: 'Completed', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
  failed: { label: 'Failed', icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-100' },
  cancelled: { label: 'Cancelled', icon: Square, color: 'text-gray-600', bg: 'bg-gray-100' },
  retrying: { label: 'Retrying', icon: RefreshCw, color: 'text-orange-600', bg: 'bg-orange-100' }
}

const getPriorityLabel = (priority: number) => {
  if (priority >= 8) return { label: 'High', color: 'text-red-600', bg: 'bg-red-100' }
  if (priority >= 4) return { label: 'Medium', color: 'text-yellow-600', bg: 'bg-yellow-100' }
  return { label: 'Low', color: 'text-green-600', bg: 'bg-green-100' }
}

export default function Processing() {
  const { isAuthenticated, hasCheckedAuth } = useAuth()
  const [jobs, setJobs] = useState<ProcessingJob[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedJob, setSelectedJob] = useState<ProcessingJob | null>(null)
  const [showNewJobModal, setShowNewJobModal] = useState(false)

  useEffect(() => {
    // Only fetch jobs if user is authenticated and auth check is complete
    if (isAuthenticated && hasCheckedAuth) {
      fetchJobs()
    }
  }, [isAuthenticated, hasCheckedAuth])

  const fetchJobs = async () => {
    try {
      setIsLoading(true)
      const response = await processingAPI.getJobs()
      // The backend returns a paginated response with {count, results, next, previous}
      const jobsData = response.data.results || response.data || []
      setJobs(jobsData)
    } catch (error: any) {
      console.error('Error fetching processing jobs:', error)
      const message = error.response?.data?.detail || 
                     error.message || 
                     'Failed to fetch processing jobs. Please check if the backend is running.'
      toast.error(message)
      
      // If it's a network error, show helpful message
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        toast.error('Cannot connect to backend. Please ensure Django server is running on port 8000.')
      }
      setJobs([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleJobAction = async (jobId: number, action: string) => {
    try {
      switch (action) {
        case 'start':
          // This would call an API endpoint to start the job
          toast.success('Job started successfully')
          break
        case 'pause':
          // This would call an API endpoint to pause the job
          toast.success('Job paused successfully')
          break
        case 'stop':
          // This would call an API endpoint to stop the job
          toast.success('Job stopped successfully')
          break
        case 'retry':
          // This would call an API endpoint to retry the job
          toast.success('Job retry initiated successfully')
          break
        default:
          return
      }
      
      // Refresh the jobs list
      fetchJobs()
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update job'
      toast.error(message)
    }
  }

  const getStatusIcon = (status: string) => {
    const config = statusConfig[status as keyof typeof statusConfig]
    return config ? config.icon : Clock
  }

  const getStatusColor = (status: string) => {
    const config = statusConfig[status as keyof typeof statusConfig]
    return config ? config.color : 'text-gray-600'
  }

  const getStatusBg = (status: string) => {
    const config = statusConfig[status as keyof typeof statusConfig]
    return config ? config.bg : 'bg-gray-100'
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        <span className="ml-2 text-gray-600">Loading processing jobs...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Processing Jobs</h1>
          <p className="text-gray-600">Monitor and manage your NER processing jobs.</p>
        </div>
        <button
          onClick={() => setShowNewJobModal(true)}
          className="btn-primary flex items-center"
        >
          <Play className="w-4 h-4 mr-2" />
          New Job
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <RefreshCw className="w-5 h-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Running</p>
              <p className="text-2xl font-semibold text-gray-900">
                {jobs.filter(j => j.status === 'running').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Queued</p>
              <p className="text-2xl font-semibold text-gray-900">
                {jobs.filter(j => j.status === 'queued').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-semibold text-gray-900">
                {jobs.filter(j => j.status === 'completed').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-2xl font-semibold text-gray-900">
                {jobs.filter(j => j.status === 'failed').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Active Jobs</h3>
          <div className="flex space-x-2">
            <button 
              onClick={fetchJobs}
              className="btn-secondary flex items-center"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
            <button className="btn-secondary flex items-center">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </button>
          </div>
        </div>
        
        {jobs.length === 0 ? (
          <div className="text-center py-12">
            <Cpu className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No processing jobs found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first processing job.
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowNewJobModal(true)}
                className="btn-primary"
              >
                <Play className="w-4 h-4 mr-2" />
                New Job
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job, index) => {
              const StatusIcon = getStatusIcon(job.status)
              const statusColor = getStatusColor(job.status)
              const statusBg = getStatusBg(job.status)
              const priority = getPriorityLabel(job.priority)
              
              return (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${statusBg}`}>
                        <StatusIcon className={`w-5 h-5 ${statusColor}`} />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{job.name}</h4>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBg} ${statusColor}`}>
                            {statusConfig[job.status]?.label}
                          </span>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${priority.bg} ${priority.color}`}>
                            {priority.label}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setSelectedJob(job)}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      {job.status === 'running' && (
                        <>
                          <button
                            onClick={() => handleJobAction(job.id, 'pause')}
                            className="text-yellow-600 hover:text-yellow-900"
                          >
                            <Pause className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleJobAction(job.id, 'stop')}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Square className="w-4 h-4" />
                          </button>
                        </>
                      )}
                      {job.status === 'pending' && (
                        <button
                          onClick={() => handleJobAction(job.id, 'start')}
                          className="text-green-600 hover:text-green-900"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      {job.status === 'failed' && job.retry_count < job.max_retries && (
                        <button
                          onClick={() => handleJobAction(job.id, 'retry')}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <RefreshCw className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div className="text-sm">
                      <span className="text-gray-500">Documents:</span>
                      <span className="ml-1 text-gray-900">{job.document}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-500">Entities:</span>
                      <span className="ml-1 text-gray-900">{job.document}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-500">Model:</span>
                      <span className="ml-1 text-gray-900">{job.job_type}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-500">Started:</span>
                      <span className="ml-1 text-gray-900">
                        {job.started_at ? formatDate(job.started_at) : 'Not started'}
                      </span>
                    </div>
                  </div>
                  
                  {job.status === 'running' && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Progress</span>
                        <span className="text-gray-900">{job.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${job.progress}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-500">
                        Estimated time remaining: {job.estimated_completion}
                      </div>
                    </div>
                  )}
                  
                  {job.status === 'failed' && job.error_message && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-800">{job.error_message}</p>
                    </div>
                  )}
                </motion.div>
              )
            })}
          </div>
        )}
      </div>

      {/* Job Detail Modal */}
      {selectedJob && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Job Details</h3>
                <button
                  onClick={() => setSelectedJob(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getStatusBg(selectedJob.status)}`}>
                    {(() => {
                      const StatusIcon = getStatusIcon(selectedJob.status)
                      return <StatusIcon className={`w-6 h-6 ${getStatusColor(selectedJob.status)}`} />
                    })()}
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold text-gray-900">{selectedJob.name}</h4>
                    <p className="text-sm text-gray-600">{selectedJob.job_type}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <p className="text-sm text-gray-900">
                      {statusConfig[selectedJob.status]?.label}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Priority</label>
                    <p className="text-sm text-gray-900">
                      {getPriorityLabel(selectedJob.priority).label}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Documents</label>
                    <p className="text-sm text-gray-900">{selectedJob.document}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Entities Found</label>
                    <p className="text-sm text-gray-900">{selectedJob.document}</p>
                  </div>
                </div>
                
                {selectedJob.started_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Started At</label>
                    <p className="text-sm text-gray-900">{formatDate(selectedJob.started_at)}</p>
                  </div>
                )}
                
                {selectedJob.completed_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Completed At</label>
                    <p className="text-sm text-gray-900">{formatDate(selectedJob.completed_at)}</p>
                  </div>
                )}
                
                {selectedJob.error_message && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Error</label>
                    <p className="text-sm text-red-800 bg-red-50 p-3 rounded-lg mt-1">
                      {selectedJob.error_message}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
