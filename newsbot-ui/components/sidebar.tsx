"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Sparkles,
  Home,
  Rss,
  Compass,
  TrendingUp,
  Library,
  Settings,
  LogOut,
  Calendar,
  ChevronLeft,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/lib/auth-context"

interface SidebarProps {
  onOpenPreferences: () => void
  isCollapsed?: boolean
  onToggleCollapse?: () => void
}

const navItems = [
  { icon: Home, label: "Home", href: "/dashboard" },
  { icon: Rss, label: "My Feed", href: "/dashboard/my-feed" },
  { icon: Compass, label: "Discover", href: "/dashboard/discover" },
  { icon: TrendingUp, label: "Trends", href: "/dashboard/trends" },
  { icon: Calendar, label: "Events", href: "/dashboard/events" },
  { icon: Library, label: "Sources", href: "/dashboard/sources" },
  { icon: Settings, label: "Settings", href: "/dashboard/settings" },
]

export function Sidebar({ onOpenPreferences, isCollapsed = false, onToggleCollapse }: SidebarProps) {
  const pathname = usePathname()
  const { logout } = useAuth()

  const getActiveLabel = () => {
    const item = navItems.find((item) => item.href === pathname)
    return item?.label || "Home"
  }

  return (
    <aside
      className={`border-r border-border bg-sidebar flex flex-col h-screen transition-all duration-300 ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border flex items-center justify-between">
        {!isCollapsed && (
          <Link href="/dashboard" className="flex items-center gap-3 hover:opacity-80 transition-opacity flex-1">
            <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-sidebar-foreground">NewsBot AI</h1>
            </div>
          </Link>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-1.5 hover:bg-sidebar-accent rounded-md transition-colors text-muted-foreground hover:text-foreground ml-auto"
          aria-label="Toggle sidebar"
        >
          <ChevronLeft className={`h-5 w-5 transition-transform ${isCollapsed ? "rotate-180" : ""}`} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link key={item.label} href={item.href}>
              <Button
                variant="ghost"
                title={isCollapsed ? item.label : ""}
                className={cn(
                  isCollapsed ? "w-full justify-center h-11 p-0" : "w-full justify-start gap-3 h-11",
                  isActive && "bg-sidebar-accent text-sidebar-accent-foreground",
                )}
              >
                <Icon className="h-5 w-5" />
                {!isCollapsed && <span>{item.label}</span>}
              </Button>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-sidebar-border space-y-2 mt-auto">
        {!isCollapsed && (
          <Button variant="ghost" className="w-full justify-start gap-3 h-auto py-3" onClick={onOpenPreferences}>
            <Avatar className="h-9 w-9">
              <AvatarImage src="/diverse-user-avatars.png" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
            <div className="flex-1 text-left">
              <p className="text-sm font-medium text-sidebar-foreground">John Doe</p>
              <p className="text-xs text-muted-foreground">Personalization Settings</p>
            </div>
          </Button>
        )}
        {isCollapsed && (
          <Button
            variant="ghost"
            size="icon"
            className="w-full h-10"
            onClick={onOpenPreferences}
            title="Personalization Settings"
          >
            <Avatar className="h-8 w-8">
              <AvatarImage src="/diverse-user-avatars.png" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
          </Button>
        )}
        <Button
          variant="ghost"
          className={cn(
            "text-muted-foreground hover:text-foreground",
            isCollapsed ? "w-full justify-center h-10 p-0" : "w-full justify-start gap-3 h-10",
          )}
          onClick={logout}
          title={isCollapsed ? "Logout" : ""}
        >
          <LogOut className="h-4 w-4" />
          {!isCollapsed && <span className="text-sm">Logout</span>}
        </Button>
      </div>
    </aside>
  )
}
