import { Brain } from 'lucide-react';

const NavIcon = () => {
  return (
    <nav className="px-6 pt-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer">
          <Brain className="w-10 h-10 text-gray-200" />
          <span className="font-semibold text-xl tracking-wide hidden sm:block">NeuroMind</span>
        </div>

      </nav>
  )
}

export default NavIcon