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
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

interface Neo4jVisualizerProps {
  schema?: string;
  visualization?: any;
}

interface GraphNode {
  label: string;
  properties: string[];
}

interface GraphRelationship {
  from_label: string;
  to_label: string;
  type: string;
}

interface NodeTheme {
  start: string;
  end: string;
  border: string;
  shadow: string;
  edge: string;
}

const NODE_THEMES: NodeTheme[] = [
  { start: "rgba(56,189,248,0.5)", end: "rgba(12,74,110,0.86)", border: "#38bdf8", shadow: "rgba(56,189,248,0.35)", edge: "#38bdf8" },
  { start: "rgba(52,211,153,0.48)", end: "rgba(6,78,59,0.86)", border: "#34d399", shadow: "rgba(52,211,153,0.34)", edge: "#34d399" },
  { start: "rgba(251,191,36,0.5)", end: "rgba(120,53,15,0.86)", border: "#fbbf24", shadow: "rgba(251,191,36,0.34)", edge: "#fbbf24" },
  { start: "rgba(244,114,182,0.5)", end: "rgba(131,24,67,0.86)", border: "#f472b6", shadow: "rgba(244,114,182,0.34)", edge: "#f472b6" },
  { start: "rgba(196,181,253,0.55)", end: "rgba(76,29,149,0.86)", border: "#c4b5fd", shadow: "rgba(196,181,253,0.34)", edge: "#c4b5fd" },
  { start: "rgba(253,186,116,0.52)", end: "rgba(124,45,18,0.86)", border: "#fdba74", shadow: "rgba(253,186,116,0.34)", edge: "#fdba74" },
];

function hashLabel(label: string): number {
  let hash = 0;
  for (let i = 0; i < label.length; i += 1) {
    hash = (hash << 5) - hash + label.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function getThemeForLabel(label: string): NodeTheme {
  return NODE_THEMES[hashLabel(label) % NODE_THEMES.length];
}

function parseNodesFromSchema(schema: string): GraphNode[] {
  const nodes: GraphNode[] = [];
  const nodeRegex = /CREATE \(n:([A-Za-z_][\w]*) \{([^}]*)\}\)/g;
  let match: RegExpExecArray | null;

  while ((match = nodeRegex.exec(schema)) !== null) {
    const label = match[1];
    const props = match[2]
      .split(",")
      .map((part) => part.split(":")[0].trim())
      .filter(Boolean);

    if (!nodes.some((node) => node.label === label)) {
      nodes.push({ label, properties: props });
    }
  }

  return nodes;
}

function parseRelationshipsFromSchema(schema: string): GraphRelationship[] {
  const relationships: GraphRelationship[] = [];
  const relRegex = /MATCH \(a:([A-Za-z_][\w]*)\), \(b:([A-Za-z_][\w]*)\)[\s\S]*?CREATE \(a\)-\[r:([A-Z_][A-Z0-9_]*)\]->\(b\)/g;
  let match: RegExpExecArray | null;

  while ((match = relRegex.exec(schema)) !== null) {
    relationships.push({
      from_label: match[1],
      to_label: match[2],
      type: match[3],
    });
  }

  return relationships;
}

function getGraph(schema: string, visualization?: any): { nodes: GraphNode[]; relationships: GraphRelationship[] } {
  if (Array.isArray(visualization?.nodes) && Array.isArray(visualization?.relationships)) {
    return {
      nodes: visualization.nodes.map((node: any) => ({
        label: String(node.label),
        properties: Array.isArray(node.properties)
          ? node.properties.map((property: any) => String(property?.name || property))
          : [],
      })),
      relationships: visualization.relationships.map((relationship: any) => ({
        from_label: String(relationship.from_label),
        to_label: String(relationship.to_label),
        type: String(relationship.type),
      })),
    };
  }

  return {
    nodes: parseNodesFromSchema(schema),
    relationships: parseRelationshipsFromSchema(schema),
  };
}

export default function Neo4jVisualizer({ schema = "", visualization }: Neo4jVisualizerProps) {
  const graph = useMemo(() => {
    const { nodes: modelNodes, relationships } = getGraph(schema, visualization);
    const nodes: any[] = [];
    const edges: any[] = [];
    const labelThemeMap = new Map<string, NodeTheme>();

    const centerX = 360;
    const centerY = 220;
    const radius = Math.max(180, modelNodes.length * 45);

    modelNodes.forEach((node, index) => {
      const angle = (index / Math.max(modelNodes.length, 1)) * Math.PI * 2;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      const theme = getThemeForLabel(node.label);
      labelThemeMap.set(node.label, theme);

      nodes.push({
        id: node.label,
        position: { x, y },
        data: {
          label: (
            <div className="flex flex-col items-center justify-center h-full w-full">
              <div className="font-bold text-sm tracking-wider uppercase mb-1">
                {node.label}
              </div>
              {node.properties.length > 0 && (
                <div className="text-[9px] opacity-70 mt-1 max-w-30 truncate">
                  {node.properties.slice(0, 3).join(", ")}
                  {node.properties.length > 3 ? "..." : ""}
                </div>
              )}
            </div>
          ),
        },
        style: {
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: `radial-gradient(circle at 30% 30%, ${theme.start}, ${theme.end})`,
          color: "#ffffff",
          border: `2px solid ${theme.border}`,
          borderColor: theme.border,
          borderRadius: "50%",
          fontFamily: "JetBrains Mono, monospace",
          width: "120px",
          height: "120px",
          boxShadow: `0 8px 32px ${theme.shadow}, inset 0 2px 10px rgba(255,255,255,0.2)`,
        },
      });
    });

    relationships.forEach((relationship, index) => {
      if (!nodes.some((node) => node.id === relationship.from_label) || !nodes.some((node) => node.id === relationship.to_label)) {
        return;
      }

      const sourceTheme = labelThemeMap.get(relationship.from_label);
      const edgeColor = sourceTheme?.edge || "#a855f7";

      edges.push({
        id: `edge-${index}-${relationship.from_label}-${relationship.to_label}`,
        source: relationship.from_label,
        target: relationship.to_label,
        label: relationship.type,
        animated: true,
        style: { stroke: edgeColor, strokeWidth: 2.2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: edgeColor },
        labelStyle: {
          fill: edgeColor,
          fontSize: "10px",
          fontWeight: 700,
          textTransform: "uppercase",
        },
        labelBgStyle: { fill: "#1f1230", fillOpacity: 0.95, stroke: edgeColor, strokeWidth: 1 },
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
        <Background color="#a855f7" variant={BackgroundVariant.Dots} gap={24} size={1} className="opacity-10" />
        <MiniMap
          pannable
          zoomable
          nodeStrokeWidth={3}
          nodeColor={(node) => String(node.style?.borderColor || "#a855f7")}
          className="bg-[#1a1a28]/95! border! border-white/10!"
          maskColor="rgba(5, 5, 10, 0.6)"
        />
        <Controls className="bg-[#1a1a28] border-white/10 fill-white [&>button]:border-white/10 [&>button]:bg-[#1a1a28] [&>button:hover]:bg-white/10" />
      </ReactFlow>

      <div className="absolute bottom-4 left-4 text-xs text-gray-300 flex items-center gap-2 bg-[#1a1a28]/90 px-4 py-2 rounded-xl border border-white/10 backdrop-blur-md z-10">
        <div className="w-2 h-2 rounded-full bg-neo4j animate-pulse shadow-[0_0_10px_#a855f7]" />
        Neo4j nodes and relationship traversal flow
      </div>
    </div>
  );
}
