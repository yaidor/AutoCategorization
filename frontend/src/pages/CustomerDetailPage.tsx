import { useParams } from "react-router-dom";

export function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-semibold">Cliente {id}</h1>
    </main>
  );
}
