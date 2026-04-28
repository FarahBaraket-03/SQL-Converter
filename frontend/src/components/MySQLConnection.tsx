import { useState } from "react";
import { Database, Loader2, CheckCircle2, AlertCircle, Eye, EyeOff } from "lucide-react";
import { apiService } from "../services/api";

interface MySQLConnectionProps {
  onSchemaExtracted: (sql: string, tables: string[]) => void;
}

export default function MySQLConnection({ onSchemaExtracted }: MySQLConnectionProps) {
  const [host, setHost] = useState("localhost");
  const [port, setPort] = useState("3306");
  const [user, setUser] = useState("root");
  const [password, setPassword] = useState("");
  const [database, setDatabase] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleConnect = async () => {
    if (!host || !user || !database) {
      setError("Please fill in all required fields");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await apiService.extractMySQLSchema({
        host: host,
        port: parseInt(port),
        user,
        password,
        database
      });

      setSuccess(true);
      onSchemaExtracted(response.sql, response.tables);
      
      // Clear password for security
      setPassword("");
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to connect to MySQL");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="w-full max-w-md bg-[#1a1a28]/60 border border-white/10 rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.5)] backdrop-blur-md">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#00758f] to-[#f29111] flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(242,145,17,0.3)]">
          <Database size={28} className="text-white" />
        </div>
        
        <h3 className="text-xl font-bold text-white mb-2">Connect to MySQL</h3>
        <p className="text-sm text-gray-400 mb-6">
          Connect directly to your database to extract the schema automatically.
        </p>

        <div className="space-y-4">
          {/* Host */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 ml-1">
              Host <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              placeholder="localhost"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              className="w-full bg-[#05050a] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-[#00758f] transition-colors"
            />
          </div>

          {/* Port */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 ml-1">
              Port
            </label>
            <input
              type="text"
              placeholder="3306"
              value={port}
              onChange={(e) => setPort(e.target.value)}
              className="w-full bg-[#05050a] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-[#00758f] transition-colors"
            />
          </div>

          {/* Username */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 ml-1">
              Username <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              placeholder="root"
              value={user}
              onChange={(e) => setUser(e.target.value)}
              className="w-full bg-[#05050a] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-[#00758f] transition-colors"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 ml-1">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#05050a] border border-white/10 rounded-xl px-4 py-3 pr-10 text-sm text-white focus:outline-none focus:border-[#00758f] transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Database Name */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 ml-1">
              Database Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              placeholder="my_database"
              value={database}
              onChange={(e) => setDatabase(e.target.value)}
              className="w-full bg-[#05050a] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-[#00758f] transition-colors"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-xl">
              <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="flex items-start gap-2 p-3 bg-green-500/10 border border-green-500/30 rounded-xl">
              <CheckCircle2 size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-green-400">Schema extracted successfully!</p>
            </div>
          )}

          {/* Connect Button */}
          <button
            onClick={handleConnect}
            disabled={loading || !host || !user || !database}
            className="w-full mt-2 py-3.5 bg-gradient-to-r from-[#00758f] to-[#f29111] rounded-xl text-white text-sm font-bold shadow-[0_4px_20px_rgba(242,145,17,0.3)] hover:-translate-y-0.5 transition-transform flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Connecting...
              </>
            ) : (
              <>
                <Database size={16} />
                Connect & Extract Schema
              </>
            )}
          </button>
        </div>

        {/* Security Note */}
        <div className="mt-6 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl">
          <p className="text-xs text-blue-300">
            <strong>Security Note:</strong> Credentials are sent directly to the backend and are not stored. 
            Use read-only accounts when possible.
          </p>
        </div>
      </div>
    </div>
  );
}
