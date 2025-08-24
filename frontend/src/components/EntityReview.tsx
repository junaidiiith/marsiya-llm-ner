import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Check, 
  Edit, 
  Plus, 
  Trash2, 
  Eye, 
  EyeOff,
  ChevronLeft,
  ChevronRight,
  Globe
} from 'lucide-react'

interface Entity {
  id: number
  text: string
  type: string
  start: number
  end: number
  confidence: number
  verified: boolean
  context: string
  english_translation?: string
}

interface EntityReviewProps {
  documentText: string
  entities: Entity[]
  onEntityUpdate: (entityId: number, updates: Partial<Entity>) => void
  onEntityDelete: (entityId: number) => void
  onEntityAdd: (entity: Omit<Entity, 'id'>) => void
}

const entityTypeColors = {
  PERSON: 'bg-blue-100 text-blue-800 border-blue-200',
  ORGANIZATION: 'bg-green-100 text-green-800 border-green-200',
  LOCATION: 'bg-purple-100 text-purple-800 border-purple-200',
  DATE: 'bg-orange-100 text-orange-800 border-orange-200',
  TIME: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  MONEY: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  QUANTITY: 'bg-red-100 text-red-800 border-red-200',
  DESIGNATION: 'bg-indigo-100 text-indigo-800 border-indigo-200',
  EVENT: 'bg-pink-100 text-pink-800 border-pink-200',
  TECHNOLOGY: 'bg-cyan-100 text-cyan-800 border-cyan-200',
}

export default function EntityReview({ 
  documentText, 
  entities, 
  onEntityUpdate, 
  onEntityDelete, 
  onEntityAdd 
}: EntityReviewProps) {
  const [currentLine, setCurrentLine] = useState(0)
  const [showEnglish, setShowEnglish] = useState(false)
  const [editingEntity, setEditingEntity] = useState<Entity | null>(null)
  const [newEntity, setNewEntity] = useState({
    text: '',
    type: 'PERSON',
    start: 0,
    end: 0,
    confidence: 0.9,
    verified: false,
    context: ''
  })

  // Split text into lines for line-by-line review
  const lines = documentText.split('\n').filter(line => line.trim())

  const getEntitiesInLine = (lineIndex: number) => {
    const lineStart = lines.slice(0, lineIndex).join('\n').length + (lineIndex > 0 ? 1 : 0)
    const lineEnd = lineStart + lines[lineIndex].length
    
    return entities.filter(entity => 
      entity.start >= lineStart && entity.end <= lineEnd
    )
  }

  const highlightText = (text: string, lineEntities: Entity[]) => {
    if (lineEntities.length === 0) return text

    let highlightedText = text
    const sortedEntities = [...lineEntities].sort((a, b) => b.start - a.start)

    sortedEntities.forEach(entity => {
      const entityText = entity.text
      const entityType = entity.type as keyof typeof entityTypeColors
      const colorClass = entityTypeColors[entityType] || 'bg-gray-100 text-gray-800 border-gray-200'
      
      const regex = new RegExp(`(${entityText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
      highlightedText = highlightedText.replace(regex, (match) => {
        return `<span class="inline-block px-1 py-0.5 rounded border text-sm font-medium ${colorClass} cursor-pointer hover:opacity-80" data-entity-id="${entity.id}">${match}</span>`
      })
    })

    return highlightedText
  }

  const handleEntityClick = (entityId: number) => {
    const entity = entities.find(e => e.id === entityId)
    if (entity) {
      setEditingEntity(entity)
    }
  }

  const handleVerifyEntity = (entityId: number, verified: boolean) => {
    onEntityUpdate(entityId, { verified })
  }

  const handleSaveEdit = () => {
    if (editingEntity) {
      onEntityUpdate(editingEntity.id, editingEntity)
      setEditingEntity(null)
    }
  }

  const handleAddEntity = () => {
    if (newEntity.text.trim()) {
      onEntityAdd({
        ...newEntity,
        start: currentLine * 100, // Simplified position calculation
        end: currentLine * 100 + newEntity.text.length,
        context: lines[currentLine]
      })
      setNewEntity({
        text: '',
        type: 'PERSON',
        start: 0,
        end: 0,
        confidence: 0.9,
        verified: false,
        context: ''
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setCurrentLine(Math.max(0, currentLine - 1))}
            disabled={currentLine === 0}
            className="btn-secondary disabled:opacity-50"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>
          
          <span className="text-sm text-gray-600">
            Line {currentLine + 1} of {lines.length}
          </span>
          
          <button
            onClick={() => setCurrentLine(Math.min(lines.length - 1, currentLine + 1))}
            disabled={currentLine === lines.length - 1}
            className="btn-secondary disabled:opacity-50"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowEnglish(!showEnglish)}
            className="btn-secondary flex items-center"
          >
            {showEnglish ? <EyeOff className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
            {showEnglish ? 'Hide' : 'Show'} English
          </button>
        </div>
      </div>

      {/* Current Line Review */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Line {currentLine + 1}</h3>
        
        <div className="space-y-4">
          {/* Original Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Original Text</label>
            <div 
              className="p-3 bg-gray-50 rounded-lg border"
              dangerouslySetInnerHTML={{ 
                __html: highlightText(lines[currentLine], getEntitiesInLine(currentLine)) 
              }}
              onClick={(e) => {
                const target = e.target as HTMLElement
                if (target.dataset.entityId) {
                  handleEntityClick(parseInt(target.dataset.entityId))
                }
              }}
            />
          </div>

          {/* English Translation */}
          {showEnglish && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                English Translation
              </label>
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <Globe className="w-4 h-4 inline mr-2 text-blue-600" />
                {lines[currentLine]} {/* This would be replaced with actual translation */}
              </div>
            </div>
          )}

          {/* Add New Entity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Add New Entity</label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newEntity.text}
                onChange={(e) => setNewEntity(prev => ({ ...prev, text: e.target.value }))}
                placeholder="Enter entity text"
                className="input-field flex-1"
              />
              <select
                value={newEntity.type}
                onChange={(e) => setNewEntity(prev => ({ ...prev, type: e.target.value }))}
                className="input-field w-32"
              >
                {Object.keys(entityTypeColors).map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <button
                onClick={handleAddEntity}
                className="btn-primary flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Entities in Current Line */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Entities in Line {currentLine + 1} ({getEntitiesInLine(currentLine).length})
        </h3>
        
        {getEntitiesInLine(currentLine).length === 0 ? (
          <p className="text-gray-500 text-center py-4">No entities found in this line</p>
        ) : (
          <div className="space-y-3">
            {getEntitiesInLine(currentLine).map(entity => (
              <motion.div
                key={entity.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      entityTypeColors[entity.type as keyof typeof entityTypeColors]
                    }`}>
                      {entity.type}
                    </span>
                    <span className="font-medium text-gray-900">{entity.text}</span>
                    <span className="text-sm text-gray-500">
                      Confidence: {Math.round(entity.confidence * 100)}%
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleVerifyEntity(entity.id, !entity.verified)}
                      className={`p-1 rounded ${
                        entity.verified 
                          ? 'text-green-600 hover:text-green-700' 
                          : 'text-gray-400 hover:text-gray-600'
                      }`}
                    >
                      <Check className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={() => setEditingEntity(entity)}
                      className="text-blue-600 hover:text-blue-700 p-1 rounded"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={() => onEntityDelete(entity.id)}
                      className="text-red-600 hover:text-red-700 p-1 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="mt-2 text-sm text-gray-600">
                  Context: {entity.context}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Entity Modal */}
      {editingEntity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Edit Entity</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Text</label>
                <input
                  type="text"
                  value={editingEntity.text}
                  onChange={(e) => setEditingEntity(prev => prev ? { ...prev, text: e.target.value } : null)}
                  className="input-field"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={editingEntity.type}
                  onChange={(e) => setEditingEntity(prev => prev ? { ...prev, type: e.target.value } : null)}
                  className="input-field"
                >
                  {Object.keys(entityTypeColors).map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confidence</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={editingEntity.confidence}
                  onChange={(e) => setEditingEntity(prev => prev ? { ...prev, confidence: parseFloat(e.target.value) } : null)}
                  className="w-full"
                />
                <span className="text-sm text-gray-500">{Math.round(editingEntity.confidence * 100)}%</span>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setEditingEntity(null)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="btn-primary"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
