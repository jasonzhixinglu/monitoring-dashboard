const OPTIONS = [2, 5, 10, 15, 20] as const;

interface Props {
  value: number;
  onChange: (y: number) => void;
}

export function YearWindowSelector({ value, onChange }: Props) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-gray-400 uppercase tracking-wider">Year window</label>
      <select
        className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      >
        {OPTIONS.map((y) => (
          <option key={y} value={y}>{y} years</option>
        ))}
      </select>
    </div>
  );
}
