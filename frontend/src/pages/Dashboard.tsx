import { useState, useEffect } from 'react'
import { 
  FileText, 
  Tag, 
  Cpu, 
  FolderOpen, 
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { motion } from 'framer-motion'
import { projectsAPI, processingAPI } from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'

interface DashboardStats {
  totalDocuments: number
  totalEntities: number
  processingJobs: number
  activeProjects: number
}

interface RecentActivity {
  id: string
  type: string
  description: string
  time: string
  status: 'success' | 'processing' | 'error'
}

export default function Dashboard() {
  const { isAuthenticated, hasCheckedAuth } = useAuth()
  const [selectedPeriod, setSelectedPeriod] = useState('7d')
  const [stats, setStats] = useState<DashboardStats>({
    totalDocuments: 0,
    totalEntities: 0,
    processingJobs: 0,
    activeProjects: 0
  })
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [processingStatus, setProcessingStatus] = useState({
    documentProcessing: { inQueue: 0, progress: 0 },
    entityExtraction: { running: 0, progress: 0 }
  })

  useEffect(() => {
    // Only fetch dashboard data if user is authenticated and auth check is complete
    if (isAuthenticated && hasCheckedAuth) {
      fetchDashboardData()
    }
  }, [selectedPeriod, isAuthenticated, hasCheckedAuth])

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      
      // Fetch projects to get counts
      const projectsResponse = await projectsAPI.getUserProjects()
      const activeProjects = projectsResponse.data.filter((p: any) => p.status === 'active').length
      
      // Fetch processing jobs
      const jobsResponse = await processingAPI.getJobs()
      const processingJobs = jobsResponse.data ? jobsResponse.data.filter((j: any) => 
        j.status === 'running' || j.status === 'queued'
      ).length : 0
      
      // Calculate totals from projects
      let totalDocuments = 0
      let totalEntities = 0
      
      for (const project of projectsResponse.data) {
        totalDocuments += project.documents_count || 0
        totalEntities += project.entities_count || 0
      }
      
      setStats({
        totalDocuments,
        totalEntities,
        processingJobs,
        activeProjects
      })
      
      // Generate recent activities from projects and jobs
      const activities: RecentActivity[] = []
      
      // Add recent project activities
      const recentProjects = projectsResponse.data
        .sort((a: any, b: any) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, 2)
      
      recentProjects.forEach((project: any) => {
        activities.push({
          id: `project-${project.id}`,
          type: 'Project Updated',
          description: project.name,
          time: formatTimeAgo(project.updated_at),
          status: 'success'
        })
      })
      
      // Add recent job activities if jobs exist
      if (jobsResponse.data && jobsResponse.data.length > 0) {
        const recentJobs = jobsResponse.data
          .sort((a: any, b: any) => new Date(b.created_at || b.started_at).getTime() - new Date(a.created_at || a.started_at).getTime())
          .slice(0, 2)
        
        recentJobs.forEach((job: any) => {
          activities.push({
            id: `job-${job.id}`,
            type: getJobActivityType(job.status),
            description: job.name || `Job ${job.id}`,
            time: formatTimeAgo(job.created_at || job.started_at),
            status: getJobActivityStatus(job.status)
          })
        })
      }
      
      setRecentActivities(activities.slice(0, 4))
      
      // Set processing status
      setProcessingStatus({
        documentProcessing: { 
          inQueue: jobsResponse.data ? jobsResponse.data.filter((j: any) => j.status === 'queued').length : 0,
          progress: 65 // This would come from actual processing data
        },
        entityExtraction: { 
          running: jobsResponse.data ? jobsResponse.data.filter((j: any) => j.status === 'running').length : 0,
          progress: 45 // This would come from actual processing data
        }
      })
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      // Set default values on error
      setStats({
        totalDocuments: 0,
        totalEntities: 0,
        processingJobs: 0,
        activeProjects: 0
      })
      setRecentActivities([])
    } finally {
      setIsLoading(false)
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`
    return `${Math.floor(diffInMinutes / 1440)} days ago`
  }

  const getJobActivityType = (status: string) => {
    switch (status) {
      case 'running': return 'Processing Started'
      case 'completed': return 'Processing Completed'
      case 'failed': return 'Processing Failed'
      case 'queued': return 'Processing Queued'
      default: return 'Processing Updated'
    }
  }

  const getJobActivityStatus = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'running': return 'processing'
      case 'failed': return 'error'
      default: return 'processing'
    }
  }

const quickActions = [
  { name: 'Upload Document', description: 'Add new document for processing', icon: FileText, href: '/documents' },
  { name: 'Create Project', description: 'Start a new NER project', icon: FolderOpen, href: '/projects' },
  { name: 'View Entities', description: 'Browse extracted entities', icon: Tag, href: '/entities' },
  { name: 'Monitor Jobs', description: 'Check processing status', icon: Cpu, href: '/processing' },
]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        <span className="ml-2 text-gray-600">Loading dashboard...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Here's what's happening with your NER projects.</p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="input-field w-auto"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-600">Total Documents</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalDocuments}</p>
            </div>
          </div>
        </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <Tag className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-600">Entities Found</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalEntities}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <Cpu className="w-5 h-5 text-primary-600" />
                </div>
              </div>
              <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-600">Processing Jobs</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.processingJobs}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <FolderOpen className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.activeProjects}</p>
            </div>
            </div>
          </motion.div>
      </div>

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {quickActions.map((action) => (
              <a
                key={action.name}
                href={action.href}
                className="group p-3 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                    <action.icon className="w-4 h-4 text-primary-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900 group-hover:text-primary-700">
                      {action.name}
                    </p>
                    <p className="text-xs text-gray-500">{action.description}</p>
                  </div>
                </div>
              </a>
            ))}
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          {recentActivities.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">No recent activity</p>
            </div>
          ) : (
          <div className="space-y-3">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  {activity.status === 'success' && (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  )}
                  {activity.status === 'processing' && (
                    <Clock className="w-4 h-4 text-yellow-500" />
                  )}
                  {activity.status === 'error' && (
                    <AlertCircle className="w-4 h-4 text-red-500" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{activity.type}</p>
                  <p className="text-sm text-gray-500">{activity.description}</p>
                  <p className="text-xs text-gray-400">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
          )}
        </motion.div>
      </div>

      {/* Processing Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Status</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900">Document Processing</p>
              <p className="text-sm text-gray-500">
                {processingStatus.documentProcessing.inQueue} documents in queue
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full" 
                  style={{ width: `${processingStatus.documentProcessing.progress}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-600">{processingStatus.documentProcessing.progress}%</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900">Entity Extraction</p>
              <p className="text-sm text-gray-500">
                Running on {processingStatus.entityExtraction.running} documents
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-accent-600 h-2 rounded-full" 
                  style={{ width: `${processingStatus.entityExtraction.progress}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-600">{processingStatus.entityExtraction.progress}%</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
