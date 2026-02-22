import React, { useState } from 'react';
import {
    LayoutDashboard,
    FolderGit2,
    Users,
    Settings,
    Plus,
    RefreshCw,
    CheckCircle2,
    AlertCircle,
    FileText,
    Activity,
    LogOut,
    Bell,
    Search,
    BookOpen,
    MoreVertical,
    Edit,
    UserPlus
} from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';

// --- Mock Daten ---
const chartData = [
    { date: '12. Okt', words: 4500, pages: 12 },
    { date: '13. Okt', words: 5200, pages: 14 },
    { date: '14. Okt', words: 5200, pages: 14 },
    { date: '15. Okt', words: 6800, pages: 18 },
    { date: '16. Okt', words: 8100, pages: 22 },
    { date: '17. Okt', words: 9500, pages: 26 },
    { date: '18. Okt', words: 11200, pages: 31 },
    { date: '19. Okt', words: 14500, pages: 40 },
];

const projects = [
    {
        id: 1,
        name: 'Masterarbeit_Physik',
        gitUrl: 'https://git.overleaf.com/6538...',
        words: 14500,
        pages: 40,
        status: 'OK',
        lastSync: 'Vor 10 Min',
        sharedWith: 'Prof. Müller (Reviewer)'
    },
    {
        id: 2,
        name: 'Paper_NeurIPS_2024',
        gitUrl: 'https://git.overleaf.com/8821...',
        words: 4200,
        pages: 8,
        status: 'OK',
        lastSync: 'Vor 1 Std',
        sharedWith: 'ML Research Group'
    },
    {
        id: 3,
        name: 'Gruppenarbeit_Verteilte_Systeme',
        gitUrl: 'https://git.overleaf.com/1192...',
        words: 1250,
        pages: 3,
        status: 'AUTH_ERROR',
        lastSync: 'Vor 2 Tagen',
        sharedWith: 'Studienkollegen'
    },
];

const groupsMock = [
    { id: 1, name: 'ML Research Group', members: 5, sharedProjects: 2, role: 'Admin' },
    { id: 2, name: 'Studienkollegen', members: 3, sharedProjects: 1, role: 'Member' },
    { id: 3, name: 'Prof. Müller (Reviewer)', members: 2, sharedProjects: 1, role: 'Admin' },
];

export default function App() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = () => {
        setIsRefreshing(true);
        setTimeout(() => setIsRefreshing(false), 1500);
    };

    return (
        <div className="flex h-screen bg-[#F7F5F1] font-sans text-[#344945] overflow-hidden">

            {/* Sidebar */}
            <aside className="w-64 bg-[#344945] text-[#E0DCD1] flex flex-col hidden md:flex">
                <div className="h-16 flex items-center px-6 border-b border-[#E0DCD1]/20">
                    <Activity className="w-6 h-6 text-[#D5E3E8] mr-2" />
                    <span className="text-xl font-bold text-[#F7F5F1] tracking-tight">Overlytics</span>
                </div>

                <nav className="flex-1 py-6 px-3 space-y-1">
                    <SidebarItem icon={<LayoutDashboard />} label="Übersicht" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
                    <SidebarItem icon={<FolderGit2 />} label="Projekte" active={activeTab === 'projects'} onClick={() => setActiveTab('projects')} />
                    <SidebarItem icon={<Users />} label="Gruppen" active={activeTab === 'groups'} onClick={() => setActiveTab('groups')} />
                    <SidebarItem icon={<Settings />} label="Einstellungen" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
                </nav>

                <div className="p-4 border-t border-[#E0DCD1]/20">
                    <div className="flex items-center gap-3 mb-4 px-2">
                        <div className="w-8 h-8 rounded-full bg-[#E4E3BC] flex items-center justify-center text-[#344945] font-bold">
                            JD
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-medium text-[#F7F5F1]">J. Doe</span>
                            <span className="text-xs text-[#E0DCD1]/70">Free Plan</span>
                        </div>
                    </div>
                    <button className="flex items-center w-full px-2 py-2 text-sm font-medium text-[#E0DCD1]/70 hover:text-[#F7F5F1] rounded-md transition-colors">
                        <LogOut className="w-4 h-4 mr-3" />
                        Abmelden
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-screen overflow-y-auto">

                {/* Top Header */}
                <header className="h-16 bg-white border-b border-[#E0DCD1] flex items-center justify-between px-6 sticky top-0 z-10">
                    <div className="flex items-center bg-[#F7F5F1] border border-[#E0DCD1]/50 rounded-md px-3 py-1.5 w-64 focus-within:border-[#344945]/30 transition-colors">
                        <Search className="w-4 h-4 text-[#344945]/50 mr-2" />
                        <input
                            type="text"
                            placeholder="Projekte suchen..."
                            className="bg-transparent border-none outline-none text-sm text-[#344945] placeholder-[#344945]/50 w-full"
                        />
                    </div>

                    <div className="flex items-center space-x-4">
                        <button className="text-[#344945]/60 hover:text-[#344945] transition-colors relative">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-0 right-0 w-2 h-2 bg-rose-500 rounded-full border border-white"></span>
                        </button>
                        <button className="bg-[#344945] hover:bg-[#344945]/90 text-[#F7F5F1] px-4 py-2 rounded-md text-sm font-medium flex items-center transition-colors shadow-sm">
                            <Plus className="w-4 h-4 mr-2" />
                            Projekt tracken
                        </button>
                    </div>
                </header>

                {/* Dynamic Content */}
                <div className="p-6 max-w-7xl mx-auto w-full space-y-6">

                    {activeTab === 'dashboard' && (
                        <>
                            <div className="flex items-center justify-between">
                                <div>
                                    <h1 className="text-2xl font-bold text-[#344945]">Willkommen zurück!</h1>
                                    <p className="text-sm text-[#344945]/60 mt-1">Hier ist der aktuelle Stand deiner Overleaf-Projekte.</p>
                                </div>
                                <button
                                    onClick={handleRefresh}
                                    className="flex items-center text-sm font-medium text-[#344945] hover:bg-[#D5E3E8]/30 transition-colors bg-white px-3 py-1.5 rounded-md border border-[#E0DCD1] shadow-sm"
                                >
                                    <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                                    {isRefreshing ? 'Synchronisiere...' : 'Jetzt synchronisieren'}
                                </button>
                            </div>

                            {/* Stats Row */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <StatCard
                                    title="Wörter Gesamt"
                                    value="19,950"
                                    trend="+12%"
                                    icon={<FileText className="w-5 h-5" />}
                                    bgColor="bg-[#D5E3E8]/40"
                                    borderColor="border-[#D5E3E8]"
                                />
                                <StatCard
                                    title="Seiten Gesamt"
                                    value="51"
                                    trend="+8%"
                                    icon={<BookOpen className="w-5 h-5" />}
                                    bgColor="bg-[#E4E3BC]/50"
                                    borderColor="border-[#E4E3BC]"
                                />
                                <StatCard
                                    title="Aktive Projekte"
                                    value="3"
                                    trend="0"
                                    icon={<FolderGit2 className="w-5 h-5" />}
                                    bgColor="bg-[#E0DCD1]/50"
                                    borderColor="border-[#E0DCD1]"
                                />
                                <StatCard
                                    title="Nächster Auto-Sync"
                                    value="In 45 Min"
                                    trend=""
                                    icon={<RefreshCw className="w-5 h-5" />}
                                    bgColor="bg-[#F7F5F1]"
                                    borderColor="border-[#E0DCD1]"
                                />
                            </div>

                            {/* Charts Row */}
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-[#E0DCD1] shadow-sm">
                                    <div className="flex items-center justify-between mb-6">
                                        <h2 className="text-base font-semibold text-[#344945]">Schreibfortschritt (Letzte 7 Tage)</h2>
                                        <select className="text-sm border-[#E0DCD1] rounded-md text-[#344945] bg-[#F7F5F1] px-2 py-1 outline-none">
                                            <option>Alle Projekte</option>
                                            <option>Masterarbeit_Physik</option>
                                        </select>
                                    </div>
                                    <div className="h-72 w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                                <defs>
                                                    <linearGradient id="colorWords" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#344945" stopOpacity={0.2}/>
                                                        <stop offset="95%" stopColor="#344945" stopOpacity={0}/>
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E0DCD1" />
                                                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#344945', fontSize: 12, opacity: 0.6}} dy={10} />
                                                <YAxis axisLine={false} tickLine={false} tick={{fill: '#344945', fontSize: 12, opacity: 0.6}} dx={-10} />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #E0DCD1', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                                    labelStyle={{ color: '#344945', marginBottom: '4px', fontWeight: 'bold' }}
                                                    itemStyle={{ color: '#344945' }}
                                                />
                                                <Area type="monotone" dataKey="words" name="Wörter" stroke="#344945" strokeWidth={3} fillOpacity={1} fill="url(#colorWords)" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                <div className="bg-white p-6 rounded-xl border border-[#E0DCD1] shadow-sm flex flex-col">
                                    <h2 className="text-base font-semibold text-[#344945] mb-4">Git Zugangsdaten</h2>

                                    <div className="flex-1 space-y-4">
                                        <div className="bg-[#D5E3E8]/30 border border-[#D5E3E8] rounded-lg p-4 flex items-start">
                                            <CheckCircle2 className="w-5 h-5 text-[#344945] mt-0.5 mr-3 flex-shrink-0" />
                                            <div>
                                                <h3 className="text-sm font-medium text-[#344945]">Token aktiv</h3>
                                                <p className="text-xs text-[#344945]/70 mt-1">Dein Overleaf Git-Token ist sicher verschlüsselt gespeichert.</p>
                                            </div>
                                        </div>

                                        <div className="bg-[#F7F5F1] border border-[#E0DCD1] rounded-lg p-4">
                                            <p className="text-xs font-medium text-[#344945]/60 uppercase tracking-wider mb-2">Verknüpfte Email</p>
                                            <p className="text-sm text-[#344945] font-medium truncate">j.doe@university.edu</p>
                                        </div>
                                    </div>

                                    <button className="mt-4 w-full text-center text-sm text-[#344945] font-medium hover:text-[#344945]/70 transition-colors">
                                        Credentials aktualisieren &rarr;
                                    </button>
                                </div>
                            </div>

                            {/* Project List */}
                            <div className="bg-white rounded-xl border border-[#E0DCD1] shadow-sm overflow-hidden">
                                <div className="p-5 border-b border-[#E0DCD1] flex items-center justify-between bg-[#F7F5F1]/50">
                                    <h2 className="text-base font-semibold text-[#344945]">Verknüpfte Projekte</h2>
                                    <button className="text-sm text-[#344945] font-medium hover:text-[#344945]/70">Alle ansehen</button>
                                </div>

                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm text-left">
                                        <thead className="text-xs text-[#344945]/70 bg-[#F7F5F1] border-b border-[#E0DCD1] uppercase">
                                        <tr>
                                            <th className="px-6 py-4 font-medium">Projektname</th>
                                            <th className="px-6 py-4 font-medium">Status</th>
                                            <th className="px-6 py-4 font-medium">Metriken</th>
                                            <th className="px-6 py-4 font-medium">Letzter Sync</th>
                                            <th className="px-6 py-4 font-medium">Geteilt mit</th>
                                            <th className="px-6 py-4 text-right font-medium">Aktion</th>
                                        </tr>
                                        </thead>
                                        <tbody className="divide-y divide-[#E0DCD1]/50">
                                        {projects.map((project) => (
                                            <tr key={project.id} className="hover:bg-[#F7F5F1]/80 transition-colors group">
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center">
                                                        <FolderGit2 className="w-4 h-4 text-[#344945]/50 mr-3" />
                                                        <div>
                                                            <p className="font-medium text-[#344945]">{project.name}</p>
                                                            <a href={project.gitUrl} className="text-xs text-[#344945]/50 hover:text-[#344945] truncate w-40 inline-block transition-colors">
                                                                {project.gitUrl}
                                                            </a>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4">
                                                    {project.status === 'OK' ? (
                                                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-[#D5E3E8]/70 text-[#344945]">
                            <CheckCircle2 className="w-3 h-3 mr-1" /> Aktiv
                          </span>
                                                    ) : (
                                                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-[#E4E3BC] text-[#344945]">
                            <AlertCircle className="w-3 h-3 mr-1" /> Auth Error
                          </span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <div className="flex flex-col gap-1">
                                                        <span className="text-[#344945] font-medium">{project.words.toLocaleString()} Wörter</span>
                                                        <span className="text-xs text-[#344945]/60">{project.pages} Seiten</span>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 text-[#344945]/70">
                                                    {project.lastSync}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center text-[#344945]/70">
                                                        <Users className="w-3.5 h-3.5 mr-1.5 text-[#344945]/50" />
                                                        <span className="truncate w-32">{project.sharedWith}</span>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    <button className="text-[#344945]/50 hover:text-[#344945] font-medium px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                                                        Details
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </>
                    )}

                    {activeTab === 'projects' && <ProjectsView projects={projects} />}

                    {activeTab === 'groups' && <GroupsView groups={groupsMock} />}

                    {activeTab === 'settings' && (
                        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-[#E0DCD1] shadow-sm">
                            <Settings className="w-12 h-12 text-[#E0DCD1] mb-4" />
                            <h2 className="text-xl font-bold text-[#344945]">Einstellungen</h2>
                            <p className="text-[#344945]/60 mt-2">Globale Profil- und Kontoeinstellungen folgen hier.</p>
                        </div>
                    )}

                </div>
            </main>
        </div>
    );
}

// --- Hilfskomponenten ---

function SidebarItem({ icon, label, active, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                active
                    ? 'bg-[#E0DCD1]/10 text-[#F7F5F1]'
                    : 'text-[#E0DCD1]/70 hover:bg-[#E0DCD1]/5 hover:text-[#F7F5F1]'
            }`}
        >
      <span className={`mr-3 ${active ? 'text-[#D5E3E8]' : 'text-[#E0DCD1]/50'}`}>
        {React.cloneElement(icon, { className: 'w-5 h-5' })}
      </span>
            {label}
        </button>
    );
}

function StatCard({ title, value, trend, icon, bgColor, borderColor }) {
    return (
        <div className="bg-white p-5 rounded-xl border border-[#E0DCD1] shadow-sm flex items-start justify-between hover:border-[#344945]/20 transition-colors">
            <div>
                <p className="text-sm font-medium text-[#344945]/60 mb-1">{title}</p>
                <div className="flex items-baseline gap-2">
                    <h3 className="text-2xl font-bold text-[#344945]">{value}</h3>
                    {trend && (
                        <span className={`text-xs font-semibold ${trend.startsWith('+') ? 'text-[#344945]' : 'text-[#344945]/60'}`}>
              {trend}
            </span>
                    )}
                </div>
            </div>
            <div className={`p-3 rounded-lg border ${bgColor} ${borderColor} text-[#344945]`}>
                {icon}
            </div>
        </div>
    );
}

function ProjectsView({ projects }) {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-[#344945]">Projekte verwalten</h1>
                    <p className="text-sm text-[#344945]/60 mt-1">Alle deine getrackten Overleaf-Projekte auf einen Blick.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map(p => (
                    <div key={p.id} className="bg-white rounded-xl border border-[#E0DCD1] shadow-sm hover:border-[#344945]/20 transition-all flex flex-col group">
                        <div className="p-5 border-b border-[#E0DCD1]/50 flex justify-between items-start">
                            <div className="overflow-hidden">
                                <h3 className="font-bold text-[#344945] text-lg truncate" title={p.name}>{p.name}</h3>
                                <a href={p.gitUrl} className="text-xs text-[#344945]/50 hover:text-[#344945] mt-1 block truncate w-full transition-colors">
                                    {p.gitUrl}
                                </a>
                            </div>
                            <button className="text-[#E0DCD1] hover:text-[#344945] transition-colors ml-2 flex-shrink-0">
                                <MoreVertical className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-5 flex-1 flex flex-col gap-4">
                            <div className="flex justify-between items-center">
                                <span className="text-xs font-medium text-[#344945]/60 uppercase tracking-wider">Status</span>
                                {p.status === 'OK' ? (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-[#D5E3E8]/70 text-[#344945]">
                    <CheckCircle2 className="w-3 h-3 mr-1" /> Aktiv
                  </span>
                                ) : (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-[#E4E3BC] text-[#344945]">
                    <AlertCircle className="w-3 h-3 mr-1" /> Auth Error
                  </span>
                                )}
                            </div>

                            <div className="grid grid-cols-2 gap-4 py-2 border-y border-[#E0DCD1]/30">
                                <div>
                                    <p className="text-xs text-[#344945]/50 mb-1">Wörter</p>
                                    <p className="font-semibold text-[#344945]">{p.words.toLocaleString()}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-[#344945]/50 mb-1">Seiten</p>
                                    <p className="font-semibold text-[#344945]">{p.pages}</p>
                                </div>
                            </div>

                            <div className="mt-auto pt-2 flex justify-between items-center">
                                <span className="text-xs text-[#344945]/50">Sync: {p.lastSync}</span>
                                <div className="flex gap-2">
                                    <button className="p-1.5 text-[#344945]/50 hover:text-[#344945] hover:bg-[#F7F5F1] rounded-md transition-colors" title="Synchronisieren">
                                        <RefreshCw className="w-4 h-4" />
                                    </button>
                                    <button className="p-1.5 text-[#344945]/50 hover:text-[#344945] hover:bg-[#F7F5F1] rounded-md transition-colors" title="Bearbeiten">
                                        <Edit className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function GroupsView({ groups }) {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-[#344945]">Gruppen & Freigaben</h1>
                    <p className="text-sm text-[#344945]/60 mt-1">Verwalte, wer Zugriff auf die Metriken deiner Projekte hat.</p>
                </div>
                <button className="bg-[#344945] hover:bg-[#344945]/90 text-[#F7F5F1] px-4 py-2 rounded-md text-sm font-medium flex items-center transition-colors shadow-sm">
                    <UserPlus className="w-4 h-4 mr-2" />
                    Neue Gruppe
                </button>
            </div>

            <div className="bg-white rounded-xl border border-[#E0DCD1] shadow-sm overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-[#344945]/70 bg-[#F7F5F1] border-b border-[#E0DCD1] uppercase">
                    <tr>
                        <th className="px-6 py-4 font-medium">Gruppenname</th>
                        <th className="px-6 py-4 font-medium">Mitglieder</th>
                        <th className="px-6 py-4 font-medium">Geteilte Projekte</th>
                        <th className="px-6 py-4 font-medium">Deine Rolle</th>
                        <th className="px-6 py-4 text-right font-medium">Aktion</th>
                    </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E0DCD1]/50">
                    {groups.map((group) => (
                        <tr key={group.id} className="hover:bg-[#F7F5F1]/80 transition-colors group-row">
                            <td className="px-6 py-4">
                                <div className="flex items-center">
                                    <div className="w-8 h-8 rounded-md bg-[#D5E3E8]/50 text-[#344945] flex items-center justify-center font-bold mr-3 border border-[#D5E3E8]">
                                        {group.name.charAt(0)}
                                    </div>
                                    <span className="font-medium text-[#344945]">{group.name}</span>
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex items-center text-[#344945]">
                                    <Users className="w-4 h-4 mr-2 text-[#344945]/50" />
                                    {group.members}
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex items-center text-[#344945]">
                                    <FolderGit2 className="w-4 h-4 mr-2 text-[#344945]/50" />
                                    {group.sharedProjects}
                                </div>
                            </td>
                            <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                      group.role === 'Admin' ? 'bg-[#344945] text-[#F7F5F1]' : 'bg-[#E0DCD1]/50 text-[#344945]'
                  }`}>
                    {group.role}
                  </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                                <div className="flex justify-end gap-2">
                                    <button className="p-1.5 text-[#344945]/50 hover:text-[#344945] hover:bg-[#E0DCD1]/30 rounded transition-colors" title="Einstellungen">
                                        <Settings className="w-4 h-4" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}