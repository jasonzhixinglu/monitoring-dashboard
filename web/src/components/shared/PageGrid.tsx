import type { ReactNode } from "react";

interface Props {
  topLeft: ReactNode;
  topRight: ReactNode;
  bottomLeft: ReactNode;
  bottomRight: ReactNode;
}

export function PageGrid({ topLeft, topRight, bottomLeft, bottomRight }: Props) {
  return (
    <div className="flex flex-col md:grid md:grid-cols-2 gap-4">
      <div>{topLeft}</div>
      <div>{topRight}</div>
      <div>{bottomLeft}</div>
      <div>{bottomRight}</div>
    </div>
  );
}
