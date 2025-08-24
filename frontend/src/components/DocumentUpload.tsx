import { useState, useEffect } from 'react'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import { documentsAPI, projectsAPI } from '@/services/api'
import toast from 'react-hot-toast'

interface DocumentUploadProps {
  projectSlug: string
  projectName: string
  isOpen: boolean
  onClose: () => void
  onDocumentUploaded: () => void
}

interface UploadFormData {
  title: string
  description: string
  project: number
  file: File | null
  content: string
  language: string
  tags: string[]
}

export default function DocumentUpload({ 
  projectSlug, 
  projectName, 
  isOpen, 
  onClose, 
  onDocumentUploaded 
}: DocumentUploadProps) {
  const [formData, setFormData] = useState<UploadFormData>({
    title: '',
    description: '',
    project: 0,
    file: null,
    content: '',
    language: 'ur',
    tags: []
  })
  const [isUploading, setIsUploading] = useState(false)
  const [uploadMethod, setUploadMethod] = useState<'file' | 'content'>('file')
  const [tagInput, setTagInput] = useState('')
  const [projectId, setProjectId] = useState<number | null>(null)
  const [isLoadingProject, setIsLoadingProject] = useState(false)

  // Fetch project ID when component opens
  useEffect(() => {
    if (isOpen && projectSlug) {
      const fetchProjectId = async () => {
        try {
          setIsLoadingProject(true)
          const response = await projectsAPI.get(projectSlug)
          setProjectId(response.data.id)
        } catch (error) {
          console.error('Error fetching project ID:', error)
          toast.error('Failed to fetch project details')
        } finally {
          setIsLoadingProject(false)
        }
      }
      fetchProjectId()
    }
  }, [isOpen, projectSlug])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Read file content for text files
      if (file.type === 'text/plain' || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
        const reader = new FileReader()
        reader.onload = (event) => {
          const content = event.target?.result as string
          setFormData(prev => ({
            ...prev,
            file,
            title: file.name.replace(/\.[^/.]+$/, '') || '',
            content: content
          }))
        }
        reader.readAsText(file)
      } else {
        // For other file types, just set the file
        setFormData(prev => ({
          ...prev,
          file,
          title: file.name.replace(/\.[^/.]+$/, '') || '',
          content: ''
        }))
      }
    }
  }

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      content: e.target.value
    }))
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }))
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!projectId) {
      toast.error('Project details not loaded. Please try again.')
      return
    }
    
    if (!formData.title.trim()) {
      toast.error('Please provide a title for the document')
      return
    }

    if (uploadMethod === 'file' && !formData.file) {
      toast.error('Please select a file to upload')
      return
    }

    if (uploadMethod === 'content' && !formData.content.trim()) {
      toast.error('Please provide content for the document')
      return
    }

    try {
      setIsUploading(true)

      if (uploadMethod === 'file' && formData.file) {
        // For file uploads, we need to create a FormData object
        const formDataObj = new FormData()
        formDataObj.append('title', formData.title)
        formDataObj.append('description', formData.description)
        formDataObj.append('project', projectId.toString())
        formDataObj.append('file', formData.file)
        formDataObj.append('language', formData.language)
        
        // Always include content for file uploads (either from file or empty)
        formDataObj.append('content', formData.content || '')
        
        if (formData.tags.length > 0) {
          // Send tags as a JSON string since the backend expects JSON
          formDataObj.append('tags', JSON.stringify(formData.tags))
        }
        
        // Use the create endpoint with FormData
        await documentsAPI.create(projectId.toString(), formDataObj)
      } else if (uploadMethod === 'content') {
        // Use the create method for text content
        await documentsAPI.create(projectId.toString(), {
          title: formData.title,
          description: formData.description,
          content: formData.content,
          language: formData.language,
          tags: formData.tags,
          project: projectId
        })
      }
      
      toast.success('Document uploaded successfully!')
      onDocumentUploaded()
      onClose()
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        project: 0,
        file: null,
        content: '',
        language: 'ur',
        tags: []
      })
      setTagInput('')
      
    } catch (error: any) {
      console.error('Error uploading document:', error)
      const message = error.response?.data?.detail || 'Failed to upload document'
      toast.error(message)
    } finally {
      setIsUploading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
                      <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Upload Document to {projectName}</h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            {isLoadingProject && (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
                <p className="text-gray-600">Loading project details...</p>
              </div>
            )}
          
                      {!isLoadingProject && (
              <form onSubmit={handleSubmit} className="space-y-6">
            {/* Upload Method Selection */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Upload Method
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="file"
                    checked={uploadMethod === 'file'}
                    onChange={(e) => setUploadMethod(e.target.value as 'file' | 'content')}
                    className="mr-2"
                  />
                  <FileText className="w-4 h-4 mr-1" />
                  Upload File
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="content"
                    checked={uploadMethod === 'content'}
                    onChange={(e) => setUploadMethod(e.target.value as 'file' | 'content')}
                    className="mr-2"
                  />
                  <FileText className="w-4 h-4 mr-1" />
                  Paste Content
                </label>
              </div>
            </div>

            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Document Title *
              </label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="input-field w-full"
                placeholder="Enter document title"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="input-field w-full"
                rows={3}
                placeholder="Enter document description"
              />
            </div>

            {/* File Upload */}
            {uploadMethod === 'file' && (
              <div>
                <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-2">
                  Document File *
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
                  <input
                    type="file"
                    id="file"
                    onChange={handleFileChange}
                    accept=".txt,.doc,.docx,.pdf,.md"
                    className="hidden"
                    required
                  />
                  <label htmlFor="file" className="cursor-pointer">
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="mt-2 text-sm text-gray-600">
                      <span className="font-medium text-primary-600 hover:text-primary-500">
                        Click to upload
                      </span> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      TXT, DOC, DOCX, PDF, MD files up to 10MB
                    </p>
                  </label>
                </div>
                {formData.file && (
                  <div className="mt-2 flex items-center text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    {formData.file.name} ({(formData.file.size / 1024 / 1024).toFixed(2)} MB)
                  </div>
                )}
              </div>
            )}

            {/* Content Input */}
            {uploadMethod === 'content' && (
              <div>
                <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                  Document Content *
                </label>
                <textarea
                  id="content"
                  value={formData.content}
                  onChange={handleContentChange}
                  className="input-field w-full"
                  rows={8}
                  placeholder="Paste or type your document content here..."
                  required
                />
              </div>
            )}

            {/* Language */}
            <div>
              <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-2">
                Language
              </label>
              <select
                id="language"
                value={formData.language}
                onChange={(e) => setFormData(prev => ({ ...prev, language: e.target.value }))}
                className="input-field w-full"
              >
                <option value="ur">Urdu (اردو)</option>
                <option value="en">English</option>
                <option value="ar">Arabic (العربية)</option>
                <option value="fa">Persian (فارسی)</option>
                <option value="hi">Hindi (हिन्दी)</option>
              </select>
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <div className="flex space-x-2 mb-2">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                  className="input-field flex-1"
                  placeholder="Add a tag and press Enter"
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  className="btn-secondary px-4 py-2"
                >
                  Add
                </button>
              </div>
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-1 text-primary-600 hover:text-primary-800"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary"
                disabled={isUploading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center"
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Document
                  </>
                )}
              </button>
            </div>
          </form>
            )}
        </div>
      </div>
    </div>
  )
}
