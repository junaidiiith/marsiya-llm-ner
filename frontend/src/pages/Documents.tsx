import { useState } from 'react'
import { 
  Upload, 
  Search, 
  FileText, 
  Download,
  Trash2,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { formatDate, formatFileSize } from '@/lib/utils'

interface Document {
  id: number
  name: string
  size: number
  type: string
  status: string
  uploadedAt: string
  entities: number
  project: string
}

const mockDocuments: Document[] = [
  {
    id: 1,
    name: 'Annual Report 2024.pdf',
    size: 2048576,
    type: 'PDF',
    status: 'processed',
    uploadedAt: '2024-01-15T10:30:00Z',
    entities: 45,
    project: 'Financial Analysis Q1'
  },
  {
    id: 2,
    name: 'Technical Specifications.docx',
    size: 1048576,
    type: 'DOCX',
    status: 'processing',
    uploadedAt: '2024-01-15T09:15:00Z',
    entities: 0,
    project: 'Product Development'
  },
  {
    id: 3,
    name: 'Q4 Financial Results.xlsx',
    size: 512000,
    type: 'XLSX',
    status: 'error',
    uploadedAt: '2024-01-14T16:45:00Z',
    entities: 0,
    project: 'Financial Analysis Q1'
  },
  {
    id: 4,
    name: 'Customer Feedback Survey.pdf',
    size: 1536000,
    type: 'PDF',
    status: 'processed',
    uploadedAt: '2024-01-14T14:20:00Z',
    entities: 23,
    project: 'Customer Insights'
  }
]

const statusConfig = {
  processed: { label: 'Processed', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
  processing: { label: 'Processing', icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  error: { label: 'Error', icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-100' },
  pending: { label: 'Pending', icon: Clock, color: 'text-gray-600', bg: 'bg-gray-100' }
}

export default function Documents() {
  const [documents, setDocuments] = useState(mockDocuments)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [showUploadModal, setShowUploadModal] = useState(false)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.txt']
    },
    onDrop: (acceptedFiles) => {
      // Handle file upload
      console.log('Files dropped:', acceptedFiles)
      setShowUploadModal(false)
    }
  })

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleDelete = (id: number) => {
    setDocuments(docs => docs.filter(doc => doc.id !== id))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600">Manage and process your documents for entity extraction.</p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="btn-primary flex items-center"
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload Document
        </button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search documents..."
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
          <option value="processed">Processed</option>
          <option value="processing">Processing</option>
          <option value="error">Error</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      {/* Documents List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Documents ({filteredDocuments.length})
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Project
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entities
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredDocuments.map((doc) => {
                const status = statusConfig[doc.status as keyof typeof statusConfig]
                return (
                  <motion.tr
                    key={doc.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-lg bg-primary-100 flex items-center justify-center">
                            <FileText className="h-6 w-6 text-primary-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{doc.name}</div>
                          <div className="text-sm text-gray-500">
                            {formatFileSize(doc.size)} • {doc.type}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.bg} ${status.color}`}>
                        <status.icon className="w-3 h-3 mr-1" />
                        {status.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {doc.project}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {doc.entities > 0 ? doc.entities : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(doc.uploadedAt)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button className="text-primary-600 hover:text-primary-900">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-900">
                          <Download className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(doc.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Document</h3>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-400 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-600">
                  {isDragActive
                    ? 'Drop the files here...'
                    : 'Drag & drop files here, or click to select files'}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  PDF, DOCX, XLSX, TXT up to 10MB
                </p>
              </div>

              <div className="mt-4 flex justify-end space-x-3">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button className="btn-primary">
                  Upload
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
