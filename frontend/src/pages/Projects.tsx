import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Plus, 
  Search, 
  FolderOpen, 
  Play,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  CheckCircle,
  BookOpen,
  Target,
  Lightbulb,
  Upload,
  FileText
} from 'lucide-react'
import { motion } from 'framer-motion'
import { formatDate } from '@/lib/utils'
import { projectsAPI } from '@/services/api'
import ProjectModal from '@/components/ProjectModal'
import DocumentUpload from '@/components/DocumentUpload'

import toast from 'react-hot-toast'
import { useAuth } from '@/contexts/AuthContext'

interface Project {
  id: number
  name: string
  description: string
  status: 'planning' | 'active' | 'completed' | 'on_hold' | 'cancelled'
  documents_count: number
  entities_count?: number // Optional since it's not in ProjectListSerializer
  members_count: number
  created_at: string
  updated_at?: string // Optional since it's not in ProjectListSerializer
  research_area: string
  objectives?: string[] // Optional since it's not in ProjectListSerializer
  tags?: string[] // Optional since it's not in ProjectListSerializer
  slug: string
}

const statusConfig = {
  planning: { label: 'Planning', color: 'text-blue-600', bg: 'bg-blue-100' },
  active: { label: 'Active', color: 'text-green-600', bg: 'bg-green-100' },
  completed: { label: 'Completed', color: 'text-purple-600', bg: 'bg-purple-100' },
  on_hold: { label: 'On Hold', color: 'text-yellow-600', bg: 'bg-yellow-100' },
  cancelled: { label: 'Cancelled', color: 'text-red-600', bg: 'bg-red-100' }
}

export default function Projects() {
  const { isAuthenticated, hasCheckedAuth } = useAuth()
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [showNewProjectModal, setShowNewProjectModal] = useState(false)
  const [showProjectMenu, setShowProjectMenu] = useState<number | null>(null)
  const [showDocumentUpload, setShowDocumentUpload] = useState<Project | null>(null)

  useEffect(() => {
    // Only fetch projects if user is authenticated and auth check is complete
    if (isAuthenticated && hasCheckedAuth) {
      fetchProjects()
    } else {
      // If not authenticated, set loading to false so we don't show infinite loading
      setIsLoading(false)
    }
  }, [isAuthenticated, hasCheckedAuth])

  const fetchProjects = async () => {
    try {
      setIsLoading(true)
      const response = await projectsAPI.getUserProjects()
      setProjects(response.data)
    } catch (error: any) {
      console.error('Error fetching projects:', error)
      const message = error.response?.data?.detail || 
                     error.message || 
                     'Failed to fetch projects. Please check if the backend is running.'
      toast.error(message)
      
      // If it's a network error, show helpful message
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        toast.error('Cannot connect to backend. Please ensure Django server is running on port 8000.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleProjectAction = async (projectId: number, action: string) => {
    try {
      const project = projects.find(p => p.id === projectId)
      if (!project) return

      switch (action) {
        case 'activate':
          await projectsAPI.update(project.slug, { status: 'active' })
          toast.success('Project activated successfully')
          break
        case 'complete':
          await projectsAPI.update(project.slug, { status: 'completed' })
          toast.success('Project completed successfully')
          break
        case 'hold':
          await projectsAPI.update(project.slug, { status: 'on_hold' })
          toast.success('Project put on hold successfully')
          break
        case 'cancel':
          await projectsAPI.update(project.slug, { status: 'cancelled' })
          toast.success('Project cancelled successfully')
          break
        default:
          return
      }
      
      fetchProjects() // Refresh the list
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update project'
      toast.error(message)
    }
  }

  const handleDeleteProject = async (projectId: number) => {
    try {
      const project = projects.find(p => p.id === projectId)
      if (!project) return

      if (confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) {
        await projectsAPI.delete(project.slug)
        toast.success('Project deleted successfully')
        fetchProjects() // Refresh the list
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to delete project'
      toast.error(message)
    }
  }

  const getProjectIcon = (project: Project, size: 'sm' | 'lg' = 'sm') => {
    const iconSize = size === 'lg' ? 'w-8 h-8' : 'w-5 h-5'
    
    // Get icon based on research area
    const researchArea = project.research_area?.toLowerCase() || ''
    
    if (researchArea.includes('literature') || researchArea.includes('poetry') || researchArea.includes('text')) {
      return <BookOpen className={`${iconSize} text-blue-600`} />
    } else if (researchArea.includes('history') || researchArea.includes('historical')) {
      return <Target className={`${iconSize} text-green-600`} />
    } else if (researchArea.includes('religious') || researchArea.includes('islamic')) {
      return <Lightbulb className={`${iconSize} text-purple-600`} />
    } else if (researchArea.includes('computer') || researchArea.includes('science')) {
      return <Target className={`${iconSize} text-orange-600`} />
    } else {
      // Default icon based on status
      switch (project.status) {
        case 'planning':
          return <Lightbulb className={`${iconSize} text-yellow-600`} />
        case 'active':
          return <Target className={`${iconSize} text-green-600`} />
        case 'completed':
          return <CheckCircle className={`${iconSize} text-purple-600`} />
        case 'on_hold':
          return <BookOpen className={`${iconSize} text-orange-600`} />
        case 'cancelled':
          return <Trash2 className={`${iconSize} text-red-600`} />
        default:
          return <FolderOpen className={`${iconSize} text-gray-600`} />
      }
    }
  }

  const handleProjectCreated = () => {
    fetchProjects() // Refresh the list after creating a new project
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading projects...</span>
      </div>
    )
  }

  // If not authenticated, show message to login
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <FolderOpen className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Authentication Required</h3>
          <p className="mt-1 text-sm text-gray-500">
            Please log in to view your projects.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">


      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600">Manage your NER projects and configurations.</p>
        </div>
        <button
          onClick={() => setShowNewProjectModal(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input-field w-auto"
        >
          <option value="all">All Status</option>
          <option value="planning">Planning</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="on_hold">On Hold</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {/* Projects Grid */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <FolderOpen className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No projects found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search or filters.'
              : 'Get started by creating your first project.'
            }
          </p>
          {!searchTerm && statusFilter === 'all' && (
            <div className="mt-6">
              <button
                onClick={() => setShowNewProjectModal(true)}
                className="btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Project
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredProjects.map((project, index) => {
            const status = statusConfig[project.status]
            
            return (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      {getProjectIcon(project)}
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{project.name}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.bg} ${status.color}`}>
                        {status.label}
                      </span>
                    </div>
                  </div>
                  
                  {/* Project Menu */}
                  <div className="relative">
                    <button 
                      onClick={() => setShowProjectMenu(showProjectMenu === project.id ? null : project.id)}
                      className="text-gray-400 hover:text-gray-600 p-1 rounded"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </button>
                    
                    {showProjectMenu === project.id && (
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                        <button
                          onClick={() => setSelectedProject(project)}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <Eye className="w-4 h-4 inline mr-2" />
                          View Details
                        </button>
                        <button
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <Edit className="w-4 h-4 inline mr-2" />
                          Edit Project
                        </button>
                        <button 
                          onClick={() => handleDeleteProject(project.id)}
                          className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4 inline mr-2" />
                          Delete Project
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {project.description}
                </p>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-sm">
                    <span className="text-gray-500">Documents:</span>
                    <span className="ml-1 text-gray-900">{project.documents_count}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Entities:</span>
                    <span className="ml-1 text-gray-900">{project.entities_count || 0}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Members:</span>
                    <span className="ml-1 text-gray-900">{project.members_count}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Research Area:</span>
                    <span className="ml-1 text-gray-900">{project.research_area || 'Not specified'}</span>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1 mb-4">
                  {project.tags && project.tags.length > 0 ? (
                    <>
                      {project.tags.slice(0, 3).map((tag, tagIndex) => (
                        <span
                          key={tagIndex}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {tag}
                        </span>
                      ))}
                      {project.tags.length > 3 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          +{project.tags.length - 3}
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="text-gray-400 text-xs">No tags</span>
                  )}
                </div>
                
                <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                  <span>Created: {formatDate(project.created_at)}</span>
                  <span>Updated: {project.updated_at ? formatDate(project.updated_at) : 'N/A'}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setSelectedProject(project)}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="text-gray-600 hover:text-gray-900">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => handleDeleteProject(project.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="flex space-x-2">
                    {/* View Documents Button */}
                    <button
                      onClick={() => navigate(`/projects/${project.slug}`)}
                      className="btn-secondary text-xs py-1 px-2"
                      title="View Documents"
                    >
                      <FileText className="w-3 h-3 mr-1" />
                      Documents
                    </button>
                    
                    {/* Upload Document Button */}
                    <button
                      onClick={() => setShowDocumentUpload(project)}
                      className="btn-secondary text-xs py-1 px-2"
                      title="Upload Document"
                    >
                      <Upload className="w-3 h-3 mr-1" />
                      Upload
                    </button>
                    
                    {/* Project Action Buttons */}
                    {project.status === 'planning' && (
                      <button
                        onClick={() => handleProjectAction(project.id, 'activate')}
                        className="btn-primary text-xs py-1 px-2"
                      >
                        <Play className="w-3 h-3 mr-1" />
                        Start
                      </button>
                    )}
                    {project.status === 'active' && (
                      <button
                        onClick={() => handleProjectAction(project.id, 'complete')}
                        className="btn-secondary text-xs py-1 px-2"
                      >
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Complete
                      </button>
                    )}
                    {project.status === 'on_hold' && (
                      <button
                        onClick={() => handleProjectAction(project.id, 'activate')}
                        className="btn-primary text-xs py-1 px-2"
                      >
                        <Play className="w-3 h-3 mr-1" />
                        Resume
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}

      {/* Project Creation Modal */}
      <ProjectModal
        isOpen={showNewProjectModal}
        onClose={() => setShowNewProjectModal(false)}
        onProjectCreated={handleProjectCreated}
      />

      {/* Document Upload Modal */}
      {showDocumentUpload && (
        <DocumentUpload
          projectSlug={showDocumentUpload.slug}
          projectName={showDocumentUpload.name}
          isOpen={!!showDocumentUpload}
          onClose={() => setShowDocumentUpload(null)}
          onDocumentUploaded={() => {
            fetchProjects() // Refresh projects to update document count
            setShowDocumentUpload(null)
          }}
        />
      )}



      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-3xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Project Details</h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => navigate(`/projects/${selectedProject.slug}`)}
                    className="btn-secondary text-sm py-2 px-4 flex items-center"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    View Documents
                  </button>
                  <button
                    onClick={() => setShowDocumentUpload(selectedProject)}
                    className="btn-primary text-sm py-2 px-4 flex items-center"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Document
                  </button>
                  <button
                    onClick={() => setSelectedProject(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-16 h-16 bg-primary-100 rounded-lg flex items-center justify-center">
                    {getProjectIcon(selectedProject)}
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xl font-semibold text-gray-900">{selectedProject.name}</h4>
                    <p className="text-gray-600 mt-1">{selectedProject.description}</p>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        statusConfig[selectedProject.status]?.bg
                      } ${
                        statusConfig[selectedProject.status]?.color
                      }`}>
                        {statusConfig[selectedProject.status]?.label}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{selectedProject.documents_count}</div>
                    <div className="text-sm text-gray-600">Documents</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{selectedProject.entities_count || 0}</div>
                    <div className="text-sm text-gray-600">Entities</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{selectedProject.members_count}</div>
                    <div className="text-sm text-gray-600">Members</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{selectedProject.research_area}</div>
                    <div className="text-sm text-gray-600">Research Area</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Objectives</h5>
                    <div className="flex flex-wrap gap-2">
                      {selectedProject.objectives && selectedProject.objectives.length > 0 ? (
                        selectedProject.objectives.map((objective, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {objective}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-500 text-sm">No objectives specified</span>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Tags</h5>
                    <div className="flex flex-wrap gap-2">
                      {selectedProject.tags && selectedProject.tags.length > 0 ? (
                        selectedProject.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {tag}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-500 text-sm">No tags specified</span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Created</label>
                    <p className="text-gray-900">{formatDate(selectedProject.created_at)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Last Updated</label>
                    <p className="text-gray-900">{selectedProject.updated_at ? formatDate(selectedProject.updated_at) : 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Click outside to close project menu */}
      {showProjectMenu !== null && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowProjectMenu(null)}
        />
      )}
    </div>
  )
}
