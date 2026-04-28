import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from "@xyflow/react";
import Editor from "@monaco-editor/react";
import { Database, FileJson } from "lucide-react";
import "@xyflow/react/dist/style.css";

interface MongoDBVisualizerProps {
  schema?: string;
  visualization?: any;
  sampleData?: string;
}

interface MongoCollection {
  name: string;
  fields: Array<{ name: string; type: string }>;
}

function parseCollectionsFromSchema(schema: string): MongoCollection[] {
  const collections: MongoCollection[] = [];
  const blocks = schema.split("// ");

  for (const block of blocks) {
    const header = block.match(/^([A-Za-z_][\w]*)\s+Collection/m);
    if (!header) {
      continue;
    }

    const name = header[1];
    const fields: Array<{ name: string; type: string }> = [];
    const fieldRegex = /\s([A-Za-z_][\w]*): \{ bsonType: '([^']+)' \}/g;
    let match: RegExpExecArray | null;

    while ((match = fieldRegex.exec(block)) !== null) {
      if (match[1] === "_id") {
        continue;
      }
      fields.push({ name: match[1], type: match[2] });
    }

    collections.push({ name, fields });
  }

  return collections;
}

function getCollections(schema: string, visualization?: any): MongoCollection[] {
  if (Array.isArray(visualization?.collections) && visualization.collections.length > 0) {
    return visualization.collections.map((collection: any) => ({
      name: String(collection.name),
      fields: Object.entries(collection.fields || {})
        .filter(([key]) => key !== "_id")
        .map(([key, value]) => ({
          name: String(key),
          type: String((value as any)?.bsonType || "string"),
        })),
    }));
  }

  return parseCollectionsFromSchema(schema);
}

function generateSampleDocument(schema: string): string {
  // Parse the schema to generate a realistic sample document
  const collections = parseCollectionsFromSchema(schema);
  
  if (collections.length === 0) {
    return `{
  "_id": ObjectId("653a1b2c9d8e7f6a5b4c3d2e"),
  "message": "No collections found in schema"
}`;
  }

  const collection = collections[0]; // Use first collection
  const doc: any = {
    "_id": `ObjectId("${Math.random().toString(36).substring(2, 15)}")`,
  };

  collection.fields.forEach((field, index) => {
    const { name, type } = field;
    
    switch (type.toLowerCase()) {
      case 'int':
      case 'long':
        doc[name] = Math.floor(Math.random() * 1000) + 1;
        break;
      case 'double':
      case 'decimal':
        doc[name] = (Math.random() * 1000).toFixed(2);
        break;
      case 'bool':
      case 'boolean':
        doc[name] = Math.random() > 0.5;
        break;
      case 'date':
        doc[name] = `ISODate("${new Date().toISOString()}")`;
        break;
      case 'array':
        doc[name] = ['item1', 'item2', 'item3'];
        break;
      case 'object':
        doc[name] = { key: 'value', nested: true };
        break;
      default:
        // String or unknown types
        if (name.toLowerCase().includes('email')) {
          doc[name] = 'user@example.com';
        } else if (name.toLowerCase().includes('name')) {
          doc[name] = 'John Doe';
        } else if (name.toLowerCase().includes('status')) {
          doc[name] = 'active';
        } else {
          doc[name] = `sample_${name}`;
        }
    }
  });

  return JSON.stringify(doc, null, 2)
    .replace(/"ObjectId\(([^)]+)\)"/g, 'ObjectId($1)')
    .replace(/"ISODate\(([^)]+)\)"/g, 'ISODate($1)');
}

export default function MongoDBVisualizer({ schema = "", visualization, sampleData }: MongoDBVisualizerProps) {
  const [viewMode, setViewMode] = useState<'graph' | 'json'>('json'); // Default to JSON view
  
  // Use sample data from backend if available, otherwise generate
  const sampleDoc = useMemo(() => {
    if (sampleData) {
      try {
        // Parse and re-format for better display
        const parsed = JSON.parse(sampleData);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return sampleData;
      }
    }
    return generateSampleDocument(schema);
  }, [sampleData, schema]);
  const graph = useMemo(() => {
    const collections = getCollections(schema, visualization);
    const nodes: any[] = [];
    const edges: any[] = [];

    collections.forEach((collection, index) => {
      const collectionId = `collection-${collection.name}`;
      const baseX = 120 + index * 330;
      const baseY = 80;

      nodes.push({
        id: collectionId,
        position: { x: baseX, y: baseY },
        data: { label: collection.name },
        style: {
          background: "rgba(0, 237, 100, 0.16)",
          color: "#d1fae5",
          border: "2px solid #00ed64",
          borderRadius: "12px",
          fontWeight: 700,
          padding: "10px 14px",
          boxShadow: "0 0 24px rgba(0,237,100,0.22)",
          minWidth: "170px",
          textAlign: "center",
          textTransform: "capitalize",
        },
      });

      collection.fields.slice(0, 8).forEach((field, fieldIndex) => {
        const fieldId = `${collection.name}-field-${field.name}`;
        const row = Math.floor(fieldIndex / 2);
        const col = fieldIndex % 2;
        const x = baseX - 80 + col * 170;
        const y = baseY + 140 + row * 88;

        nodes.push({
          id: fieldId,
          position: { x, y },
          data: { label: `${field.name}: ${field.type}` },
          style: {
            background: "rgba(8, 14, 24, 0.85)",
            color: "#a7f3d0",
            border: "1px solid rgba(0,237,100,0.45)",
            borderRadius: "10px",
            fontSize: "11px",
            padding: "8px 10px",
            minWidth: "150px",
            fontFamily: "JetBrains Mono, monospace",
          },
        });

        edges.push({
          id: `edge-${collectionId}-${fieldId}`,
          source: collectionId,
          target: fieldId,
          animated: true,
          style: { stroke: "#00ed64", strokeWidth: 1.8 },
          markerEnd: { type: MarkerType.ArrowClosed, color: "#00ed64" },
        });
      });
    });

    const strategy = visualization?.embedding_strategy || {};
    Object.entries(strategy).forEach(([key, relation], index) => {
      const [fromTable, toTable] = String(key).split("->");
      const sourceId = `collection-${fromTable}`;
      const targetId = `collection-${toTable}`;
      if (!nodes.some((node) => node.id === sourceId) || !nodes.some((node) => node.id === targetId)) {
        return;
      }

      const relationLabel = String(relation).toLowerCase() === "embed" ? "embeds" : "references";
      const color = relationLabel === "embeds" ? "#22c55e" : "#3b82f6";

      edges.push({
        id: `strategy-${index}-${sourceId}-${targetId}`,
        source: sourceId,
        target: targetId,
        label: relationLabel,
        animated: true,
        style: { stroke: color, strokeWidth: 2.2 },
        markerEnd: { type: MarkerType.ArrowClosed, color },
        labelStyle: {
          fill: color,
          fontSize: "10px",
          fontWeight: 700,
          textTransform: "uppercase",
        },
        labelBgStyle: { fill: "#0b1020", fillOpacity: 0.9, stroke: color, strokeWidth: 1 },
        labelBgPadding: [5, 2],
      });
    });

    return { nodes, edges };
  }, [schema, visualization]);

  const [nodes, setNodes, onNodesChange] = useNodesState(graph.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(graph.edges);

  useEffect(() => {
    setNodes(graph.nodes);
    setEdges(graph.edges);
  }, [graph, setEdges, setNodes]);

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  return (
    <div className="w-full h-full relative flex flex-col">
      {/* View Mode Tabs */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/5 bg-[#1a1a28]/40">
        <div className="flex items-center gap-2.5 text-[13px] font-semibold text-[#00ed64]">
          <Database size={16} /> MongoDB Document
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('json')}
            className={`flex items-center gap-2 px-3 py-1.5 text-[11px] font-medium rounded-lg transition-all ${
              viewMode === 'json' ? 'bg-[#00ed64]/20 text-[#00ed64] border border-[#00ed64]/30' : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
            }`}
          >
            <FileJson size={14} /> Sample JSON
          </button>
          <button
            onClick={() => setViewMode('graph')}
            className={`flex items-center gap-2 px-3 py-1.5 text-[11px] font-medium rounded-lg transition-all ${
              viewMode === 'graph' ? 'bg-[#00ed64]/20 text-[#00ed64] border border-[#00ed64]/30' : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
            }`}
          >
            <Database size={14} /> Schema Graph
          </button>
        </div>
      </div>

      {/* JSON View */}
      {viewMode === 'json' && (
        <div className="flex-1 bg-[#0d1117] relative">
          <Editor
            height="100%"
            defaultLanguage="javascript"
            theme="vs-dark"
            value={sampleDoc}
            options={{
              readOnly: true,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              fontSize: 13,
              fontFamily: '"JetBrains Mono", "Fira Code", monospace',
              padding: { top: 16, bottom: 16 },
              lineNumbersMinChars: 3,
              folding: true,
              renderLineHighlight: "none",
              scrollbar: {
                verticalScrollbarSize: 8,
                horizontalScrollbarSize: 8,
              }
            }}
          />
        </div>
      )}

      {/* Graph View */}
      {viewMode === 'graph' && (
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
            className="bg-transparent"
            minZoom={0.2}
            maxZoom={4}
          >
            <Background color="#00ed64" variant={BackgroundVariant.Dots} gap={24} size={1} className="opacity-10" />
            <Controls className="bg-[#1a1a28] border-white/10 fill-white [&>button]:border-white/10 [&>button]:bg-[#1a1a28] [&>button:hover]:bg-white/10" />
          </ReactFlow>

          <div className="absolute bottom-4 left-4 text-xs text-gray-300 flex items-center gap-2 bg-[#1a1a28]/90 px-4 py-2 rounded-xl border border-white/10 backdrop-blur-md z-10">
            <div className="w-2 h-2 rounded-full bg-[#00ed64] animate-pulse shadow-[0_0_10px_#00ed64]" />
            MongoDB collections and field hierarchy
          </div>
        </div>
      )}
    </div>
  );
}
