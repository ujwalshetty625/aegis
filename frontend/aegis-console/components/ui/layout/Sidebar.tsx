"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, ListChecks, ShieldAlert } from "lucide-react"

const navItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Review Queue",
    href: "/cases",
    icon: ListChecks,
  },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r bg-white px-4 py-6">
      {/* Brand */}
      <div className="flex items-center gap-2 mb-10">
        <ShieldAlert className="w-6 h-6" />
        <h1 className="text-xl font-bold tracking-tight">Aegis</h1>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const active = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                active
                  ? "bg-black text-white"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
