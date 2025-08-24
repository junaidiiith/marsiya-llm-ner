import { useState } from 'react'
import { 
  Search, 
  Tag, 
  MapPin, 
  Building, 
  User, 
  Calendar,
  DollarSign,
  Hash,
  Download,
  Share2
} from 'lucide-react'
import { motion } from 'framer-motion'
import { formatDate } from '@/lib/utils'

interface Entity {
  id: number
  text: string
  type: string
  confidence: number
  document: string
  project: string
  extractedAt: string
  context: string
  metadata: Record<string, string>
}

const mockEntities: Entity[] = [
  {
    id: 1,
    text: 'John Smith',
    type: 'PERSON',
    confidence: 0.95,
    document: 'Annual Report 2024.pdf',
    project: 'Financial Analysis Q1',
    extractedAt: '2024-01-15T10:30:00Z',
    context: '...CEO John Smith announced record profits...',
    metadata: { position: 'CEO', company: 'TechCorp Inc.' }
  },
  {
    id: 2,
    text: 'New York',
    type: 'LOCATION',
    confidence: 0.92,
    document: 'Annual Report 2024.pdf',
    project: 'Financial Analysis Q1',
    extractedAt: '2024-01-15T10:30:00Z',
    context: '...headquartered in New York with offices...',
    metadata: { country: 'USA', state: 'NY' }
  },
  {
    id: 3,
    text: 'TechCorp Inc.',
    type: 'ORGANIZATION',
    confidence: 0.98,
    document: 'Annual Report 2024.pdf',
    project: 'Financial Analysis Q1',
    extractedAt: '2024-01-15T10:30:00Z',
    context: '...TechCorp Inc. reported strong Q4 results...',
    metadata: { industry: 'Technology', founded: '2010' }
  },
  {
    id: 4,
    text: '$2.5 billion',
    type: 'MONEY',
    confidence: 0.89,
    document: 'Annual Report 2024.pdf',
    project: 'Financial Analysis Q1',
    extractedAt: '2024-01-15T10:30:00Z',
    context: '...revenue reached $2.5 billion this quarter...',
    metadata: { currency: 'USD', period: 'Q4 2024' }
  },
  {
    id: 5,
    text: '2024-01-15',
    type: 'DATE',
    confidence: 0.97,
    document: 'Technical Specifications.docx',
    project: 'Product Development',
    extractedAt: '2024-01-15T09:15:00Z',
    context: '...project deadline set for 2024-01-15...',
    metadata: { format: 'ISO', significance: 'deadline' }
  }
]

const entityTypes = [
  { value: 'all', label: 'All Types', icon: Tag, color: 'text-gray-600' },
  { value: 'PERSON', label: 'Person', icon: User, color: 'text-blue-600' },
  { value: 'ORGANIZATION', label: 'Organization', icon: Building, color: 'text-green-600' },
  { value: 'LOCATION', label: 'Location', icon: MapPin, color: 'text-purple-600' },
  { value: 'DATE', label: 'Date', icon: Calendar, color: 'text-orange-600' },
  { value: 'MONEY', label: 'Money', icon: DollarSign, color: 'text-emerald-600' },
  { value: 'QUANTITY', label: 'Quantity', icon: Hash, color: 'text-red-600' }
]

export default function Entities() {
  const [entities, setEntities] = useState(mockEntities)
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [confidenceFilter, setConfidenceFilter] = useState('all')
  const [selectedEntity, setSelectedEntity] = useState<any>(null)

  const filteredEntities = entities.filter(entity => {
    const matchesSearch = entity.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entity.context.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || entity.type === typeFilter
    const matchesConfidence = confidenceFilter === 'all' || 
      (confidenceFilter === 'high' && entity.confidence >= 0.9) ||
      (confidenceFilter === 'medium' && entity.confidence >= 0.7 && entity.confidence < 0.9) ||
      (confidenceFilter === 'low' && entity.confidence < 0.7)
    
    return matchesSearch && matchesType && matchesConfidence
  })

  const getEntityTypeIcon = (type: string) => {
    const entityType = entityTypes.find(t => t.value === type)
    return entityType ? entityType.icon : Tag
  }

  const getEntityTypeColor = (type: string) => {
    const entityType = entityTypes.find(t => t.value === type)
    return entityType ? entityType.color : 'text-gray-600'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600'
    if (confidence >= 0.7) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Entities</h1>
          <p className="text-gray-600">Browse and manage extracted named entities from your documents.</p>
        </div>
        <div className="flex space-x-3">
          <button className="btn-secondary flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button className="btn-primary flex items-center">
            <Share2 className="w-4 h-4 mr-2" />
            Share Results
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search entities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="input-field"
        >
          {entityTypes.map(type => (
            <option key={type.value} value={type.value}>{type.label}</option>
          ))}
        </select>
        <select
          value={confidenceFilter}
          onChange={(e) => setConfidenceFilter(e.target.value)}
          className="input-field"
        >
          <option value="all">All Confidence</option>
          <option value="high">High (≥90%)</option>
          <option value="medium">Medium (70-89%)</option>
          <option value="low">Low (&lt;70%)</option>
        </select>
        <div className="text-sm text-gray-500 flex items-center justify-center">
          {filteredEntities.length} entities found
        </div>
      </div>

      {/* Entities Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredEntities.map((entity, index) => {
          const IconComponent = getEntityTypeIcon(entity.type)
          const typeColor = getEntityTypeColor(entity.type)
          const confidenceColor = getConfidenceColor(entity.confidence)
          
          return (
            <motion.div
              key={entity.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedEntity(entity)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className={`w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center`}>
                    <IconComponent className={`w-4 h-4 ${typeColor}`} />
                  </div>
                  <span className="text-sm font-medium text-gray-900">{entity.text}</span>
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${confidenceColor} bg-opacity-10`}>
                  {Math.round(entity.confidence * 100)}%
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Tag className="w-3 h-3 text-gray-400" />
                  <span className="text-xs text-gray-600">{entity.type}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Document:</span>
                  <span className="text-xs text-gray-700 truncate">{entity.document}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Project:</span>
                  <span className="text-xs text-gray-700 truncate">{entity.project}</span>
                </div>
                <div className="text-xs text-gray-500">
                  Extracted: {formatDate(entity.extractedAt)}
                </div>
              </div>
              
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-600 line-clamp-2">
                  {entity.context}
                </p>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Entity Detail Modal */}
      {selectedEntity && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Entity Details</h3>
                <button
                  onClick={() => setSelectedEntity(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-lg bg-primary-100 flex items-center justify-center">
                    {(() => {
                      const IconComponent = getEntityTypeIcon(selectedEntity.type)
                      return <IconComponent className="w-6 h-6 text-primary-600" />
                    })()}
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold text-gray-900">{selectedEntity.text}</h4>
                    <p className="text-sm text-gray-600">{selectedEntity.type}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Confidence</label>
                    <p className="text-sm text-gray-900">{Math.round(selectedEntity.confidence * 100)}%</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Document</label>
                    <p className="text-sm text-gray-900">{selectedEntity.document}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Project</label>
                    <p className="text-sm text-gray-900">{selectedEntity.project}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Extracted</label>
                    <p className="text-sm text-gray-900">{formatDate(selectedEntity.extractedAt)}</p>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">Context</label>
                  <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg mt-1">
                    {selectedEntity.context}
                  </p>
                </div>
                
                {Object.keys(selectedEntity.metadata).length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Metadata</label>
                    <div className="bg-gray-50 p-3 rounded-lg mt-1">
                      {Object.entries(selectedEntity.metadata).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-gray-600">{key}:</span>
                          <span className="text-gray-900">{String(value)}</span>
                        </div>
                      ))}
                    </div>
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
