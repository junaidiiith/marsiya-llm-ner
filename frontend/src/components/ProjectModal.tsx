import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Save, FolderOpen } from 'lucide-react'
import { projectsAPI } from '@/services/api'
import toast from 'react-hot-toast'

const projectSchema = z.object({
  name: z.string().min(3, 'Project name must be at least 3 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  entityTypes: z.array(z.string()).min(1, 'Select at least one entity type'),
  llmModel: z.string().min(1, 'Please select an LLM model'),
  customPrompt: z.string().optional(),
})

type ProjectFormData = z.infer<typeof projectSchema>

interface ProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onProjectCreated: () => void
}

const entityTypeOptions = [
  { value: 'PERSON', label: 'Person', color: 'text-blue-600' },
  { value: 'ORGANIZATION', label: 'Organization', color: 'text-green-600' },
  { value: 'LOCATION', label: 'Location', color: 'text-purple-600' },
  { value: 'DATE', label: 'Date', color: 'text-orange-600' },
  { value: 'TIME', label: 'Time', color: 'text-yellow-600' },
  { value: 'MONEY', label: 'Money', color: 'text-emerald-600' },
  { value: 'QUANTITY', label: 'Quantity', color: 'text-red-600' },
  { value: 'DESIGNATION', label: 'Designation', color: 'text-indigo-600' },
  { value: 'EVENT', label: 'Event', color: 'text-pink-600' },
  { value: 'TECHNOLOGY', label: 'Technology', color: 'text-cyan-600' },
]

const llmModelOptions = [
  { value: 'gpt-4o', label: 'OpenAI GPT-4o', description: 'Latest GPT-4 model with improved performance' },
  { value: 'gpt-4-turbo', label: 'OpenAI GPT-4 Turbo', description: 'Fast and efficient GPT-4 variant' },
  { value: 'claude-3-opus', label: 'Anthropic Claude 3 Opus', description: 'Most capable Claude model' },
  { value: 'claude-3-sonnet', label: 'Anthropic Claude 3 Sonnet', description: 'Balanced Claude model' },
  { value: 'claude-3-haiku', label: 'Anthropic Claude 3 Haiku', description: 'Fastest Claude model' },
]

const predefinedPrompts = [
  {
    id: 'urdu-marsiya',
    name: 'Urdu Marsiya Analysis',
    prompt: 'Extract named entities from Urdu Marsiya poetry. Focus on historical figures, locations, dates, and religious references. Provide English translations for context.',
    entityTypes: ['PERSON', 'LOCATION', 'DATE', 'ORGANIZATION']
  },
  {
    id: 'financial-document',
    name: 'Financial Document Analysis',
    prompt: 'Extract financial entities including amounts, dates, company names, and transaction details from financial documents.',
    entityTypes: ['MONEY', 'DATE', 'ORGANIZATION', 'QUANTITY']
  },
  {
    id: 'legal-contract',
    name: 'Legal Contract Analysis',
    prompt: 'Extract legal entities including parties, dates, amounts, and legal terms from contracts and legal documents.',
    entityTypes: ['PERSON', 'ORGANIZATION', 'DATE', 'MONEY', 'EVENT']
  },
  {
    id: 'technical-spec',
    name: 'Technical Specification',
    prompt: 'Extract technical entities including technologies, specifications, measurements, and technical terms.',
    entityTypes: ['TECHNOLOGY', 'QUANTITY', 'ORGANIZATION', 'DESIGNATION']
  }
]

export default function ProjectModal({ isOpen, onClose, onProjectCreated }: ProjectModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [selectedPrompt, setSelectedPrompt] = useState<string>('')
  const [useCustomPrompt, setUseCustomPrompt] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      entityTypes: [],
      llmModel: 'gpt-4o'
    }
  })

  const watchedEntityTypes = watch('entityTypes')

  const handlePromptSelect = (promptId: string) => {
    const prompt = predefinedPrompts.find(p => p.id === promptId)
    if (prompt) {
      setValue('entityTypes', prompt.entityTypes)
      setValue('customPrompt', prompt.prompt)
      setSelectedPrompt(promptId)
      setUseCustomPrompt(false)
    }
  }

  const handleEntityTypeToggle = (entityType: string) => {
    const currentTypes = watch('entityTypes')
    if (currentTypes.includes(entityType)) {
      setValue('entityTypes', currentTypes.filter(type => type !== entityType))
    } else {
      setValue('entityTypes', [...currentTypes, entityType])
    }
  }

  const onSubmit = async (data: ProjectFormData) => {
    try {
      setIsLoading(true)
      
      // Create project with fields that match the backend model
      await projectsAPI.create({
        name: data.name,
        description: data.description,
        research_area: data.entityTypes.join(', '), // Use research_area instead of entityTypes
        objectives: data.entityTypes, // Store entity types in objectives field
        tags: [data.llmModel], // Store LLM model in tags
        status: 'planning'
      })

      toast.success('Project created successfully!')
      reset()
      onProjectCreated()
      onClose()
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to create project. Please try again.'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    reset()
    setSelectedPrompt('')
    setUseCustomPrompt(false)
    onClose()
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <FolderOpen className="w-5 h-5 text-primary-600" />
                  </div>
                  <h2 className="text-xl font-semibold text-gray-900">Create New Project</h2>
                </div>
                <button
                  onClick={handleClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project Name *
                  </label>
                  <input
                    {...register('name')}
                    type="text"
                    className="input-field"
                    placeholder="Enter project name"
                  />
                  {errors.name && (
                    <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    LLM Model *
                  </label>
                  <select {...register('llmModel')} className="input-field">
                    {llmModelOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  {errors.llmModel && (
                    <p className="text-red-600 text-sm mt-1">{errors.llmModel.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  {...register('description')}
                  rows={3}
                  className="input-field"
                  placeholder="Describe your project and what you want to achieve"
                />
                {errors.description && (
                  <p className="text-red-600 text-sm mt-1">{errors.description.message}</p>
                )}
              </div>

              {/* Predefined Prompts */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Choose a Predefined Prompt (Optional)
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {predefinedPrompts.map(prompt => (
                    <button
                      key={prompt.id}
                      type="button"
                      onClick={() => handlePromptSelect(prompt.id)}
                      className={`p-3 border rounded-lg text-left transition-colors ${
                        selectedPrompt === prompt.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <h4 className="font-medium text-gray-900">{prompt.name}</h4>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {prompt.prompt}
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Entity Types */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Entity Types to Extract *
                </label>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  {entityTypeOptions.map(entityType => (
                    <button
                      key={entityType.value}
                      type="button"
                      onClick={() => handleEntityTypeToggle(entityType.value)}
                      className={`p-2 border rounded-lg text-sm font-medium transition-colors ${
                        watchedEntityTypes.includes(entityType.value)
                          ? 'border-primary-500 bg-primary-100 text-primary-800'
                          : 'border-gray-200 hover:border-gray-300 text-gray-700'
                      }`}
                    >
                      {entityType.label}
                    </button>
                  ))}
                </div>
                {errors.entityTypes && (
                  <p className="text-red-600 text-sm mt-1">{errors.entityTypes.message}</p>
                )}
              </div>

              {/* Custom Prompt */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <input
                    type="checkbox"
                    id="useCustomPrompt"
                    checked={useCustomPrompt}
                    onChange={(e) => setUseCustomPrompt(e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <label htmlFor="useCustomPrompt" className="text-sm font-medium text-gray-700">
                    Use Custom Prompt
                  </label>
                </div>
                
                {useCustomPrompt && (
                  <textarea
                    {...register('customPrompt')}
                    rows={4}
                    className="input-field"
                    placeholder="Enter your custom prompt for entity extraction..."
                  />
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={handleClose}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary flex items-center"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  Create Project
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
