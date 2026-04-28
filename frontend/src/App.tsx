import { useState, useEffect, useRef } from "react";
import SqlEditor from "./components/SqlEditor";
import ConversionPanel from "./components/ConversionPanel";
import ThreeBackground from "./components/ThreeBackground";
import HistoryPanel from "./components/HistoryPanel";
import DocsPanel from "./components/DocsPanel";
import MySQLConnection from "./components/MySQLConnection";
import { apiService } from "./services/api";
import { Database, Upload, Play, FileCode2, History, Settings, BookOpen, Search, RefreshCw, Sparkles, ChevronDown, Loader2, Zap, Rocket, Gamepad2, ClipboardPaste, FileText, Network, Hexagon, Leaf, BarChart3 } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

const DEFAULT_SQL = `-- E-commerce Database Schema
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    status ENUM('pending', 'shipped', 'delivered'),
    total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);`;

export default function App() {
  const [loading, setLoading] = useState(true);
  const [sql, setSql] = useState<string>(DEFAULT_SQL);
  const [status, setStatus] = useState<'idle' | 'converting' | 'done' | 'error'>('idle');
  const [pipelineStep, setPipelineStep] = useState(-1);
  const [conversionProgress, setConversionProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [inputTab, setInputTab] = useState<'paste' | 'mysql' | 'upload'>('paste');
  const [showHero, setShowHero] = useState(true);
  const [activePanel, setActivePanel] = useState<'converter' | 'history' | 'docs'>('converter');
  const [aiAvailable, setAiAvailable] = useState(false);
  
  const converterRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2000);
    // Check API health
    checkApiHealth();
    return () => clearTimeout(timer);
  }, []);

  const checkApiHealth = async () => {
    try {
      const health = await apiService.healthCheck();
      setAiAvailable(health.ai_available);
    } catch (err) {
      console.error('API health check failed:', err);
      setAiAvailable(false);
    }
  };

  const scrollToConverter = () => {
    setShowHero(false);
    setActivePanel('converter');
    setTimeout(() => {
      converterRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleLoadHistory = (historySql: string) => {
    setSql(historySql);
    setActivePanel('converter');
    setInputTab('paste');
    setShowHero(false);
  };

  const handleSchemaExtracted = (extractedSql: string, tables: string[]) => {
    setSql(extractedSql);
    setInputTab('paste');
  };

  const saveToHistory = (sql: string, inputMethod: string, databases: string[]) => {
    const historyEntry = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      sql,
      inputMethod,
      databases,
      preview: sql.substring(0, 100) + (sql.length > 100 ? '...' : '')
    };

    const savedHistory = localStorage.getItem('conversion_history');
    const history = savedHistory ? JSON.parse(savedHistory) : [];
    const updatedHistory = [historyEntry, ...history].slice(0, 50);
    localStorage.setItem('conversion_history', JSON.stringify(updatedHistory));
  };

  const handleConvert = async () => {
    setStatus('converting');
    setResult(null);
    setError(null);
    setPipelineStep(0); // Parse
    
    try {
      // Simulate pipeline steps with real API call
      await new Promise(r => setTimeout(r, 400));
      setPipelineStep(1); // Analyze
      
      await new Promise(r => setTimeout(r, 400));
      setPipelineStep(2); // Transform
      
      // Map frontend input method to backend enum
      const inputMethodMap: Record<string, string> = {
        'paste': 'manual',
        'mysql': 'mysql',
        'upload': 'file'
      };
      
      // Call real API
      const response = await apiService.convertSchema({
        sql: sql,
        target_databases: ['mongodb', 'cassandra', 'neo4j'],
        input_method: inputMethodMap[inputTab] as any,
        include_ai_explanation: true
      });
      
      setPipelineStep(3); // Generate
      await new Promise(r => setTimeout(r, 400));
      
      // Transform API response to match UI format
      const transformedResult: any = {};
      
      if (response.mongodb) {
        transformedResult.mongodb = {
          schema: response.mongodb.schema,
          explanation: response.mongodb.explanation,
          warnings: response.mongodb.warnings,
          stats: response.mongodb.stats,
          score: response.mongodb.score,
          sample_data: response.mongodb.sample_data,
          visualization: response.mongodb.visualization
        };
      }
      
      if (response.cassandra) {
        transformedResult.cassandra = {
          schema: response.cassandra.schema,
          explanation: response.cassandra.explanation,
          warnings: response.cassandra.warnings,
          stats: response.cassandra.stats,
          score: response.cassandra.score,
          visualization: response.cassandra.visualization
        };
      }
      
      if (response.neo4j) {
        transformedResult.neo4j = {
          schema: response.neo4j.schema,
          explanation: response.neo4j.explanation,
          warnings: response.neo4j.warnings,
          stats: response.neo4j.stats,
          score: response.neo4j.score,
          visualization: response.neo4j.visualization
        };
      }
      
      if (document.startViewTransition) {
        document.startViewTransition(() => {
          setResult(transformedResult);
          setStatus('done');
          setPipelineStep(-1);
          // Save to history
          saveToHistory(sql, inputTab, Object.keys(transformedResult));
        });
      } else {
        setResult(transformedResult);
        setStatus('done');
        setPipelineStep(-1);
        // Save to history
        saveToHistory(sql, inputTab, Object.keys(transformedResult));
      }
    } catch (err: any) {
      console.error('Conversion failed:', err);
      setError(err.message || 'Conversion failed. Please try again.');
      setStatus('error');
      setPipelineStep(-1);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-[#050508] z-50 flex flex-col items-center justify-center">
        <div className="w-24 h-24 mb-8 relative preserve-3d animate-[spin_3s_linear_infinite]">
          <div className="absolute inset-0 border-2 border-[#3b82f6] bg-[#3b82f6]/10 flex items-center justify-center text-[#3b82f6]" style={{ transform: 'translateZ(48px)' }}><Leaf size={32} /></div>
          <div className="absolute inset-0 border-2 border-[#3b82f6] bg-[#3b82f6]/10 flex items-center justify-center text-[#3b82f6]" style={{ transform: 'rotateY(90deg) translateZ(48px)' }}><Hexagon size={32} /></div>
          <div className="absolute inset-0 border-2 border-[#3b82f6] bg-[#3b82f6]/10 flex items-center justify-center text-[#3b82f6]" style={{ transform: 'rotateY(180deg) translateZ(48px)' }}><Network size={32} /></div>
          <div className="absolute inset-0 border-2 border-[#3b82f6] bg-[#3b82f6]/10 flex items-center justify-center text-[#3b82f6]" style={{ transform: 'rotateY(-90deg) translateZ(48px)' }}><BarChart3 size={32} /></div>
        </div>
        <div className="font-orbitron text-sm text-gray-400 tracking-[0.25em] uppercase">Initializing 3D Experience</div>
        <div className="w-48 h-1 bg-white/10 rounded-full mt-5 overflow-hidden">
          <motion.div className="h-full bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6]" initial={{ width: 0 }} animate={{ width: '100%' }} transition={{ duration: 2 }} />
        </div>
      </div>
    );
  }

  return (
    <>
      <ThreeBackground />
      <div className="scanlines" />
      <div className="vignette" />
      
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Top Navigation */}
        <nav className="flex items-center justify-between px-6 py-3 bg-[#0a0a12]/70 backdrop-blur-xl border-b border-[#3b82f6]/20 sticky top-0 z-50">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl accent-gradient flex items-center justify-center text-white shadow-[0_0_20px_rgba(59,130,246,0.4)] relative overflow-hidden">
              <span className="relative z-10"><Zap size={22} fill="currentColor" /></span>
              <motion.div className="absolute inset-0 bg-white/30" animate={{ x: ['-100%', '100%'] }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }} />
            </div>
            <div>
              <div className="font-orbitron font-bold text-lg tracking-widest accent-gradient-text">SQLCONV</div>
              <div className="text-[10px] text-[#3b82f6] bg-[#3b82f6]/15 px-2 py-0.5 rounded-full border border-[#3b82f6]/30 inline-block">v3.0</div>
            </div>
          </div>

          <div className="flex gap-1 bg-[#12121c]/60 p-1 rounded-2xl border border-white/5">
            <button 
              onClick={() => { setActivePanel('converter'); setShowHero(false); }}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                activePanel === 'converter' 
                  ? 'bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white shadow-[0_4px_20px_rgba(59,130,246,0.4)]'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <RefreshCw size={16} /> Converter
            </button>
            <button 
              onClick={() => { setActivePanel('history'); setShowHero(false); }}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                activePanel === 'history' 
                  ? 'bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white shadow-[0_4px_20px_rgba(59,130,246,0.4)]'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <History size={16} /> History
            </button>
            <button 
              onClick={() => { setActivePanel('docs'); setShowHero(false); }}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                activePanel === 'docs' 
                  ? 'bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white shadow-[0_4px_20px_rgba(59,130,246,0.4)]'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <BookOpen size={16} /> Docs
            </button>
          </div>

          <div className="flex items-center gap-4">
            <button className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-br from-[#00758f] to-[#f29111] rounded-xl text-white text-sm font-semibold shadow-[0_4px_20px_rgba(242,145,17,0.3)] hover:-translate-y-0.5 transition-transform">
              <Database size={16} /> Connect MySQL
            </button>
            <div className="flex gap-2">
              <div className="flex items-center gap-1.5 px-3.5 py-2 bg-[#12121c]/80 border border-white/10 rounded-full text-xs font-medium backdrop-blur-md">
                <div className={`w-2 h-2 rounded-full ${aiAvailable ? 'bg-green-500 shadow-[0_0_10px_#22c55e] animate-pulse' : 'bg-red-500 shadow-[0_0_10px_#ef4444]'}`} /> 
                {aiAvailable ? 'Ollama AI' : 'AI Offline'}
              </div>
              <div className="flex items-center gap-1.5 px-3.5 py-2 bg-[#12121c]/80 border border-white/10 rounded-full text-xs font-medium backdrop-blur-md">
                <div className={`w-2 h-2 rounded-full ${aiAvailable ? 'bg-green-500 shadow-[0_0_10px_#22c55e] animate-pulse' : 'bg-gray-500'}`} /> 
                LangGraph
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        {showHero && (
          <section className="min-h-[calc(100vh-76px)] flex flex-col items-center justify-center px-6 relative">
            <div className="text-center max-w-3xl z-10">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#3b82f6]/10 border border-[#3b82f6]/30 rounded-full text-xs font-semibold text-[#3b82f6] mb-6 animate-[float_3s_ease-in-out_infinite]">
                <Sparkles size={14} /> Powered by Ollama + LangGraph + 3D
              </div>
              <h1 className="text-7xl font-black font-orbitron leading-tight mb-6 tracking-tighter">
                Transform SQL to<br/>
                <span className="cyber-gradient">Any Database</span>
              </h1>
              <p className="text-xl text-gray-400 leading-relaxed mb-10 max-w-2xl mx-auto">
                Experience the future of database migration with AI-powered schema conversion, real-time 3D visualizations, and intelligent query translation.
              </p>
              <div className="flex justify-center gap-4 mb-16">
                <button onClick={scrollToConverter} className="px-9 py-4 rounded-2xl bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white font-semibold flex items-center gap-2 shadow-[0_8px_30px_rgba(59,130,246,0.4)] hover:-translate-y-1 transition-transform cursor-pointer">
                  <Rocket size={20} /> Start Converting
                </button>
                <button className="px-9 py-4 rounded-2xl bg-white/5 border border-white/10 text-white font-semibold flex items-center gap-2 hover:bg-white/10 transition-colors cursor-pointer">
                  <Gamepad2 size={20} /> Explore 3D
                </button>
              </div>
              <div className="flex justify-center gap-16">
                <div className="text-center">
                  <div className="text-5xl font-bold font-orbitron accent-gradient-text">4</div>
                  <div className="text-sm text-gray-500 mt-2 uppercase tracking-widest">Databases</div>
                </div>
                <div className="text-center">
                  <div className="text-5xl font-bold font-orbitron accent-gradient-text">98%</div>
                  <div className="text-sm text-gray-500 mt-2 uppercase tracking-widest">Accuracy</div>
                </div>
                <div className="text-center">
                  <div className="text-5xl font-bold font-orbitron accent-gradient-text">&lt;2s</div>
                  <div className="text-sm text-gray-500 mt-2 uppercase tracking-widest">Speed</div>
                </div>
              </div>
            </div>
            
            <div onClick={scrollToConverter} className="absolute bottom-10 flex flex-col items-center gap-2 cursor-pointer animate-bounce">
              <span className="text-xs text-gray-500 uppercase tracking-widest">Scroll Down</span>
              <div className="w-6 h-10 border-2 border-gray-500 rounded-full relative">
                <div className="absolute top-2 left-1/2 -translate-x-1/2 w-1 h-2 bg-[#3b82f6] rounded-full animate-[ping_2s_infinite]" />
              </div>
            </div>
          </section>
        )}

        {/* Main Content Section */}
        <section ref={converterRef} className="flex-1 p-6 max-w-[1800px] mx-auto w-full flex flex-col">
          {/* History Panel */}
          {!showHero && activePanel === 'history' && (
            <div className="flex-1 glass-panel rounded-[20px] overflow-hidden">
              <HistoryPanel onLoadHistory={handleLoadHistory} />
            </div>
          )}

          {/* Docs Panel */}
          {!showHero && activePanel === 'docs' && (
            <div className="flex-1 glass-panel rounded-[20px] overflow-hidden">
              <DocsPanel />
            </div>
          )}

          {/* Converter Panel */}
          {!showHero && activePanel === 'converter' && (
            <div className="text-center mb-10">
              <h2 className="text-4xl font-bold font-orbitron cyber-gradient mb-3">SQL Converter</h2>
              <p className="text-gray-400">Paste your SQL schema and watch the magic happen</p>
            </div>
          )}

          {activePanel === 'converter' && (
          <div className="flex flex-col xl:flex-row gap-6 flex-1 min-h-[700px]">
            {/* Left Panel - Editor */}
            <div className="w-full xl:flex-1 xl:min-w-[500px] xl:max-w-[700px] glass-panel rounded-[20px] flex flex-col relative overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-white/5 bg-[#1a1a28]/40">
                <div className="flex items-center gap-3 font-semibold text-sm">
                  <div className="w-9 h-9 rounded-xl accent-gradient flex items-center justify-center text-white"><FileCode2 size={20} /></div>
                  SQL Input
                </div>
                <div className="flex gap-1">
                  <button onClick={() => setInputTab('paste')} className={`px-4 py-2 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${inputTab === 'paste' ? 'accent-gradient text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}><ClipboardPaste size={14} /> Paste</button>
                  <button onClick={() => setInputTab('mysql')} className={`px-4 py-2 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${inputTab === 'mysql' ? 'accent-gradient text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}><Database size={14} /> MySQL</button>
                  <button onClick={() => setInputTab('upload')} className={`px-4 py-2 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${inputTab === 'upload' ? 'accent-gradient text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}><Upload size={14} /> Upload</button>
                </div>
              </div>

              <div className="flex-1 relative flex flex-col">
                {inputTab === 'paste' && (
                  <>
                    {/* Warning for long SQL */}
                    {sql.length > 10000 && (
                      <div className="absolute top-4 right-4 z-20 px-4 py-2.5 bg-yellow-500/20 border border-yellow-500/50 rounded-xl text-yellow-500 text-xs font-medium flex items-center gap-2 backdrop-blur-md shadow-lg animate-[slideInRight_0.3s_ease-out]">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span>Large SQL ({Math.round(sql.length / 1000)}KB)</span>
                        <span className="text-yellow-400/70">• May take longer</span>
                      </div>
                    )}
                    
                    <div className="flex-1 relative flex">
                      {/* Line numbers with optimization for long code */}
                      <div className="w-14 bg-[#05050a]/50 border-r border-white/5 text-right py-4 pr-3 font-mono text-[13px] text-gray-600 select-none leading-[1.6] overflow-hidden">
                        {sql.split('\n').slice(0, Math.min(sql.split('\n').length, 1000)).map((_, i) => (
                          <div key={i} className="hover:text-[#3b82f6] transition-colors">{i + 1}</div>
                        ))}
                        {sql.split('\n').length > 1000 && (
                          <div className="text-yellow-500 text-[10px] mt-2">
                            +{sql.split('\n').length - 1000} more lines
                          </div>
                        )}
                      </div>
                      
                      {/* Editor with optimizations */}
                      <div className="flex-1 relative">
                        <SqlEditor 
                          value={sql} 
                          onChange={(val) => setSql(val || "")}
                        />
                        
                        {/* Minimap indicator for long code */}
                        {sql.length > 5000 && (
                          <div className="absolute bottom-4 right-4 px-3 py-1.5 bg-[#1a1a28]/90 border border-white/10 rounded-lg text-[10px] text-gray-400 backdrop-blur-md flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#3b82f6] animate-pulse" />
                            Minimap enabled
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )}

                {inputTab === 'upload' && (
                  <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-[#3b82f6]/30 m-6 rounded-2xl bg-[#3b82f6]/5 hover:bg-[#3b82f6]/10 transition-colors cursor-pointer relative group">
                    <input 
                      type="file" 
                      accept=".sql,.txt" 
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (!file) return;
                        const reader = new FileReader();
                        reader.onload = (event) => {
                          const content = event.target?.result as string;
                          setSql(content);
                          setInputTab('paste');
                        };
                        reader.readAsText(file);
                      }} 
                    />
                    <div className="w-20 h-20 rounded-2xl bg-[#3b82f6]/20 text-[#3b82f6] flex items-center justify-center mb-5 group-hover:scale-110 group-hover:shadow-[0_0_30px_rgba(59,130,246,0.4)] transition-all duration-300">
                      <Upload size={36} />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">Upload SQL File</h3>
                    <p className="text-sm text-gray-400 text-center max-w-xs mb-6">Drag and drop your .sql or .txt file here, or click to browse your computer</p>
                    <div className="px-6 py-2.5 rounded-xl bg-[#1a1a28] border border-white/10 text-sm font-medium text-gray-300 group-hover:border-[#3b82f6]/50 transition-colors">
                      Select File
                    </div>
                  </div>
                )}

                {inputTab === 'mysql' && (
                  <MySQLConnection onSchemaExtracted={handleSchemaExtracted} />
                )}
                  
                {/* Conversion Overlay with Parallel Progress */}
                <AnimatePresence>
                    {status === 'converting' && (
                      <motion.div 
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-[#050508]/95 backdrop-blur-md z-10 flex flex-col items-center justify-center p-8"
                      >
                        {/* Main Pipeline Steps */}
                        <div className="flex items-center gap-6 mb-12">
                          {[
                            { id: 0, icon: <FileText size={32} />, label: 'Parse', time: '0.5s' },
                            { id: 1, icon: <Search size={32} />, label: 'Analyze', time: '0.8s' },
                            { id: 2, icon: <RefreshCw size={32} />, label: 'Transform', time: '2.0s' },
                            { id: 3, icon: <Sparkles size={32} />, label: 'AI Enhance', time: '3.5s' }
                          ].map((step, i) => (
                            <div key={step.id} className="flex items-center gap-6">
                              <div className={`flex flex-col items-center gap-2.5 transition-all duration-500 ${pipelineStep >= step.id ? 'opacity-100' : 'opacity-30'}`}>
                                <div className={`w-[70px] h-[70px] rounded-[18px] flex items-center justify-center text-3xl transition-all duration-500 ${
                                  pipelineStep === step.id ? 'accent-gradient shadow-[0_0_40px_rgba(59,130,246,0.6)] animate-pulse' : 
                                  pipelineStep > step.id ? 'bg-green-500 shadow-[0_0_30px_rgba(34,197,94,0.5)]' : 
                                  'bg-[#1a1a28]/80 border-2 border-[#27272a]'
                                }`}>
                                  {step.icon}
                                </div>
                                <div className="text-xs font-bold text-gray-400 uppercase tracking-widest">{step.label}</div>
                                <div className="text-[10px] text-gray-500">{step.time}</div>
                              </div>
                              {i < 3 && <div className="text-3xl text-gray-600 opacity-50">→</div>}
                            </div>
                          ))}
                        </div>
                        
                        {/* Parallel Database Conversions */}
                        {pipelineStep >= 2 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 20 }} 
                            animate={{ opacity: 1, y: 0 }}
                            className="w-full max-w-2xl mb-8"
                          >
                            <div className="text-center mb-4">
                              <div className="text-sm font-semibold text-white mb-1">Parallel Conversions</div>
                              <div className="text-xs text-gray-400">Converting to 3 databases simultaneously</div>
                            </div>
                            
                            <div className="grid grid-cols-3 gap-4">
                              {[
                                { name: 'MongoDB', icon: <Leaf size={20} />, color: 'from-[#00ed64] to-[#00c853]' },
                                { name: 'Cassandra', icon: <Hexagon size={20} />, color: 'from-[#f59e0b] to-[#f97316]' },
                                { name: 'Neo4j', icon: <Network size={20} />, color: 'from-[#a855f7] to-[#9333ea]' }
                              ].map((db, i) => (
                                <div key={db.name} className="bg-[#1a1a28]/80 border border-white/10 rounded-xl p-4 backdrop-blur-md">
                                  <div className="flex items-center gap-2 mb-3">
                                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${db.color} flex items-center justify-center text-white`}>
                                      {db.icon}
                                    </div>
                                    <div className="text-xs font-semibold text-white">{db.name}</div>
                                  </div>
                                  <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                                    <motion.div 
                                      className={`h-full bg-gradient-to-r ${db.color}`}
                                      initial={{ width: '0%' }}
                                      animate={{ width: pipelineStep >= 3 ? '100%' : '60%' }}
                                      transition={{ duration: 1.5, delay: i * 0.2 }}
                                    />
                                  </div>
                                  <div className="text-[10px] text-gray-500 mt-2 text-center">
                                    {pipelineStep >= 3 ? 'Complete ✓' : 'Converting...'}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}
                        
                        {/* Overall Progress */}
                        <div className="w-[500px] text-center">
                          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mb-4">
                            <motion.div 
                              className="h-full accent-gradient shadow-[0_0_20px_rgba(59,130,246,0.5)]"
                              initial={{ width: '0%' }}
                              animate={{ width: `${((pipelineStep + 1) / 4) * 100}%` }}
                              transition={{ duration: 0.5 }}
                            />
                          </div>
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">
                              {pipelineStep === 0 ? 'Parsing SQL syntax...' :
                               pipelineStep === 1 ? 'Analyzing schema structure...' :
                               pipelineStep === 2 ? 'Converting to NoSQL formats...' :
                               'Enhancing with LangGraph AI...'}
                            </span>
                            <span className="text-[#3b82f6] font-bold">
                              {Math.round(((pipelineStep + 1) / 4) * 100)}%
                            </span>
                          </div>
                          {estimatedTime > 0 && (
                            <div className="text-xs text-gray-500 mt-2">
                              Estimated time: ~{estimatedTime}s
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                    
                    {status === 'error' && error && (
                      <motion.div 
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-[#050508]/95 backdrop-blur-md z-10 flex flex-col items-center justify-center p-8"
                      >
                        <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mb-6">
                          <span className="text-4xl">⚠️</span>
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Conversion Failed</h3>
                        <p className="text-sm text-gray-400 text-center max-w-md mb-6">{error}</p>
                        <button
                          onClick={() => setStatus('idle')}
                          className="px-6 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
                        >
                          Try Again
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
              </div>

              <div className="flex items-center justify-between p-3.5 border-t border-white/5 bg-[#1a1a28]/40">
                <div className="flex gap-6 text-xs text-gray-500">
                  <span>Lines: <strong className="text-gray-200">{sql.split('\n').length}</strong></span>
                  <span>Tables: <strong className="text-gray-200">{(sql.match(/CREATE TABLE/gi) || []).length}</strong></span>
                  <span>Characters: <strong className={`${sql.length > 10000 ? 'text-yellow-500' : sql.length > 50000 ? 'text-red-500' : 'text-gray-200'}`}>{sql.length.toLocaleString()}</strong>{sql.length > 10000 && <span className="ml-1 text-yellow-500">⚠️</span>}</span>
                  <span>UTF-8</span>
                </div>
                <button 
                  onClick={handleConvert}
                  disabled={status === 'converting' || !sql.trim()}
                  className={`flex items-center gap-3 px-8 py-3.5 rounded-xl text-sm font-semibold text-white transition-all overflow-hidden relative cursor-pointer ${
                    status === 'converting' ? 'bg-gradient-to-br from-yellow-500 to-orange-600 shadow-[0_8px_30px_rgba(245,158,11,0.4)]' :
                    status === 'done' ? 'bg-gradient-to-br from-green-500 to-green-700 shadow-[0_8px_30px_rgba(34,197,94,0.4)]' :
                    'accent-gradient shadow-[0_8px_30px_rgba(59,130,246,0.4)] hover:-translate-y-0.5'
                  }`}
                >
                  {status === 'converting' && <Loader2 size={18} className="animate-spin" />}
                  <span>{status === 'converting' ? 'Converting...' : status === 'done' ? 'Done ✓' : 'Convert'}</span>
                  {status === 'idle' && <span>→</span>}
                </button>
              </div>
            </div>

            {/* Right Panel - Output */}
            <div className="w-full xl:flex-[1.5] xl:min-w-[600px] glass-panel rounded-[20px] flex flex-col relative overflow-hidden min-h-[520px]">
              <ConversionPanel data={result} status={status} />
            </div>
          </div>
          )}
        </section>

        {/* Status Bar */}
        <footer className="flex items-center justify-between px-6 py-3 bg-[#0a0a12]/90 backdrop-blur-xl border-t border-white/5 mt-auto relative z-50">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <div className={`w-2 h-2 rounded-full ${status === 'converting' ? 'bg-yellow-500 shadow-[0_0_10px_#eab308] animate-pulse' : 'bg-green-500 shadow-[0_0_10px_#22c55e]'}`} />
              {status === 'converting' ? 'Converting...' : 'Ready'}
            </div>
            <div className="flex items-center gap-2.5 px-4 py-2 bg-white/5 border border-white/5 rounded-full text-xs font-medium">
              <Zap size={14} className="text-[#3b82f6]" /> LangGraph: {status === 'converting' ? 'Processing' : status === 'done' ? 'Done ✓' : 'Idle'}
            </div>
          </div>
          <div className="flex items-center gap-5 text-xs text-gray-500">
            <span>v3.0.0</span>
            <span>|</span>
            <span>3D Engine: Active</span>
            <span>|</span>
            <span className="text-gray-300">60 FPS</span>
          </div>
        </footer>
      </div>
    </>
  );
}
