"use client";
import Editor from "@monaco-editor/react";

interface SqlEditorProps {
  value: string;
  onChange: (value: string | undefined) => void;
}

export default function SqlEditor({ value, onChange }: SqlEditorProps) {
  return (
    <div className="h-full w-full rounded-md overflow-hidden border border-gray-800">
      <Editor
        height="100%"
        defaultLanguage="sql"
        theme="vs-dark"
        value={value}
        onChange={onChange}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          padding: { top: 16 },
        }}
      />
    </div>
  );
}
