"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Users,
  Receipt,
  ListChecks,
  ShieldAlert,
} from "lucide-react"

const navItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Accounts",
    href: "/accounts",
    icon: Users,
  },
  {
    name: "Transactions",
    href: "/transactions",
    icon: Receipt,
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
    <aside className="w-72 border-r border-[#1C2630] bg-[#0D1117] px-4 py-6">
      <div className="flex items-center gap-2 mb-10">
        <ShieldAlert className="w-6 h-6 text-sky-400" />
        <div>
          <h1 className="text-xl font-bold tracking-tight">Aegis</h1>
          <p className="text-[11px] text-gray-400 font-mono">
            Risk Intelligence Console
          </p>
        </div>
      </div>

      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const active = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                active
                  ? "bg-[#111820] text-white border border-[#243040]"
                  : "text-gray-300 hover:bg-[#111820]"
              }`}
            >
              <item.icon className="w-4 h-4 text-sky-400" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}