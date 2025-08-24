import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft,
  Target,
  Upload,
  FileText,
  Trash2,
  Eye,
  Calendar,
  User,
  Tag,
  AlertTriangle,
  Play,
  CheckCircle
} from 'lucide-react'
import { projectsAPI, documentsAPI } from '@/services/api'

import DocumentUpload from '@/components/DocumentUpload'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'

interface Project {
  id: number
  name: string
  description: string
  slug: string
  research_area: string
  methodology: string
  objectives: string
  timeline: string
  status: string
  is_public: boolean
  allow_public_view: boolean
  tags: string[]
  references: string
  created_by: {
    id: number
    username: string
    full_name: string
    institution: string
    academic_title: string
    research_focus: string
  }
  created_at: string
  updated_at: string
  members_count: number
  documents_count: number
  entities_count: number
  verified_entities_count: number
}

interface Document {
  id: number
  title: string
  description: string
  processing_status: string
  word_count: number
  line_count: number
  language: string
  total_entities: number
  verified_entities: number
  created_by: {
    username: string
    full_name: string
  }
  created_at: string
  tags: string[]
}

const statusConfig = {
  planning: { label: 'Planning', bg: 'bg-blue-100', color: 'text-blue-800', icon: Target },
  active: { label: 'Active', bg: 'bg-green-100', color: 'text-green-800', icon: Play },
  completed: { label: 'Completed', bg: 'bg-purple-100', color: 'text-purple-800', icon: CheckCircle },
  on_hold: { label: 'On Hold', bg: 'bg-yellow-100', color: 'text-yellow-800', icon: Target },
  cancelled: { label: 'Cancelled', bg: 'bg-red-100', color: 'text-red-800', icon: Target }
}

const processingStatusConfig = {
  pending: { label: 'Pending', bg: 'bg-yellow-100', color: 'text-yellow-800' },
  processing: { label: 'Processing', bg: 'bg-blue-100', color: 'text-blue-800' },
  completed: { label: 'Completed', bg: 'bg-green-100', color: 'text-green-800' },
  failed: { label: 'Failed', bg: 'bg-red-100', color: 'text-red-800' },
  cancelled: { label: 'Cancelled', bg: 'bg-gray-100', color: 'text-gray-800' }
}

export default function ProjectDetail() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()

  
  const [project, setProject] = useState<Project | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showDocumentUpload, setShowDocumentUpload] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<Document | null>(null)

  useEffect(() => {
    if (slug) {
      fetchProject()
      fetchDocuments()
    }
  }, [slug])

  const fetchProject = async () => {
    try {
      setIsLoading(true)
      const response = await projectsAPI.get(slug!)
      setProject(response.data)
    } catch (error: any) {
      console.error('Error fetching project:', error)
      toast.error('Failed to fetch project details')
      navigate('/projects')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchDocuments = async () => {
    try {
      const response = await documentsAPI.list(slug!)
      const documentsData = response.data.results || response.data
      setDocuments(documentsData)
    } catch (error: any) {
      console.error('Error fetching documents:', error)
      toast.error('Failed to fetch documents')
    }
  }

  const handleDeleteDocument = async (document: Document) => {
    try {
      await documentsAPI.delete(slug!, document.id)
      toast.success('Document deleted successfully')
      setShowDeleteConfirm(null)
      fetchDocuments()
      fetchProject() // Refresh project to update document count
    } catch (error: any) {
      console.error('Error deleting document:', error)
      const message = error.response?.data?.detail || 'Failed to delete document'
      toast.error(message)
    }
  }

  const handleStartProject = async () => {
    if (!project) return
    
    try {
      await projectsAPI.update(project.slug, { status: 'active' })
      toast.success('Project started successfully!')
      fetchProject()
    } catch (error: any) {
      console.error('Error starting project:', error)
      toast.error('Failed to start project')
    }
  }

  const handleCompleteProject = async () => {
    if (!project) return
    
    try {
      await projectsAPI.update(project.slug, { status: 'completed' })
      toast.success('Project completed successfully!')
      fetchProject()
    } catch (error: any) {
      console.error('Error completing project:', error)
      toast.error('Failed to complete project')
    }
  }



  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getLanguageLabel = (code: string) => {
    const languages: { [key: string]: string } = {
      'ur': 'Urdu (اردو)',
      'en': 'English',
      'ar': 'Arabic (العربية)',
      'fa': 'Persian (فارسی)',
      'hi': 'Hindi (हिन्दी)'
    }
    return languages[code] || code
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading project details...</p>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Project not found</p>
          <button 
            onClick={() => navigate('/projects')}
            className="mt-4 text-primary-600 hover:text-primary-700"
          >
            Back to Projects
          </button>
        </div>
      </div>
    )
  }


  const StatusConfig = statusConfig[project.status as keyof typeof statusConfig] || statusConfig.planning

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/projects')}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
                <p className="text-gray-600">Project Details & Documents</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowDocumentUpload(true)}
                className="btn-primary flex items-center"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload Document
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Project Information Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-8">
              <div className="flex items-center space-x-3 mb-4">
                <div className={`p-3 rounded-lg ${StatusConfig.bg}`}>
                  <StatusConfig.icon className={`h-6 w-6 ${StatusConfig.color}`} />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">{project.name}</h2>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${StatusConfig.bg} ${StatusConfig.color}`}>
                    {StatusConfig.label}
                  </span>
                </div>
              </div>

              <p className="text-gray-600 mb-6">{project.description}</p>

              {/* Project Stats */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-primary-600">{project.documents_count}</div>
                  <div className="text-sm text-gray-600">Documents</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-primary-600">{project.entities_count}</div>
                  <div className="text-sm text-gray-600">Entities</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-primary-600">{project.members_count}</div>
                  <div className="text-sm text-gray-600">Members</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-primary-600">{project.verified_entities_count}</div>
                  <div className="text-sm text-gray-600">Verified</div>
                </div>
              </div>

              {/* Project Details */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Research Area</h3>
                  <p className="text-sm text-gray-600">{project.research_area}</p>
                </div>
                
                {project.objectives && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Objectives</h3>
                    <p className="text-sm text-gray-600">{project.objectives}</p>
                  </div>
                )}

                {project.tags && project.tags.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Tags</h3>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {project.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h3 className="text-sm font-medium text-gray-900">Created</h3>
                  <p className="text-sm text-gray-600">{formatDate(project.created_at)}</p>
                </div>

                {project.updated_at && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Last Updated</h3>
                    <p className="text-sm text-gray-600">{formatDate(project.updated_at)}</p>
                  </div>
                )}
              </div>

              {/* Project Actions */}
              <div className="mt-6 space-y-3">
                {project.status === 'planning' && (
                  <button
                    onClick={handleStartProject}
                    className="w-full btn-primary flex items-center justify-center"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start Project
                  </button>
                )}
                
                {project.status === 'active' && (
                  <button
                    onClick={handleCompleteProject}
                    className="w-full btn-secondary flex items-center justify-center"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Complete Project
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Documents Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Project Documents</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {documents.length} document{documents.length !== 1 ? 's' : ''} in this project
                </p>
              </div>

              {documents.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
                  <p className="text-gray-600 mb-4">This project doesn't have any documents yet.</p>
                  <button
                    onClick={() => setShowDocumentUpload(true)}
                    className="btn-primary"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Upload First Document
                  </button>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {documents.map((document) => (
                    <motion.div
                      key={document.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-6 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-3">
                            <FileText className="h-5 w-5 text-primary-600" />
                            <h4 className="text-lg font-semibold text-gray-900">{document.title}</h4>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              processingStatusConfig[document.processing_status as keyof typeof processingStatusConfig]?.bg || 'bg-gray-100'
                            } ${
                              processingStatusConfig[document.processing_status as keyof typeof processingStatusConfig]?.color || 'text-gray-800'
                            }`}>
                              {processingStatusConfig[document.processing_status as keyof typeof processingStatusConfig]?.label || document.processing_status}
                            </span>
                          </div>
                          
                          {document.description && (
                            <p className="text-gray-600 mb-4">{document.description}</p>
                          )}

                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <Calendar className="h-4 w-4" />
                              <span>{formatDate(document.created_at)}</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <User className="h-4 w-4" />
                              <span>{document.created_by.full_name || document.created_by.username}</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <FileText className="h-4 w-4" />
                              <span>{getLanguageLabel(document.language)}</span>
                            </div>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <Tag className="h-4 w-4" />
                              <span>{document.total_entities} entities</span>
                            </div>
                          </div>

                          {document.tags && document.tags.length > 0 && (
                            <div className="flex flex-wrap gap-2 mb-4">
                              {document.tags.map((tag, index) => (
                                <span
                                  key={index}
                                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}

                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>{document.word_count} words</span>
                            <span>{document.line_count} lines</span>
                            {document.verified_entities > 0 && (
                              <span className="text-green-600">{document.verified_entities} verified entities</span>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => {/* TODO: Implement document detail view */}}
                            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Eye className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => setShowDeleteConfirm(document)}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete Document"
                          >
                            <Trash2 className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Document Upload Modal */}
      {showDocumentUpload && (
        <DocumentUpload
          projectSlug={project.slug}
          projectName={project.name}
          isOpen={showDocumentUpload}
          onClose={() => setShowDocumentUpload(false)}
          onDocumentUploaded={() => {
            fetchDocuments()
            fetchProject()
            setShowDocumentUpload(false)
          }}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Delete Document</h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete "{showDeleteConfirm.title}"? 
                This will also remove all named entities associated with this document.
              </p>
              <div className="flex justify-center space-x-3">
                <button
                  onClick={() => setShowDeleteConfirm(null)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDeleteDocument(showDeleteConfirm)}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
