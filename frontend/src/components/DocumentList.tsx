import { useState, useEffect } from 'react'
import { 
  FileText, 
  Trash2, 
  Eye, 
  Download, 
  Calendar,
  User,
  Tag,
  AlertTriangle
} from 'lucide-react'
import { documentsAPI } from '@/services/api'
import toast from 'react-hot-toast'

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

interface DocumentListProps {
  projectSlug: string
  projectName: string
  isOpen: boolean
  onClose: () => void
  onDocumentDeleted: () => void
}

const statusConfig = {
  pending: { label: 'Pending', bg: 'bg-yellow-100', color: 'text-yellow-800' },
  processing: { label: 'Processing', bg: 'bg-blue-100', color: 'text-blue-800' },
  completed: { label: 'Completed', bg: 'bg-green-100', color: 'text-green-800' },
  failed: { label: 'Failed', bg: 'bg-red-100', color: 'text-red-800' },
  cancelled: { label: 'Cancelled', bg: 'bg-gray-100', color: 'text-gray-800' }
}

export default function DocumentList({ 
  projectSlug, 
  projectName, 
  isOpen, 
  onClose, 
  onDocumentDeleted 
}: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<Document | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchDocuments()
    }
  }, [isOpen, projectSlug])

  const fetchDocuments = async () => {
          try {
        setIsLoading(true)
        const response = await documentsAPI.list(projectSlug)
        // The backend returns a paginated response with {count, results, next, previous}
        const documentsData = response.data.results || response.data
        setDocuments(documentsData)
      } catch (error: any) {
      console.error('Error fetching documents:', error)
      toast.error('Failed to fetch documents')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteDocument = async (document: Document) => {
    try {
      await documentsAPI.delete(projectSlug, document.id)
      toast.success('Document deleted successfully')
      setShowDeleteConfirm(null)
      onDocumentDeleted()
      fetchDocuments() // Refresh the list
    } catch (error: any) {
      console.error('Error deleting document:', error)
      const message = error.response?.data?.detail || 'Failed to delete document'
      toast.error(message)
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

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-6xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">Documents in {projectName}</h3>
              <p className="text-gray-600 mt-1">Manage and view all project documents</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
              <p className="text-gray-600">This project doesn't have any documents yet.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {documents.map((document) => (
                <div
                  key={document.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <FileText className="h-6 w-6 text-primary-600" />
                        <h4 className="text-lg font-semibold text-gray-900">{document.title}</h4>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          statusConfig[document.processing_status as keyof typeof statusConfig]?.bg || 'bg-gray-100'
                        } ${
                          statusConfig[document.processing_status as keyof typeof statusConfig]?.color || 'text-gray-800'
                        }`}>
                          {statusConfig[document.processing_status as keyof typeof statusConfig]?.label || document.processing_status}
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
                        onClick={() => setSelectedDocument(document)}
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
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

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
