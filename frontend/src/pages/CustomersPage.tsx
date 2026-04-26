import { useQuery } from "@tanstack/react-query";
import { SearchIcon } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { fetchCustomers } from "@/api/customers";
import type { CustomerSort } from "@/api/types";
import { CustomerDetailDrawer } from "@/components/customers/CustomerDetailDrawer";
import { CustomersTable } from "@/components/customers/CustomersTable";
import { GlobalFilters } from "@/components/filters/GlobalFilters";
import { Input } from "@/components/ui/input";
import { useMetricsFilters } from "@/hooks/useMetricsFilters";

const PAGE_SIZE = 20;

export function CustomersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { filters } = useMetricsFilters();

  const customerParam = searchParams.get("customer");
  const customerId = customerParam ? Number(customerParam) : null;

  const skip = Number(searchParams.get("skip") ?? 0);
  const sort = (searchParams.get("sort") as CustomerSort | null) ?? "meeting_date_desc";
  const search = searchParams.get("q") ?? "";

  const [searchInput, setSearchInput] = useState(search);

  useEffect(() => {
    const handle = setTimeout(() => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (searchInput) next.set("q", searchInput);
        else next.delete("q");
        next.delete("skip");
        return next;
      });
    }, 300);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  const queryParams = useMemo(
    () => ({
      ...filters,
      skip,
      limit: PAGE_SIZE,
      sort,
      search: search || undefined,
    }),
    [filters, skip, sort, search],
  );

  const { data, isLoading } = useQuery({
    queryKey: ["customers", queryParams],
    queryFn: () => fetchCustomers(queryParams),
  });

  function setSort(next: CustomerSort) {
    setSearchParams((prev) => {
      const p = new URLSearchParams(prev);
      p.set("sort", next);
      p.delete("skip");
      return p;
    });
  }

  function setSkip(next: number) {
    setSearchParams((prev) => {
      const p = new URLSearchParams(prev);
      if (next > 0) p.set("skip", String(next));
      else p.delete("skip");
      return p;
    });
  }

  function openCustomer(id: number) {
    setSearchParams((prev) => {
      const p = new URLSearchParams(prev);
      p.set("customer", String(id));
      return p;
    });
  }

  function closeDrawer(open: boolean) {
    if (!open) {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        p.delete("customer");
        return p;
      });
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-heading text-3xl font-semibold tracking-tight">Clientes</h1>
        <p className="text-muted-foreground">
          Listado de reuniones con sus categorizaciones.
        </p>
      </header>

      <GlobalFilters />

      <div className="relative max-w-sm">
        <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Buscar por nombre…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="pl-9"
        />
      </div>

      <CustomersTable
        data={data?.items}
        total={data?.total ?? 0}
        skip={skip}
        isLoading={isLoading}
        sort={sort}
        onSortChange={setSort}
        onPageChange={setSkip}
        onRowClick={openCustomer}
      />

      <CustomerDetailDrawer customerId={customerId} onOpenChange={closeDrawer} />
    </div>
  );
}
