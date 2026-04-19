interface Props {
  tableText: string;
  csvContent: string;
  filename: string;
  description: string;
}

export function DataTable({ tableText, csvContent, filename, description }: Props) {
  function downloadCsv() {
    const blob = new Blob([csvContent], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{description}</span>
        <button
          onClick={downloadCsv}
          className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded"
        >
          Download CSV (full history)
        </button>
      </div>
      <pre className="text-xs font-mono text-gray-300 overflow-x-auto whitespace-pre leading-5">
        {tableText}
      </pre>
    </div>
  );
}
