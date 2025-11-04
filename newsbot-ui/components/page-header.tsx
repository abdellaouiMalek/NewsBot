import type { ReactNode } from "react"

interface PageHeaderProps {
  title: string
  description?: string
  children?: ReactNode
}

export function PageHeader({ title, description, children }: PageHeaderProps) {
  return (
    <div className="mb-6 md:mb-8">
      <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-2">{title}</h1>
      {description && <p className="text-muted-foreground text-base md:text-lg">{description}</p>}
      {children && <div className="mt-4">{children}</div>}
    </div>
  )
}
