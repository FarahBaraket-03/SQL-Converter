import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import ExportButton from "./ExportButton";
import { motion, AnimatePresence } from "motion/react";
import { Code2, Eye, BrainCircuit, AlertTriangle, Zap, CheckCircle2, UploadCloud, Leaf, Hexagon, Network, BarChart3, Bot, Maximize2, Minimize2 } from "lucide-react";
import MongoDBVisualizer from "./MongoDBVisualizer";
import Neo4jVisualizer from "./Neo4jVisualizer";
import CassandraVisualizer from "./CassandraVisualizer";

interface ConversionPanelProps {
  data: any;
  status: string;
}

const DB_TABS = [
  { id: "mongodb", label: "MongoDB", color: "text-[#00ed64] border-[#00ed64]", bg: "bg-[#00ed64]/10", shadow: "shadow-[0_4px_25px_rgba(0,237,100,0.4)]", icon: Leaf },
  { id: "cassandra", label: "Cassandra", color: "text-[#f59e0b] border-[#f59e0b]", bg: "bg-[#f59e0b]/10", shadow: "shadow-[0_4px_25px_rgba(245,158,11,0.4)]", icon: Hexagon },
  { id: "neo4j", label: "Neo4j", color: "text-[#a855f7] border-[#a855f7]", bg: "bg-[#a855f7]/10", shadow: "shadow-[0_4px_25px_rgba(168,85,247,0.4)]", icon: Network },
];

const SUB_VIEWS = [
  { id: "schema", label: "Schema", icon: Code2 },
  { id: "visualize", label: "3D View", icon: Eye },
  { id: "explain", label: "AI Explain", icon: BrainCircuit },
];

function parseExplanationSections(explanation: string): Array<{ title: string; paragraphs: string[]; bullets: string[] }> {
  const lines = explanation.split("\n");
  const sections: Array<{ title: string; paragraphs: string[]; bullets: string[] }> = [];
  let current = { title: "Overview", paragraphs: [] as string[], bullets: [] as string[] };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    if (trimmed.startsWith("## ")) {
      if (current.paragraphs.length > 0 || current.bullets.length > 0) {
        sections.push(current);
      }
      current = { title: trimmed.replace("## ", "").trim(), paragraphs: [], bullets: [] };
      continue;
    }

    if (trimmed.startsWith("- ")) {
      current.bullets.push(trimmed.replace("- ", "").trim());
      continue;
    }

    current.paragraphs.push(trimmed);
  }

  if (current.paragraphs.length > 0 || current.bullets.length > 0) {
    sections.push(current);
  }

  return sections.length > 0
    ? sections
    : [{ title: "Overview", paragraphs: ["No explanation available."], bullets: [] }];
}

export default function ConversionPanel({ data, status }: ConversionPanelProps) {
  const [activeDbTab, setActiveDbTab] = useState<string>("mongodb");
  const [activeSubView, setActiveSubView] = useState<string>("schema");
  const [isVisualizerFullscreen, setIsVisualizerFullscreen] = useState<boolean>(false);

  useEffect(() => {
    if (!isVisualizerFullscreen) {
      return;
    }

    const onEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsVisualizerFullscreen(false);
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onEscape);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onEscape);
    };
  }, [isVisualizerFullscreen]);

  useEffect(() => {
    if (activeSubView !== "visualize" && isVisualizerFullscreen) {
      setIsVisualizerFullscreen(false);
    }
  }, [activeSubView, isVisualizerFullscreen]);

  if (status !== 'done' || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 relative overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-20" />
        
        <div className="text-center z-10">
          <div className="w-24 h-24 mx-auto mb-6 bg-[#1a1a28]/80 border-2 border-white/10 rounded-2xl flex items-center justify-center text-gray-400 shadow-[0_0_40px_rgba(102,126,234,0.2)]">
            <UploadCloud size={40} />
          </div>
          <h2 className="text-2xl font-bold font-orbitron text-white mb-2">Output Panel</h2>
          <p className="text-gray-400">Awaiting conversion...</p>
        </div>
      </div>
    );
  }

  const currentData = data[activeDbTab];
  const explanationSections = parseExplanationSections(currentData?.explanation || "");

  const renderVisualizer = () => {
    if (activeDbTab === "mongodb") {
      return (
        <MongoDBVisualizer
          schema={currentData?.schema}
          visualization={currentData?.visualization}
          sampleData={currentData?.sample_data}
        />
      );
    }

    if (activeDbTab === "cassandra") {
      return <CassandraVisualizer schema={currentData?.schema} visualization={currentData?.visualization} />;
    }

    return <Neo4jVisualizer schema={currentData?.schema} visualization={currentData?.visualization} />;
  };

  const renderVisualizerFrame = (fullscreen: boolean) => (
    <div className={`${fullscreen ? "w-full h-full" : "w-full h-112.5"} bg-[#05050a]/50 rounded-2xl border border-white/10 relative overflow-hidden`}>
      <button
        onClick={() => setIsVisualizerFullscreen((prev) => !prev)}
        className="absolute top-3 right-3 z-20 px-3 py-2 text-xs font-semibold rounded-lg border border-white/20 bg-[#12121c]/90 text-white hover:bg-white/10 transition-all flex items-center gap-2"
        aria-label={fullscreen ? "Exit fullscreen visualization" : "Open fullscreen visualization"}
      >
        {fullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
        {fullscreen ? "Exit Full Screen" : "Full Screen"}
      </button>

      {fullscreen && (
        <div className="absolute top-14 right-3 z-20 text-[11px] text-gray-300 bg-[#12121c]/85 border border-white/10 rounded-md px-2.5 py-1.5">
          Press ESC to exit
        </div>
      )}

      {renderVisualizer()}
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      {/* DB Tabs */}
      <div className="flex gap-2 p-4 border-b border-white/5 bg-[#1a1a28]/40">
        <div className="flex items-center gap-3 font-semibold text-sm mr-4 text-white">
          <div className="w-9 h-9 rounded-xl accent-gradient flex items-center justify-center text-white"><UploadCloud size={20} /></div>
          Output
        </div>
        {DB_TABS.map((tab) => {
          const Icon = tab.icon;
          const isAvailable = Boolean(data[tab.id]);
          return (
            <button
              key={tab.id}
              onClick={() => isAvailable && setActiveDbTab(tab.id)}
              disabled={!isAvailable}
              className={`px-4 py-2.5 text-[13px] font-semibold border-2 rounded-xl transition-all flex items-center gap-2 ${
                activeDbTab === tab.id
                  ? `${tab.color} ${tab.bg} ${tab.shadow}`
                  : isAvailable
                  ? "border-transparent bg-white/5 text-gray-400 hover:text-gray-200 hover:bg-white/10"
                  : "border-transparent bg-white/5 text-gray-600 cursor-not-allowed"
              }`}
            >
              <Icon size={16} className={activeDbTab === tab.id ? "" : isAvailable ? "text-gray-500" : "text-gray-700"} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Sub Views */}
      <div className="flex gap-1 px-6 py-3.5 border-b border-white/5 bg-[#1a1a28]/30">
        {SUB_VIEWS.map((view) => {
          const Icon = view.icon;
          return (
            <button
              key={view.id}
              onClick={() => setActiveSubView(view.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-[13px] font-medium rounded-lg transition-all ${
                activeSubView === view.id ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <Icon size={16} />
              {view.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6 relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={`${activeDbTab}-${activeSubView}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            {/* SCHEMA VIEW */}
            {activeSubView === 'schema' && (
              <div className="h-full flex flex-col bg-[#05050a]/50 rounded-2xl border border-white/10 overflow-hidden">
                <div className="flex justify-between items-center px-5 py-3.5 border-b border-white/5 bg-[#1a1a28]/40">
                  <div className="flex items-center gap-2.5 text-[13px] font-semibold text-white">
                    {activeDbTab === 'mongodb' ? <Leaf size={16} className="text-[#00ed64]" /> : activeDbTab === 'cassandra' ? <Hexagon size={16} className="text-[#f59e0b]" /> : <Network size={16} className="text-[#a855f7]" />}
                    <span>{activeDbTab === 'mongodb' ? 'MongoDB Schema' : activeDbTab === 'cassandra' ? 'Cassandra CQL' : 'Neo4j Cypher'}</span>
                    <span className="px-3 py-1 bg-green-500/15 border border-green-500/30 rounded-full text-green-500 text-[11px] flex items-center gap-1"><CheckCircle2 size={12} /> {currentData?.score}%</span>
                  </div>
                  <ExportButton content={currentData?.schema || ''} filename={`schema-${activeDbTab}.txt`} />
                </div>
                <div className="p-5 overflow-auto flex-1">
                  <pre className="text-[13px] font-mono leading-[1.7] text-blue-300">
                    <code>{currentData?.schema}</code>
                  </pre>
                </div>
              </div>
            )}

            {/* VISUALIZE VIEW */}
            {activeSubView === 'visualize' && (
              <>
                {!isVisualizerFullscreen && renderVisualizerFrame(false)}
                {isVisualizerFullscreen && typeof document !== "undefined" && createPortal(
                  <div className="fixed inset-0 bg-[#05050a]/90 p-4" style={{ zIndex: 9999 }}>
                    {renderVisualizerFrame(true)}
                  </div>,
                  document.body
                )}
              </>
            )}

            {/* AI EXPLAIN VIEW */}
            {activeSubView === 'explain' && (
              <div className="flex flex-col gap-5">
                {/* AI Explanation */}
                <div className="bg-[#12121c]/60 border border-white/10 rounded-2xl p-6">
                  <div className="flex items-center gap-3 text-[15px] font-semibold text-white mb-4 pb-3 border-b border-white/5">
                    <Bot size={18} className="text-[#3b82f6]" /> 
                    <span>LangGraph AI Analysis</span>
                    <span className="ml-auto px-3 py-1 bg-[#3b82f6]/10 border border-[#3b82f6]/30 rounded-full text-[#3b82f6] text-[11px] font-medium">
                      Powered by Ollama
                    </span>
                  </div>
                  <div className="flex flex-col gap-4">
                    {explanationSections.map((section, i) => (
                      <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-4">
                        <h3 className="text-[14px] font-semibold text-white flex items-center gap-2 mb-3">
                          <Zap size={14} className="text-[#3b82f6]" />
                          {section.title}
                        </h3>
                        {section.paragraphs.map((paragraph, idx) => (
                          <p key={idx} className="text-[13px] text-gray-300 leading-[1.8] mb-2 last:mb-0">
                            {paragraph}
                          </p>
                        ))}
                        {section.bullets.length > 0 && (
                          <ul className="space-y-2 mt-2">
                            {section.bullets.map((item, idx) => (
                              <li key={idx} className="flex items-start gap-2 text-[13px] text-gray-200">
                                <CheckCircle2 size={14} className="text-[#00ed64] shrink-0 mt-1" />
                                <span>{item}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Warnings */}
                {currentData?.warnings && currentData.warnings.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-[13px] font-semibold text-[#f59e0b] mb-2">
                      <AlertTriangle size={16} />
                      <span>Considerations & Warnings</span>
                    </div>
                    {currentData.warnings.map((warning: string, i: number) => (
                      <div key={i} className="bg-[#f59e0b]/10 border border-[#f59e0b]/25 rounded-xl p-4 flex items-start gap-3">
                        <div className="w-6 h-6 rounded-full bg-[#f59e0b]/20 flex items-center justify-center shrink-0 mt-0.5">
                          <span className="text-[#f59e0b] text-[11px] font-bold">{i + 1}</span>
                        </div>
                        <p className="text-[13px] text-[#f59e0b] leading-[1.7]">{warning}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Performance Stats */}
                <div className="bg-[#12121c]/60 border border-white/10 rounded-2xl p-6">
                  <div className="flex items-center gap-3 text-[15px] font-semibold text-white mb-5 pb-3 border-b border-white/5">
                    <BarChart3 size={18} className="text-[#3b82f6]" /> 
                    <span>Performance Metrics</span>
                  </div>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="bg-gradient-to-br from-white/5 to-white/0 rounded-xl p-5 text-center border border-white/5 hover:border-white/10 transition-all hover:scale-105">
                      <div className={`text-3xl font-bold font-orbitron mb-2 ${activeDbTab === 'mongodb' ? 'text-[#00ed64]' : activeDbTab === 'cassandra' ? 'text-[#f59e0b]' : 'text-[#a855f7]'}`}>
                        {currentData?.stats.reads}
                      </div>
                      <div className="text-[11px] text-gray-500 uppercase tracking-widest font-medium">Read Performance</div>
                    </div>
                    <div className="bg-gradient-to-br from-white/5 to-white/0 rounded-xl p-5 text-center border border-white/5 hover:border-white/10 transition-all hover:scale-105">
                      <div className={`text-3xl font-bold font-orbitron mb-2 ${activeDbTab === 'mongodb' ? 'text-[#00ed64]' : activeDbTab === 'cassandra' ? 'text-[#f59e0b]' : 'text-[#a855f7]'}`}>
                        {currentData?.stats.writes}
                      </div>
                      <div className="text-[11px] text-gray-500 uppercase tracking-widest font-medium">Write Performance</div>
                    </div>
                    <div className="bg-gradient-to-br from-white/5 to-white/0 rounded-xl p-5 text-center border border-white/5 hover:border-white/10 transition-all hover:scale-105">
                      <div className={`text-xl font-bold font-orbitron mb-2 mt-2 ${activeDbTab === 'mongodb' ? 'text-[#00ed64]' : activeDbTab === 'cassandra' ? 'text-[#f59e0b]' : 'text-[#a855f7]'}`}>
                        {currentData?.stats.complexity}
                      </div>
                      <div className="text-[11px] text-gray-500 uppercase tracking-widest font-medium">Complexity</div>
                    </div>
                    <div className="bg-gradient-to-br from-white/5 to-white/0 rounded-xl p-5 text-center border border-white/5 hover:border-white/10 transition-all hover:scale-105">
                      <div className={`text-3xl font-bold font-orbitron mb-2 ${activeDbTab === 'mongodb' ? 'text-[#00ed64]' : activeDbTab === 'cassandra' ? 'text-[#f59e0b]' : 'text-[#a855f7]'}`}>
                        {currentData?.score}
                      </div>
                      <div className="text-[11px] text-gray-500 uppercase tracking-widest font-medium">Quality Score</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}