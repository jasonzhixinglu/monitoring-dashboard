interface Props {
  lines: string[];
  outerClassName?: string;
  preClassName?: string;
}

export function SnapshotBox({
  lines,
  outerClassName = "h-full bg-gray-950 rounded-lg p-4 overflow-auto",
  preClassName = "text-xs text-green-300 font-mono leading-5 whitespace-pre",
}: Props) {
  return (
    <div className={outerClassName}>
      <pre className={preClassName}>{lines.join("\n")}</pre>
    </div>
  );
}
