import { useState, useEffect } from "react";
import { History, Trash2, Clock, Database, FileText, Download } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface ConversionHistory {
  id: string;
  timestamp: Date;
  sql: string;
  inputMethod: string;
  databases: string[];
  preview: string;
}

interface HistoryPanelProps {
  onLoadHistory: (sql: string) => void;
}

export default function HistoryPanel({ onLoadHistory }: HistoryPanelProps) {
  const [history, setHistory] = useState<ConversionHistory[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    // Load history from localStorage
    const savedHistory = localStorage.getItem('conversion_history');
    if (savedHistory) {
      const parsed = JSON.parse(savedHistory);
      setHistory(parsed.map((item: any) => ({
        ...item,
        timestamp: new Date(item.timestamp)
      })));
    }
  }, []);

  const saveToHistory = (sql: string, inputMethod: string, databases: string[]) => {
    const newEntry: ConversionHistory = {
      id: Date.now().toString(),
      timestamp: new Date(),
      sql,
      inputMethod,
      databases,
      preview: sql.substring(0, 100) + (sql.length > 100 ? '...' : '')
    };

    const updatedHistory = [newEntry, ...history].slice(0, 50); // Keep last 50
    setHistory(updatedHistory);
    localStorage.setItem('conversion_history', JSON.stringify(updatedHistory));
  };

  const deleteEntry = (id: string) => {
    const updatedHistory = history.filter(item => item.id !== id);
    setHistory(updatedHistory);
    localStorage.setItem('conversion_history', JSON.stringify(updatedHistory));
  };

  const clearAll = () => {
    if (confirm('Clear all history?')) {
      setHistory([]);
      localStorage.removeItem('conversion_history');
    }
  };

  const exportHistory = () => {
    const dataStr = JSON.stringify(history, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `conversion-history-${Date.now()}.json`;
    link.click();
  };

  return (
    <div className="flex flex-col h-full bg-[#0a0a12]/90 backdrop-blur-xl">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <History size={20} className="text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-white">Conversion History</h2>
            <p className="text-xs text-gray-400">{history.length} conversions</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={exportHistory}
            disabled={history.length === 0}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
            title="Export history"
          >
            <Download size={16} />
          </button>
          <button
            onClick={clearAll}
            disabled={history.length === 0}
            className="p-2 rounded-lg bg-white/5 hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors disabled:opacity-50"
            title="Clear all"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <History size={48} className="mb-4 opacity-20" />
            <p className="text-sm">No conversion history yet</p>
            <p className="text-xs mt-2">Your conversions will appear here</p>
          </div>
        ) : (
          <AnimatePresence>
            {history.map((item) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  selectedId === item.id
                    ? 'bg-purple-500/10 border-purple-500/30'
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
                onClick={() => setSelectedId(item.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Clock size={12} />
                    <span>{item.timestamp.toLocaleString()}</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteEntry(item.id);
                    }}
                    className="p-1 rounded hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>

                <div className="flex items-center gap-2 mb-2">
                  {item.inputMethod === 'mysql' ? (
                    <Database size={14} className="text-orange-400" />
                  ) : (
                    <FileText size={14} className="text-blue-400" />
                  )}
                  <span className="text-xs font-medium text-gray-300 capitalize">
                    {item.inputMethod}
                  </span>
                </div>

                <p className="text-sm text-gray-300 font-mono mb-3 line-clamp-2">
                  {item.preview}
                </p>

                <div className="flex items-center gap-2">
                  {item.databases.map((db) => (
                    <span
                      key={db}
                      className="px-2 py-1 rounded text-xs bg-white/5 border border-white/10 text-gray-400"
                    >
                      {db}
                    </span>
                  ))}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onLoadHistory(item.sql);
                  }}
                  className="mt-3 w-full py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-sm font-medium transition-colors"
                >
                  Load SQL
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

// Export the saveToHistory function for use in App.tsx
export { type ConversionHistory };
