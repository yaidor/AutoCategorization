import { Navigate, useParams } from "react-router-dom";

export function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  return <Navigate to={`/customers?customer=${id}`} replace />;
}
