import { ReactNode } from 'react'

export function renderMarkdown(text: string): ReactNode[] {
  const lines = text.split('\n')
  const elements: ReactNode[] = []

  lines.forEach((line, i) => {
    if (line.match(/^- /)) {
      const content = line.slice(2)
      elements.push(
        <li key={i} className="ml-4 list-disc text-inherit">
          {parseInline(content)}
        </li>
      )
    } else if (line.trim() === '') {
      elements.push(<br key={i} />)
    } else {
      elements.push(
        <span key={i}>
          {parseInline(line)}
          {i < lines.length - 1 && <br />}
        </span>
      )
    }
  })

  return elements
}

function parseInline(text: string): ReactNode[] {
  const parts: ReactNode[] = []
  const regex = /\*\*(.+?)\*\*|\*(.+?)\*/g
  let lastIndex = 0
  let match

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index))
    }
    if (match[1]) {
      parts.push(<strong key={match.index} className="font-bold">{match[1]}</strong>)
    } else if (match[2]) {
      parts.push(<em key={match.index} className="italic">{match[2]}</em>)
    }
    lastIndex = regex.lastIndex
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex))
  }

  return parts
}
