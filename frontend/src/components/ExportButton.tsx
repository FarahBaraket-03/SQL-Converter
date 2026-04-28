"use client";
import { Download, Copy, Check } from "lucide-react";
import { useState } from "react";

interface ExportButtonProps {
  content: string;
  filename: string;
}

export default function ExportButton({ content, filename }: ExportButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={handleCopy}
        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-md transition-colors"
      >
        {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
        Copy
      </button>
      <button
        onClick={handleDownload}
        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-md transition-colors"
      >
        <Download size={16} />
        Download
      </button>
    </div>
  );
}
