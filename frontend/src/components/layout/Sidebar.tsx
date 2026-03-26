import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  PlusCircle,
  Video,
  LayoutTemplate,
  BarChart3,
  CalendarDays,
  Share2,
  Settings,
  History,
} from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/create', icon: PlusCircle, label: 'Create Video' },
  { to: '/videos', icon: Video, label: 'My Videos' },
  { to: '/templates', icon: LayoutTemplate, label: 'Templates' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/calendar', icon: CalendarDays, label: 'Calendar' },
  { to: '/prompts', icon: History, label: 'Prompt History' },
  { to: '/accounts', icon: Share2, label: 'Social Accounts' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  const sidebarOpen = useUIStore((s) => s.sidebarOpen)

  return (
    <aside
      className={`fixed left-0 top-0 z-40 h-screen bg-white border-r border-gray-200 transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-16'
      }`}
    >
      <div className="flex h-16 items-center justify-center border-b border-gray-200 px-4">
        <h1 className={`font-bold text-xl text-brand-600 ${sidebarOpen ? '' : 'hidden'}`}>
          Gase-Y
        </h1>
        {!sidebarOpen && <span className="font-bold text-xl text-brand-600">G</span>}
      </div>

      <nav className="mt-4 space-y-1 px-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
