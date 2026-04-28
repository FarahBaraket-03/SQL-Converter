import { useCallback, useEffect, useMemo } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

interface CassandraVisualizerProps {
  schema?: string;
  visualization?: any;
}

interface CassandraTable {
  name: string;
  columns?: { name: string; type: string }[];
  partition_keys: string[];
  clustering_keys: string[];
  is_query_table?: boolean;
  query_pattern?: string;
}

function parseTablesFromSchema(schema: string): CassandraTable[] {
  const tables: CassandraTable[] = [];
  const tableRegex = /CREATE TABLE IF NOT EXISTS\s+([A-Za-z_][\w]*)\s*\((.*?)\)\s*(?:WITH CLUSTERING ORDER BY \((.*?)\))?\s*;/gs;

  let match: RegExpExecArray | null;
  while ((match = tableRegex.exec(schema)) !== null) {
    const name = match[1];
    const body = match[2];
    
    // Support both PRIMARY KEY ((pk1, pk2), ck1) and PRIMARY KEY (pk1, ck1)
    const pkMatch = body.match(/PRIMARY KEY\s*\(\((.*?)\)(?:,\s*(.*?))?\)/s) || body.match(/PRIMARY KEY\s*\((.*?)\)/s);

    const partitionKeys = pkMatch?.[1]
      ? pkMatch[1].split(",").map((key) => key.trim()).filter(Boolean)
      : [];
    const clusteringKeys = pkMatch?.[2]
      ? pkMatch[2].split(",").map((key) => key.trim()).filter(Boolean)
      : [];

    const columnDefinitions = body.split(/,(?![^\(]*\))/);
    const columns = [];
    for (const def of columnDefinitions) {
      const cleanDef = def.trim();
      if (cleanDef && !cleanDef.toUpperCase().startsWith('PRIMARY KEY')) {
        const parts = cleanDef.split(/\s+/);
        if (parts.length >= 2) {
          columns.push({ name: parts[0], type: parts.slice(1).join(' ') });
        }
      }
    }

    tables.push({
      name,
      columns,
      partition_keys: partitionKeys,
      clustering_keys: clusteringKeys,
      is_query_table: name.includes("_by_"),
    });
  }

  return tables;
}

function getTables(schema: string, visualization?: any): CassandraTable[] {
  if (Array.isArray(visualization?.tables) && visualization.tables.length > 0) {
    return visualization.tables.map((table: any) => ({
      name: String(table.name),
      columns: Array.isArray(table.columns) ? table.columns : [],
      partition_keys: Array.isArray(table.partition_keys) ? table.partition_keys.map(String) : [],
      clustering_keys: Array.isArray(table.clustering_keys) ? table.clustering_keys.map(String) : [],
      is_query_table: Boolean(table.is_query_table),
      query_pattern: table.query_pattern ? String(table.query_pattern) : undefined,
    }));
  }

  return parseTablesFromSchema(schema);
}

export default function CassandraVisualizer({ schema = "", visualization }: CassandraVisualizerProps) {
  const graph = useMemo(() => {
    const tables = getTables(schema, visualization);
    const nodes: any[] = [];
    const edges: any[] = [];

    tables.forEach((table, index) => {
      const x = 100 + (index % 3) * 350;
      const y = 70 + Math.floor(index / 3) * 250;
      const partition = table.partition_keys.length > 0 ? table.partition_keys.join(", ") : "none";
      const clustering = table.clustering_keys.length > 0 ? table.clustering_keys.join(", ") : "none";

      nodes.push({
        id: table.name,
        position: { x, y },
        data: {
          label: (
            <div className="flex flex-col h-full">
              <div className="font-bold text-sm border-b border-current pb-2 mb-2 uppercase tracking-wider bg-black/20 -mx-3 -mt-2.5 px-3 py-2 rounded-t-[10px]">
                {table.name}
              </div>
              <div className="flex flex-col gap-1 text-left mt-1">
                {table.columns && table.columns.length > 0 && (
                  <div className="flex flex-col gap-1 mb-2 border-b border-current/20 pb-2">
                    {table.columns.map((col, i) => {
                      const isPk = table.partition_keys.includes(col.name);
                      const isCk = table.clustering_keys.includes(col.name);
                      return (
                        <div key={i} className="flex justify-between gap-4">
                          <span className="font-semibold flex items-center gap-1.5">
                            {col.name}
                            {(isPk || isCk) && (
                              <span className={`text-[8px] px-1 rounded ${isPk ? 'bg-amber-500/20 text-amber-300' : 'bg-blue-500/20 text-blue-300'}`}>
                                {isPk ? 'PK' : 'CK'}
                              </span>
                            )}
                          </span>
                          <span className="opacity-60 text-right">{col.type}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
                <div className="flex justify-between gap-4 pt-1">
                  <span className="opacity-60">Partition:</span>
                  <span className="font-semibold text-right">{partition}</span>
                </div>
                <div className="flex justify-between gap-4">
                  <span className="opacity-60">Clustering:</span>
                  <span className="font-semibold text-right">{clustering}</span>
                </div>
              </div>
            </div>
          ),
        },
        style: {
          background: table.is_query_table ? "rgba(245,158,11,0.18)" : "rgba(59,130,246,0.16)",
          color: table.is_query_table ? "#fde68a" : "#bfdbfe",
          border: table.is_query_table ? "1px solid #f59e0b" : "1px solid #3b82f6",
          borderColor: table.is_query_table ? "#f59e0b" : "#3b82f6",
          borderRadius: "12px",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: "11px",
          lineHeight: "1.45",
          padding: "10px 12px",
          minWidth: "260px",
          boxShadow: table.is_query_table
            ? "0 4px 20px rgba(245,158,11,0.15)"
            : "0 4px 20px rgba(59,130,246,0.15)",
        },
      });
    });

    return { nodes, edges: [] };
  }, [schema, visualization]);

  const [nodes, setNodes, onNodesChange] = useNodesState(graph.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(graph.edges);

  useEffect(() => {
    setNodes(graph.nodes);
    setEdges(graph.edges);
  }, [graph, setEdges, setNodes]);

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  return (
    <div className="w-full h-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        fitViewOptions={{ padding: 0.25, maxZoom: 1.2 }}
        nodesDraggable
        panOnDrag
        panOnScroll
        zoomOnScroll
        zoomOnPinch
        selectionOnDrag
        className="bg-transparent"
        minZoom={0.2}
        maxZoom={4}
      >
        <Background color="#f59e0b" variant={BackgroundVariant.Dots} gap={24} size={1} className="opacity-10" />
        <MiniMap
          pannable
          zoomable
          nodeStrokeWidth={2}
          nodeColor={(node) => String(node.style?.borderColor || "#3b82f6")}
          className="bg-[#1a1a28]/95! border! border-white/10!"
          maskColor="rgba(5, 5, 10, 0.6)"
        />
        <Controls className="bg-[#1a1a28] border-white/10 fill-white [&>button]:border-white/10 [&>button]:bg-[#1a1a28] [&>button:hover]:bg-white/10" />
      </ReactFlow>

      <div className="absolute bottom-4 left-4 text-xs text-gray-300 flex items-center gap-2 bg-[#1a1a28]/90 px-4 py-2 rounded-xl border border-white/10 backdrop-blur-md z-10">
        <div className="w-2 h-2 rounded-full bg-cassandra animate-pulse shadow-[0_0_10px_#f59e0b]" />
        Cassandra key and query-table flow
      </div>
    </div>
  );
}
