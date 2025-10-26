import React, { useEffect, useState, useRef } from 'react'
import { Streamlit } from 'streamlit-component-lib'

type Props = {
  args: {
    image_b64?: string
    box?: { x: number; y: number; w: number; h: number } | null
    minSize?: number
  }
}

type Rect = { x: number; y: number; w: number; h: number }

const App: React.FC<Props> = (props) => {
  const { image_b64, box, minSize = 32 } = props.args || {}
  const [rect, setRect] = useState<Rect>(box || { x: 50, y: 50, w: 200, h: 200 })
  const [isDragging, setIsDragging] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const containerRef = useRef<HTMLDivElement>(null)
  const [imgSize, setImgSize] = useState({ width: 0, height: 0 })

  // Update frame height when content changes
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [rect, image_b64])

  // Handle image load to get dimensions
  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget
    setImgSize({ width: img.clientWidth, height: img.clientHeight })
    
    // Initialize rect if needed
    if (!box) {
      const size = Math.min(200, img.clientWidth * 0.5, img.clientHeight * 0.5)
      setRect({
        x: (img.clientWidth - size) / 2,
        y: (img.clientHeight - size) / 2,
        w: size,
        h: size,
      })
    }
  }

  // Mouse down on rectangle (start drag)
  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).classList.contains('resize-handle')) {
      setIsResizing(true)
    } else {
      setIsDragging(true)
    }
    setDragStart({ x: e.clientX, y: e.clientY })
    e.preventDefault()
  }

  // Mouse move (drag or resize)
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging && !isResizing) return

    const dx = e.clientX - dragStart.x
    const dy = e.clientY - dragStart.y

    if (isDragging) {
      // Move rectangle
      const newX = Math.max(0, Math.min(imgSize.width - rect.w, rect.x + dx))
      const newY = Math.max(0, Math.min(imgSize.height - rect.h, rect.y + dy))
      setRect({ ...rect, x: newX, y: newY })
      setDragStart({ x: e.clientX, y: e.clientY })
    } else if (isResizing) {
      // Resize rectangle
      const newW = Math.max(minSize, Math.min(imgSize.width - rect.x, rect.w + dx))
      const newH = Math.max(minSize, Math.min(imgSize.height - rect.y, rect.h + dy))
      setRect({ ...rect, w: newW, h: newH })
      setDragStart({ x: e.clientX, y: e.clientY })
    }
  }

  // Mouse up (stop drag/resize)
  const handleMouseUp = () => {
    setIsDragging(false)
    setIsResizing(false)
  }

  const onConfirm = () => {
    Streamlit.setComponentValue({ rect })
  }

  const onReset = () => {
    const size = Math.min(200, imgSize.width * 0.5, imgSize.height * 0.5)
    setRect({
      x: (imgSize.width - size) / 2,
      y: (imgSize.height - size) / 2,
      w: size,
      h: size,
    })
  }

  return (
    <div style={{ width: '100%', padding: '8px', fontFamily: 'sans-serif' }}>
      {image_b64 ? (
        <div
          ref={containerRef}
          style={{ position: 'relative', width: '100%', maxWidth: '800px', userSelect: 'none' }}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <img
            src={`data:image/png;base64,${image_b64}`}
            style={{ width: '100%', display: 'block', pointerEvents: 'none' }}
            onLoad={handleImageLoad}
            alt="Crop target"
          />
          
          {/* Crop rectangle overlay */}
          <div
            style={{
              position: 'absolute',
              left: `${rect.x}px`,
              top: `${rect.y}px`,
              width: `${rect.w}px`,
              height: `${rect.h}px`,
              border: '2px dashed #00d4ff',
              boxShadow: '0 0 0 9999px rgba(0,0,0,0.4)',
              cursor: isDragging ? 'grabbing' : 'grab',
              boxSizing: 'border-box',
            }}
            onMouseDown={handleMouseDown}
          >
            {/* Resize handle (bottom-right corner) */}
            <div
              className="resize-handle"
              style={{
                position: 'absolute',
                right: '-6px',
                bottom: '-6px',
                width: '12px',
                height: '12px',
                background: '#00d4ff',
                border: '2px solid white',
                borderRadius: '50%',
                cursor: 'nwse-resize',
                boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
              }}
            />
            
            {/* Info label */}
            <div
              style={{
                position: 'absolute',
                top: '-24px',
                left: '0',
                background: 'rgba(0,212,255,0.9)',
                color: 'white',
                padding: '2px 8px',
                borderRadius: '3px',
                fontSize: '12px',
                fontWeight: 'bold',
                whiteSpace: 'nowrap',
                pointerEvents: 'none',
              }}
            >
              {Math.round(rect.w)} × {Math.round(rect.h)}
            </div>
          </div>
        </div>
      ) : (
        <div style={{ padding: '20px', color: '#999', textAlign: 'center' }}>
          No image provided
        </div>
      )}

      <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
        <button
          onClick={onConfirm}
          style={{
            padding: '8px 16px',
            background: '#00d4ff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '14px',
          }}
        >
          ✓ Confirm
        </button>
        <button
          onClick={onReset}
          style={{
            padding: '8px 16px',
            background: '#666',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          ↻ Reset
        </button>
      </div>

      <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
        Drag to move • Drag corner to resize • Click Confirm to apply
      </div>
    </div>
  )
}

export default App
